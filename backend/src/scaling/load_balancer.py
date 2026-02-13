"""
Load Balancer for distributing events across shard replicas.

Implements:
- Round-robin distribution
- Least-loaded distribution
- Consistent hashing (for sticky routing)
- Health checking
"""

from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime
import hashlib
import logging

from src.common.schema import RiskEvent
from src.scaling.sharding_coordinator import Shard, ShardType

logger = logging.getLogger(__name__)


class LoadBalancer:
    """
    Load balances events across shard replicas.

    When multiple replicas exist for a shard type (e.g., 3 price shards),
    the load balancer decides which replica gets each event.
    """

    def __init__(self):
        # Track current round-robin index per shard type
        self.round_robin_index: Dict[ShardType, int] = defaultdict(int)

        # Track load per shard (for least-loaded strategy)
        self.shard_load: Dict[str, int] = defaultdict(int)

    def distribute_events_round_robin(
        self,
        events: List[RiskEvent],
        shards: List[Shard]
    ) -> Dict[int, List[RiskEvent]]:
        """
        Distribute events using round-robin across shard replicas.

        Args:
            events: Events to distribute
            shards: List of shard replicas

        Returns:
            Dict mapping shard_id -> events for that shard
        """
        if not shards:
            return {}

        distribution: Dict[int, List[RiskEvent]] = {
            shard.shard_id: [] for shard in shards
        }

        shard_type = shards[0].shard_type
        current_idx = self.round_robin_index[shard_type]

        for event in events:
            # Assign to next shard in round-robin
            shard = shards[current_idx % len(shards)]
            distribution[shard.shard_id].append(event)

            # Move to next shard
            current_idx += 1

        # Update index for next call
        self.round_robin_index[shard_type] = current_idx

        logger.debug(
            f"Round-robin distribution for {shard_type.value}: "
            f"{len(events)} events across {len(shards)} replicas"
        )

        return distribution

    def distribute_events_least_loaded(
        self,
        events: List[RiskEvent],
        shards: List[Shard]
    ) -> Dict[int, List[RiskEvent]]:
        """
        Distribute events to least-loaded shard replicas.

        Args:
            events: Events to distribute
            shards: List of shard replicas

        Returns:
            Dict mapping shard_id -> events for that shard
        """
        if not shards:
            return {}

        distribution: Dict[int, List[RiskEvent]] = {
            shard.shard_id: [] for shard in shards
        }

        for event in events:
            # Find least-loaded shard
            least_loaded = min(
                shards,
                key=lambda s: self.shard_load[f"{s.shard_type.value}[{s.shard_id}]"]
            )

            distribution[least_loaded.shard_id].append(event)

            # Update load
            shard_key = f"{least_loaded.shard_type.value}[{least_loaded.shard_id}]"
            self.shard_load[shard_key] += 1

        return distribution

    def distribute_events_consistent_hash(
        self,
        events: List[RiskEvent],
        shards: List[Shard]
    ) -> Dict[int, List[RiskEvent]]:
        """
        Distribute events using consistent hashing.

        Events for the same coin+chain will always go to the same shard.
        This enables sticky routing for stateful processing.

        Args:
            events: Events to distribute
            shards: List of shard replicas

        Returns:
            Dict mapping shard_id -> events for that shard
        """
        if not shards:
            return {}

        distribution: Dict[int, List[RiskEvent]] = {
            shard.shard_id: [] for shard in shards
        }

        for event in events:
            # Hash coin+chain to get consistent shard assignment
            key = f"{event.coin}:{event.chain}"
            hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
            shard_idx = hash_value % len(shards)

            shard = shards[shard_idx]
            distribution[shard.shard_id].append(event)

        logger.debug(
            f"Consistent hash distribution: "
            f"{len(events)} events across {len(shards)} replicas"
        )

        return distribution

    def get_load_stats(self) -> Dict:
        """Get current load statistics."""
        return {
            "shard_load": dict(self.shard_load),
            "total_load": sum(self.shard_load.values())
        }

    def reset_load_stats(self):
        """Reset load statistics."""
        self.shard_load.clear()
        self.round_robin_index.clear()


# Singleton load balancer
load_balancer = LoadBalancer()
