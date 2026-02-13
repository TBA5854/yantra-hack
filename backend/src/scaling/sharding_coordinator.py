"""
Shard Coordinator for distributed event processing.

Implements feature-based logical sharding:
- Price Shard: Handles price events
- Liquidity Shard: Handles liquidity events
- Supply Shard: Handles supply events
- Volatility Shard: Handles volatility events
- Sentiment Shard: Handles sentiment events

Each shard processes events independently in parallel, then results
are aggregated by the coordinator.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio
import logging

from src.common.schema import RiskEvent, AggregatedRiskSnapshot
from src.confidence.tcs_calculator import tcs_calculator

logger = logging.getLogger(__name__)


class ShardType(Enum):
    """Types of feature-based shards."""
    PRICE = "price"
    LIQUIDITY = "liquidity"
    SUPPLY = "supply"
    VOLATILITY = "volatility"
    SENTIMENT = "sentiment"


@dataclass
class ShardStats:
    """Statistics for a shard."""
    shard_type: ShardType
    events_processed: int = 0
    events_per_second: float = 0.0
    avg_processing_time_ms: float = 0.0
    errors: int = 0
    last_processed: Optional[datetime] = None


class Shard:
    """
    Individual shard for processing specific event types.

    Each shard runs independently and can be scaled horizontally.
    """

    def __init__(self, shard_type: ShardType, shard_id: int = 0):
        self.shard_type = shard_type
        self.shard_id = shard_id
        self.stats = ShardStats(shard_type=shard_type)

        logger.info(f"Initialized shard: {shard_type.value}[{shard_id}]")

    async def process_events(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """
        Process events for this shard.

        In production, this would:
        - Run on separate worker processes
        - Have its own connection pools
        - Store results in shard-specific storage
        - Communicate via message queue

        For demo, we simulate parallel processing with asyncio.
        """
        if not events:
            return []

        start_time = datetime.utcnow()

        # Simulate processing delay (would be actual computation in production)
        await asyncio.sleep(0.01 * len(events))  # 10ms per event

        # Filter events for this shard's feature type
        relevant_events = self._filter_events(events)

        # Process TCS for each event
        for event in relevant_events:
            tcs_calculator.update_event_tcs(event)

        # Update stats
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        self.stats.events_processed += len(relevant_events)
        self.stats.avg_processing_time_ms = processing_time * 1000 / len(relevant_events) if relevant_events else 0
        self.stats.last_processed = datetime.utcnow()

        if relevant_events:
            logger.debug(
                f"Shard {self.shard_type.value}[{self.shard_id}] processed "
                f"{len(relevant_events)} events in {processing_time*1000:.1f}ms"
            )

        return relevant_events

    def _filter_events(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """Filter events relevant to this shard's feature type."""
        filtered = []

        for event in events:
            if self.shard_type == ShardType.PRICE and event.price is not None:
                filtered.append(event)
            elif self.shard_type == ShardType.LIQUIDITY and event.liquidity_depth is not None:
                filtered.append(event)
            elif self.shard_type == ShardType.SUPPLY and event.net_supply_change is not None:
                filtered.append(event)
            elif self.shard_type == ShardType.VOLATILITY and event.market_volatility is not None:
                filtered.append(event)
            elif self.shard_type == ShardType.SENTIMENT and event.sentiment_score is not None:
                filtered.append(event)

        return filtered


class ShardCoordinator:
    """
    Coordinates multiple shards for distributed processing.

    Responsibilities:
    1. Route events to appropriate shards
    2. Manage shard lifecycle
    3. Aggregate results from all shards
    4. Monitor shard health and performance
    5. Load balancing across shard replicas
    """

    def __init__(self, num_replicas_per_shard: int = 1):
        """
        Initialize coordinator with shards.

        Args:
            num_replicas_per_shard: Number of replica shards per feature type
        """
        self.num_replicas = num_replicas_per_shard

        # Create shards (one per feature type, with optional replicas)
        self.shards: Dict[ShardType, List[Shard]] = {
            shard_type: [
                Shard(shard_type, replica_id)
                for replica_id in range(num_replicas_per_shard)
            ]
            for shard_type in ShardType
        }

        # Flatten for easy iteration
        self.all_shards = [
            shard
            for shard_list in self.shards.values()
            for shard in shard_list
        ]

        logger.info(
            f"ShardCoordinator initialized with {len(self.all_shards)} shards "
            f"({len(ShardType)} types × {num_replicas_per_shard} replicas)"
        )

    async def process_events_distributed(
        self,
        events: List[RiskEvent]
    ) -> List[RiskEvent]:
        """
        Process events across all shards in parallel.

        This is the key method that enables horizontal scaling.

        Args:
            events: All events to process

        Returns:
            All processed events from all shards
        """
        if not events:
            return []

        start_time = datetime.utcnow()

        logger.info(f"Distributing {len(events)} events across {len(self.all_shards)} shards")

        # Process events in parallel across all shards
        # Each shard will filter for its relevant events
        tasks = [
            shard.process_events(events)
            for shard in self.all_shards
        ]

        # Wait for all shards to complete (parallel processing!)
        shard_results = await asyncio.gather(*tasks)

        # Flatten results
        all_processed = []
        for result in shard_results:
            all_processed.extend(result)

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        logger.info(
            f"Distributed processing complete: {len(all_processed)} events "
            f"in {processing_time*1000:.1f}ms "
            f"({len(all_processed)/processing_time:.0f} events/sec)"
        )

        return all_processed

    async def aggregate_shard_results(
        self,
        window_id: str,
        coin: str
    ) -> Optional[AggregatedRiskSnapshot]:
        """
        Aggregate results from all shards into a unified snapshot.

        In production, this would:
        - Query each shard's storage
        - Merge results with conflict resolution
        - Calculate cross-shard TCS

        For demo, we aggregate from in-memory shard outputs.
        """
        # In production implementation, would collect from shard outputs
        # For now, this is a placeholder showing the architecture
        pass

    def get_shard_stats(self) -> Dict[str, ShardStats]:
        """Get statistics for all shards."""
        return {
            f"{shard.shard_type.value}[{shard.shard_id}]": shard.stats
            for shard in self.all_shards
        }

    def get_coordinator_stats(self) -> Dict:
        """Get overall coordinator statistics."""
        total_events = sum(s.stats.events_processed for s in self.all_shards)
        total_errors = sum(s.stats.errors for s in self.all_shards)

        # Calculate events per shard type
        events_by_type = {}
        for shard_type in ShardType:
            type_events = sum(
                s.stats.events_processed
                for s in self.shards[shard_type]
            )
            events_by_type[shard_type.value] = type_events

        return {
            "total_shards": len(self.all_shards),
            "shard_types": len(ShardType),
            "replicas_per_type": self.num_replicas,
            "total_events_processed": total_events,
            "total_errors": total_errors,
            "events_by_type": events_by_type,
            "shards_health": "healthy" if total_errors == 0 else "degraded"
        }


# Singleton coordinator
shard_coordinator = ShardCoordinator(num_replicas_per_shard=1)
