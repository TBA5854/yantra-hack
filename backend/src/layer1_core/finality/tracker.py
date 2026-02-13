"""
Finality tracking for heterogeneous blockchain finality.
Monitors confirmation counts and determines finality tier for events.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio
import logging

from src.common.schema import RiskEvent, FinalityTier
from src.common.config import config, ChainConfig

logger = logging.getLogger(__name__)


class FinalityTracker(ABC):
    """Abstract base class for chain-specific finality tracking."""

    def __init__(self, chain_config: ChainConfig):
        self.chain_config = chain_config
        self.name = chain_config.name

    @abstractmethod
    async def get_current_block_number(self) -> int:
        """Get the current block number from the chain."""
        pass

    @abstractmethod
    async def check_block_exists(self, block_number: int) -> bool:
        """Check if a block still exists (reorg detection)."""
        pass

    def calculate_finality_tier(self, confirmations: int) -> FinalityTier:
        """
        Determine finality tier based on confirmation count.

        Returns:
            FinalityTier: TIER1 (0.3), TIER2 (0.8), or TIER3 (1.0)
        """
        if confirmations >= self.chain_config.tier3_confirmations:
            return FinalityTier.TIER3
        elif confirmations >= self.chain_config.tier2_confirmations:
            return FinalityTier.TIER2
        else:
            return FinalityTier.TIER1

    def get_finality_confidence(self, tier: FinalityTier) -> float:
        """Get numeric confidence value for finality tier."""
        confidence_map = {
            FinalityTier.TIER1: 0.3,
            FinalityTier.TIER2: 0.8,
            FinalityTier.TIER3: 1.0
        }
        return confidence_map[tier]

    async def update_event_finality(self, event: RiskEvent) -> RiskEvent:
        """
        Update finality information for an event.

        Args:
            event: RiskEvent with block_number set

        Returns:
            Updated RiskEvent with current finality tier
        """
        if event.block_number is None:
            # Off-chain data source - use timestamp-based finality
            return self._update_offchain_finality(event)

        try:
            current_block = await self.get_current_block_number()
            confirmations = max(0, current_block - event.block_number + 1)

            # Check for reorg
            block_exists = await self.check_block_exists(event.block_number)
            if not block_exists:
                logger.warning(
                    f"Reorg detected for event {event.event_id} on {self.name} "
                    f"at block {event.block_number}"
                )
                event.invalidated = True
                event.reorg_detected_at = datetime.utcnow()
                event.original_block_number = event.block_number
                return event

            # Update confirmation count
            event.confirmation_count = confirmations

            # Calculate finality tier
            tier = self.calculate_finality_tier(confirmations)
            event.finality_tier = tier.value
            event.temporal_confidence = self.get_finality_confidence(tier)

            # Mark as finalized if tier3
            if tier == FinalityTier.TIER3 and not event.is_finalized:
                event.is_finalized = True
                event.finality_timestamp = datetime.utcnow()
                logger.info(
                    f"Event {event.event_id} reached finality on {self.name} "
                    f"at block {current_block}"
                )

            return event

        except Exception as e:
            logger.error(f"Error updating finality for event {event.event_id}: {e}")
            return event

    def _update_offchain_finality(self, event: RiskEvent) -> RiskEvent:
        """
        Update finality for off-chain data sources based on timestamp age.

        Off-chain data (price feeds, sentiment) don't have block confirmations,
        so we use time-based finality approximation.
        """
        age = (datetime.utcnow() - event.timestamp).total_seconds()

        if age >= self.chain_config.tier3_time_sec:
            event.finality_tier = FinalityTier.TIER3.value
            event.temporal_confidence = 1.0
            event.is_finalized = True
            if event.finality_timestamp is None:
                event.finality_timestamp = datetime.utcnow()
        elif age >= self.chain_config.tier2_time_sec:
            event.finality_tier = FinalityTier.TIER2.value
            event.temporal_confidence = 0.8
        else:
            event.finality_tier = FinalityTier.TIER1.value
            event.temporal_confidence = 0.3

        return event


class EthereumFinalityTracker(FinalityTracker):
    """Finality tracker for Ethereum (PoS with 12.8 min finality)."""

    def __init__(self):
        super().__init__(config.CHAINS["ethereum"])
        # TODO: Initialize Web3 connection
        self.w3 = None

    async def get_current_block_number(self) -> int:
        """Get current Ethereum block number."""
        # TODO: Implement with web3.py
        # return await self.w3.eth.block_number
        raise NotImplementedError("Ethereum RPC connection not implemented")

    async def check_block_exists(self, block_number: int) -> bool:
        """Check if block exists (reorg detection)."""
        # TODO: Implement with web3.py
        # try:
        #     block = await self.w3.eth.get_block(block_number)
        #     return block is not None
        # except:
        #     return False
        raise NotImplementedError("Ethereum RPC connection not implemented")


class ArbitrumFinalityTracker(FinalityTracker):
    """
    Finality tracker for Arbitrum (L2 with ~13 sec batch posting + L1 finality).

    Arbitrum has two-phase finality:
    1. L2 confirmation (~250ms) - optimistic
    2. L1 batch posted (~13 sec) - tier2
    3. L1 finalized (~15 min total) - tier3
    """

    def __init__(self):
        super().__init__(config.CHAINS["arbitrum"])
        self.w3 = None

    async def get_current_block_number(self) -> int:
        """Get current Arbitrum block number."""
        # TODO: Implement with web3.py
        raise NotImplementedError("Arbitrum RPC connection not implemented")

    async def check_block_exists(self, block_number: int) -> bool:
        """Check if block exists (reorg detection)."""
        # TODO: Implement with web3.py
        raise NotImplementedError("Arbitrum RPC connection not implemented")


class SolanaFinalityTracker(FinalityTracker):
    """
    Finality tracker for Solana (probabilistic finality with rooted confirmation).

    Solana finality stages:
    1. 1 confirmation (~400ms) - optimistic
    2. 32 confirmations (~13 sec) - optimistic confirmation
    3. Rooted (~2 min) - 2/3 of stake has voted, probabilistically final
    """

    def __init__(self):
        super().__init__(config.CHAINS["solana"])
        self.client = None

    async def get_current_block_number(self) -> int:
        """Get current Solana slot (equivalent to block number)."""
        # TODO: Implement with solana.py
        raise NotImplementedError("Solana RPC connection not implemented")

    async def check_block_exists(self, block_number: int) -> bool:
        """Check if block/slot exists (reorg detection)."""
        # TODO: Implement with solana.py
        # Solana uses slots; need to check if slot is still valid
        raise NotImplementedError("Solana RPC connection not implemented")


class FinalityTrackerRegistry:
    """Registry for managing multiple chain finality trackers."""

    def __init__(self):
        self.trackers: Dict[str, FinalityTracker] = {
            "ethereum": EthereumFinalityTracker(),
            "arbitrum": ArbitrumFinalityTracker(),
            "solana": SolanaFinalityTracker()
        }

    def get_tracker(self, chain: str) -> Optional[FinalityTracker]:
        """Get finality tracker for a specific chain."""
        return self.trackers.get(chain)

    async def update_event_finality(self, event: RiskEvent) -> RiskEvent:
        """Update finality for an event using appropriate chain tracker."""
        tracker = self.get_tracker(event.chain)
        if tracker is None:
            logger.warning(f"No finality tracker for chain: {event.chain}")
            return event

        return await tracker.update_event_finality(event)

    async def monitor_finality_upgrades(
        self,
        events: list[RiskEvent],
        check_interval_sec: int = 10
    ):
        """
        Continuously monitor events and upgrade their finality tiers.

        This background task checks unfinalized events periodically and
        updates their finality status as they gain confirmations.
        """
        logger.info(f"Starting finality monitor for {len(events)} events")

        while True:
            unfinalized = [e for e in events if not e.is_finalized and not e.invalidated]

            if not unfinalized:
                logger.info("All events finalized, stopping monitor")
                break

            logger.debug(f"Checking finality for {len(unfinalized)} unfinalized events")

            # Update finality for all unfinalized events
            tasks = [self.update_event_finality(event) for event in unfinalized]
            await asyncio.gather(*tasks, return_exceptions=True)

            await asyncio.sleep(check_interval_sec)


# Singleton registry
finality_registry = FinalityTrackerRegistry()
