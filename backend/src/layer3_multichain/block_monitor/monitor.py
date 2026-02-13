"""
Block Header Monitor for detecting blockchain reorganizations.

Continuously polls blockchain RPC endpoints to:
1. Cache block headers (hash, parent hash, number)
2. Detect fork points when hashes don't match
3. Emit reorg signals to ReorgHandler
4. Track reorg statistics per chain
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from datetime import datetime
from abc import ABC, abstractmethod
from collections import OrderedDict
import asyncio
import logging

from src.common.config import config
from src.layer1_core.finality.tracker import FinalityTracker
from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


@dataclass
class BlockHeader:
    """Blockchain block header information."""
    number: int
    hash: str
    parent_hash: str
    timestamp: int


class BlockMonitor(ABC):
    """
    Abstract block monitor for detecting chain reorganizations.

    Monitors blockchain by:
    - Polling RPC for new blocks
    - Caching recent block headers
    - Comparing cached vs current block hashes
    - Detecting mismatches (fork points)
    - Emitting reorg signals to handler
    """

    def __init__(self, chain: str, tracker: FinalityTracker):
        """
        Initialize block monitor.

        Args:
            chain: Chain name (ethereum, arbitrum, solana)
            tracker: FinalityTracker instance for RPC calls
        """
        self.chain = chain
        self.tracker = tracker
        self.chain_config = config.CHAINS[chain]

        # Block cache: height -> header (LRU cache)
        self.block_cache: OrderedDict[int, BlockHeader] = OrderedDict()
        self.max_cache_size = self.chain_config.max_reorg_depth

        # Monitoring state
        self.is_running = False
        self.last_poll_time: Optional[datetime] = None
        self.poll_count = 0

        # Reorg detection stats
        self.reorgs_detected = 0
        self.last_reorg_time: Optional[datetime] = None

        # Event store (for querying affected events)
        self._event_store: List[RiskEvent] = []

        logger.info(
            f"Initialized BlockMonitor for {chain} "
            f"(cache_size={self.max_cache_size}, poll_interval={self.poll_interval_sec()}s)"
        )

    @abstractmethod
    def poll_interval_sec(self) -> float:
        """How often to poll for new blocks (varies by chain)."""
        pass

    async def start_monitoring(self):
        """
        Start infinite monitoring loop.

        Continuously polls blockchain and checks for reorgs.
        Runs until stopped or error.
        """
        self.is_running = True
        logger.info(f"🔍 Starting block monitoring for {self.chain}")

        try:
            while self.is_running:
                await self._poll_and_check()
                await asyncio.sleep(self.poll_interval_sec())
        except Exception as e:
            logger.error(f"Block monitor crashed for {self.chain}: {e}")
            self.is_running = False
            raise

    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        logger.info(f"Stopping block monitoring for {self.chain}")
        self.is_running = False

    async def _poll_and_check(self):
        """Poll blockchain and check for reorgs."""
        try:
            self.poll_count += 1
            self.last_poll_time = datetime.utcnow()

            # Get current block
            current_height = await self.tracker.get_current_block_number()

            # Fetch and cache new block header
            new_header = await self.get_block_header(current_height)
            if new_header:
                self._add_to_cache(new_header)

            # Check recent blocks for hash mismatches (reorg detection)
            await self._check_for_reorg(current_height)

            # Log progress periodically
            if self.poll_count % 100 == 0:
                logger.info(
                    f"{self.chain}: polled {self.poll_count} times, "
                    f"current_block={current_height:,}, "
                    f"cache_size={len(self.block_cache)}, "
                    f"reorgs_detected={self.reorgs_detected}"
                )

        except Exception as e:
            logger.error(f"Error in poll cycle for {self.chain}: {e}")

    async def _check_for_reorg(self, current_height: int):
        """
        Check recent blocks for hash mismatches.

        Compares cached block hashes with current chain state.
        If hashes don't match -> reorg detected!
        """
        # Check last 10 blocks (or however many we have cached)
        check_range = min(10, len(self.block_cache))
        start_height = max(current_height - check_range, 0)

        for height in range(start_height, current_height):
            if height not in self.block_cache:
                continue

            # Get cached hash
            cached_header = self.block_cache[height]
            expected_hash = cached_header.hash

            # Get current hash from chain
            actual_header = await self.get_block_header(height)
            if actual_header is None:
                # Block doesn't exist anymore -> definitely a reorg
                logger.warning(
                    f"🚨 REORG: Block {height} on {self.chain} no longer exists! "
                    f"(expected hash: {expected_hash[:10]}...)"
                )
                await self._handle_fork(height, None)
                return

            # Compare hashes
            if actual_header.hash != expected_hash:
                # FORK DETECTED!
                logger.warning(
                    f"🚨 REORG: Hash mismatch at block {height} on {self.chain}! "
                    f"Expected: {expected_hash[:10]}..., "
                    f"Actual: {actual_header.hash[:10]}..."
                )
                await self._handle_fork(height, actual_header)
                return

    async def _handle_fork(self, fork_height: int, new_block: Optional[BlockHeader]):
        """
        Handle detected fork.

        1. Find fork point (where chains diverged)
        2. Identify affected events
        3. Emit reorg signal to handler
        4. Update cache with new canonical chain
        """
        logger.error(f"🚨 FORK DETECTED on {self.chain} at height {fork_height}")

        # Find fork point (backtrack to where chains diverge)
        fork_point = await self._find_fork_point(fork_height)
        affected_range = (fork_point, fork_height)

        logger.error(
            f"Fork range on {self.chain}: blocks {fork_point} - {fork_height} "
            f"({fork_height - fork_point + 1} blocks affected)"
        )

        # Get affected events from event store
        affected_events = self._get_events_in_range(fork_point, fork_height)

        if affected_events:
            logger.warning(
                f"Found {len(affected_events)} events affected by reorg "
                f"on {self.chain}"
            )

            # Emit to ReorgHandler
            from src.layer3_multichain.reorg_handler.handler import reorg_handler

            # TODO: Fetch replacement events from new canonical chain
            new_events = None  # For now, handler will mark as invalidated

            correction_events = reorg_handler.handle_reorg(
                chain=self.chain,
                affected_events=affected_events,
                new_events=new_events
            )

            logger.info(
                f"ReorgHandler created {len(correction_events)} correction events"
            )

        # Update stats
        self.reorgs_detected += 1
        self.last_reorg_time = datetime.utcnow()

        # Clear cache for affected range and re-fetch
        self._clear_cache_range(fork_point, fork_height)

    async def _find_fork_point(self, start_height: int) -> int:
        """
        Find fork point by backtracking until hashes match.

        Uses binary search to efficiently find where chains diverged.
        """
        # Simple implementation: linear backtrack
        # TODO: Binary search for efficiency

        for height in range(start_height, max(0, start_height - 100), -1):
            if height not in self.block_cache:
                continue

            cached_header = self.block_cache[height]
            actual_header = await self.get_block_header(height)

            if actual_header and actual_header.hash == cached_header.hash:
                # Found common ancestor
                return height

        # Couldn't find fork point in last 100 blocks
        return max(0, start_height - 100)

    def _get_events_in_range(self, start_height: int, end_height: int) -> List[RiskEvent]:
        """
        Query event store for events in block range.

        Returns events with block_number in [start_height, end_height].
        """
        affected = []

        for event in self._event_store:
            if event.block_number is None:
                continue

            if start_height <= event.block_number <= end_height:
                if event.chain == self.chain:
                    affected.append(event)

        return affected

    def register_event(self, event: RiskEvent):
        """
        Register an event to track for reorgs.

        Events with block_number set will be monitored.
        If reorg affects their block, they'll be invalidated.
        """
        if event.block_number is not None and event.chain == self.chain:
            self._event_store.append(event)

    def _add_to_cache(self, header: BlockHeader):
        """Add block header to cache (LRU)."""
        self.block_cache[header.number] = header

        # Enforce max cache size (remove oldest)
        while len(self.block_cache) > self.max_cache_size:
            self.block_cache.popitem(last=False)  # Remove oldest (FIFO)

    def _clear_cache_range(self, start: int, end: int):
        """Clear cache for a range of blocks."""
        for height in range(start, end + 1):
            self.block_cache.pop(height, None)

    @abstractmethod
    async def get_block_header(self, block_number: int) -> Optional[BlockHeader]:
        """
        Fetch block header from blockchain.

        Must be implemented by chain-specific subclasses.
        """
        pass

    def get_stats(self) -> Dict:
        """Get monitoring statistics."""
        return {
            "chain": self.chain,
            "is_running": self.is_running,
            "poll_count": self.poll_count,
            "cache_size": len(self.block_cache),
            "max_cache_size": self.max_cache_size,
            "reorgs_detected": self.reorgs_detected,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "last_reorg_time": self.last_reorg_time.isoformat() if self.last_reorg_time else None
        }


class EthereumBlockMonitor(BlockMonitor):
    """Block monitor for Ethereum."""

    def poll_interval_sec(self) -> float:
        """Poll every 3 seconds (Ethereum block time ~12s)."""
        return 3.0

    async def get_block_header(self, block_number: int) -> Optional[BlockHeader]:
        """Fetch Ethereum block header."""
        try:
            # Use web3.py to get block
            block = self.tracker.w3.eth.get_block(block_number)

            return BlockHeader(
                number=block['number'],
                hash=block['hash'].hex(),
                parent_hash=block['parentHash'].hex(),
                timestamp=block['timestamp']
            )
        except Exception as e:
            logger.debug(f"Could not fetch Ethereum block {block_number}: {e}")
            return None


class ArbitrumBlockMonitor(BlockMonitor):
    """Block monitor for Arbitrum."""

    def poll_interval_sec(self) -> float:
        """Poll every 500ms (Arbitrum block time ~250ms)."""
        return 0.5

    async def get_block_header(self, block_number: int) -> Optional[BlockHeader]:
        """Fetch Arbitrum block header."""
        try:
            # Arbitrum uses same web3 interface as Ethereum
            block = self.tracker.w3.eth.get_block(block_number)

            return BlockHeader(
                number=block['number'],
                hash=block['hash'].hex(),
                parent_hash=block['parentHash'].hex(),
                timestamp=block['timestamp']
            )
        except Exception as e:
            logger.debug(f"Could not fetch Arbitrum block {block_number}: {e}")
            return None


class SolanaBlockMonitor(BlockMonitor):
    """Block monitor for Solana."""

    def poll_interval_sec(self) -> float:
        """Poll every 400ms (Solana slot time ~400ms)."""
        return 0.4

    async def get_block_header(self, block_number: int) -> Optional[BlockHeader]:
        """Fetch Solana block/slot header."""
        try:
            # Solana uses slots instead of blocks
            response = await self.tracker.client.get_block(block_number)

            if response.value is None:
                return None

            block = response.value

            # Solana block structure is different
            return BlockHeader(
                number=block_number,
                hash=block.blockhash if hasattr(block, 'blockhash') else str(block_number),
                parent_hash=block.previous_blockhash if hasattr(block, 'previous_blockhash') else "",
                timestamp=block.block_time if hasattr(block, 'block_time') else 0
            )
        except Exception as e:
            logger.debug(f"Could not fetch Solana slot {block_number}: {e}")
            return None
