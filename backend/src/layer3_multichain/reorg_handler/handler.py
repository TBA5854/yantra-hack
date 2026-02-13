"""
Reorg handler with event versioning.

Handles blockchain reorganizations by:
1. Detecting invalidated events (blocks no longer in canonical chain)
2. Emitting correction events
3. Updating event versions
4. Maintaining event history
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import logging

from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


@dataclass
class ReorgEvent:
    """Record of a blockchain reorganization."""
    chain: str
    timestamp: datetime
    original_block: int
    new_block: int
    depth: int  # How many blocks were reorg'd
    affected_events: List[str]  # Event IDs


class ReorgHandler:
    """
    Handles blockchain reorganizations across multiple chains.

    Reorgs are more common on:
    - Solana (probabilistic finality)
    - Arbitrum (L2 batching)
    - Ethereum (less common with PoS, but still possible)

    Strategy:
    1. Monitor block headers for reorgs
    2. Mark invalidated events
    3. Emit correction events with updated data
    4. Increment event version numbers
    """

    def __init__(self):
        # Track reorg history per chain
        self.reorg_history: Dict[str, List[ReorgEvent]] = {
            "ethereum": [],
            "arbitrum": [],
            "solana": []
        }

        # Track event versions
        self.event_versions: Dict[str, int] = {}  # event_id -> version

    def detect_reorg(
        self,
        chain: str,
        expected_block: int,
        actual_block: int
    ) -> bool:
        """
        Detect if a reorg occurred.

        Args:
            chain: Blockchain name
            expected_block: Block number we thought was canonical
            actual_block: Current block number at that height

        Returns:
            True if reorg detected (blocks don't match)
        """
        is_reorg = expected_block != actual_block

        if is_reorg:
            logger.warning(
                f"Reorg detected on {chain}: "
                f"expected block {expected_block}, got {actual_block}"
            )

        return is_reorg

    def handle_reorg(
        self,
        chain: str,
        affected_events: List[RiskEvent],
        new_events: Optional[List[RiskEvent]] = None
    ) -> List[RiskEvent]:
        """
        Handle a blockchain reorganization.

        Args:
            chain: Blockchain name
            affected_events: Events that were in reorg'd blocks
            new_events: Replacement events from new canonical chain

        Returns:
            List of correction events to emit
        """
        correction_events = []

        logger.error(
            f"🚨 REORG HANDLER: Processing {len(affected_events)} "
            f"affected events on {chain}"
        )

        for old_event in affected_events:
            # Mark old event as invalidated
            old_event.invalidated = True
            old_event.reorg_detected_at = datetime.utcnow()

            # Find replacement event (if any)
            replacement = None
            if new_events:
                # Try to match by coin + source + approximate timestamp
                replacement = self._find_replacement_event(old_event, new_events)

            if replacement:
                # Create correction event
                correction = self._create_correction_event(old_event, replacement)
                correction_events.append(correction)

                old_event.replacement_event_id = correction.event_id

                logger.info(
                    f"Correction event created: {old_event.event_id} -> "
                    f"{correction.event_id} (v{correction.event_version})"
                )
            else:
                # No replacement found - event was removed in reorg
                logger.warning(
                    f"No replacement found for invalidated event: "
                    f"{old_event.event_id} (removed in reorg)"
                )

        # Record reorg
        reorg_record = ReorgEvent(
            chain=chain,
            timestamp=datetime.utcnow(),
            original_block=affected_events[0].block_number if affected_events else 0,
            new_block=new_events[0].block_number if new_events else 0,
            depth=len(affected_events),
            affected_events=[e.event_id for e in affected_events]
        )
        self.reorg_history[chain].append(reorg_record)

        return correction_events

    def _find_replacement_event(
        self,
        old_event: RiskEvent,
        new_events: List[RiskEvent]
    ) -> Optional[RiskEvent]:
        """
        Find replacement event in new canonical chain.

        Match criteria:
        - Same coin
        - Same source
        - Similar timestamp (within 60 seconds)
        """
        for new_event in new_events:
            if (new_event.coin == old_event.coin and
                new_event.source == old_event.source):

                # Check timestamp proximity (within 1 minute)
                time_diff = abs((new_event.timestamp - old_event.timestamp).total_seconds())
                if time_diff < 60:
                    return new_event

        return None

    def _create_correction_event(
        self,
        old_event: RiskEvent,
        new_event: RiskEvent
    ) -> RiskEvent:
        """
        Create a correction event with incremented version.

        The correction event:
        - Has the same event_id as the original
        - Has an incremented event_version
        - Contains the updated data from new_event
        """
        # Get current version
        current_version = self.event_versions.get(old_event.event_id, 1)
        new_version = current_version + 1
        self.event_versions[old_event.event_id] = new_version

        # Create correction event (copy new_event data with same event_id)
        correction = RiskEvent(
            event_id=old_event.event_id,  # Keep same ID
            event_version=new_version,     # Increment version
            timestamp=new_event.timestamp,
            coin=new_event.coin,
            chain=new_event.chain,
            source=new_event.source,
            # Copy data fields from new event
            price=new_event.price,
            volume=new_event.volume,
            liquidity_depth=new_event.liquidity_depth,
            net_supply_change=new_event.net_supply_change,
            market_volatility=new_event.market_volatility,
            sentiment_score=new_event.sentiment_score,
            # Copy blockchain fields from new event
            block_number=new_event.block_number,
            tx_hash=new_event.tx_hash,
            confirmation_count=new_event.confirmation_count,
            finality_tier=new_event.finality_tier,
            is_finalized=False,  # Reset finality
            # Metadata
            invalidated=False,  # This is the corrected version
            original_block_number=old_event.block_number  # Record original block
        )

        logger.info(
            f"Created correction event: {correction.event_id} v{new_version} "
            f"(block {old_event.block_number} -> {new_event.block_number})"
        )

        return correction

    def get_reorg_stats(self, chain: str) -> Dict:
        """Get reorg statistics for a chain."""
        reorgs = self.reorg_history.get(chain, [])

        if not reorgs:
            return {
                "chain": chain,
                "reorg_count": 0,
                "total_affected_events": 0,
                "max_depth": 0
            }

        return {
            "chain": chain,
            "reorg_count": len(reorgs),
            "total_affected_events": sum(len(r.affected_events) for r in reorgs),
            "max_depth": max(r.depth for r in reorgs),
            "latest_reorg": reorgs[-1].timestamp.isoformat() if reorgs else None
        }

    def get_all_reorg_stats(self) -> Dict[str, Dict]:
        """Get reorg statistics for all chains."""
        return {
            chain: self.get_reorg_stats(chain)
            for chain in ["ethereum", "arbitrum", "solana"]
        }

    def should_wait_for_finality(
        self,
        event: RiskEvent,
        min_confirmations: int = 12
    ) -> bool:
        """
        Check if we should wait for more confirmations before using this event.

        Args:
            event: Event to check
            min_confirmations: Minimum confirmations required

        Returns:
            True if we should wait for more confirmations
        """
        if event.block_number is None:
            # Off-chain event - no blockchain confirmations needed
            return False

        if event.is_finalized:
            # Already finalized - safe to use
            return False

        if event.confirmation_count < min_confirmations:
            logger.debug(
                f"Event {event.event_id} has {event.confirmation_count} confirmations, "
                f"waiting for {min_confirmations}"
            )
            return True

        return False


# Singleton handler
reorg_handler = ReorgHandler()
