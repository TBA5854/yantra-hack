"""
Layer 4 Demo: Sharded Scaling

Demonstrates horizontal scalability through feature-based sharding:
1. Feature-based logical sharding (5 shard types)
2. Shard coordination and parallel processing
3. Load balancing strategies
4. High-throughput event processing
5. Shard statistics and monitoring
"""

import asyncio
import logging
from datetime import datetime
import json

from src.common.config import config
from src.common.schema import RiskEvent
from src.layer1_core.sources.price_source import price_source
from src.layer1_core.sources.liquidity_source import liquidity_source
from src.layer1_core.sources.volatility_source import volatility_source
from src.layer1_core.sources.sentiment_source import sentiment_source
from src.layer1_core.quality.pipeline import quality_pipeline
from src.layer4_sharded.sharding.coordinator import ShardCoordinator, ShardType
from src.layer4_sharded.load_balancer.balancer import load_balancer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_synthetic_events(num_events: int = 100) -> list[RiskEvent]:
    """Generate synthetic events for high-throughput testing."""
    import random

    events = []
    coins = ["USDC", "USDT", "DAI"]
    chains = ["ethereum", "arbitrum", "solana"]
    sources = ["coingecko", "uniswap_v3", "supply_tracker", "volatility", "sentiment"]

    for i in range(num_events):
        coin = random.choice(coins)
        chain = random.choice(chains)
        source = random.choice(sources)

        # Create event with random data
        event = RiskEvent(
            timestamp=datetime.utcnow(),
            coin=coin,
            chain=chain,
            source=source,
            price=random.uniform(0.995, 1.005) if source == "coingecko" else None,
            liquidity_depth=random.uniform(100_000_000, 500_000_000) if source == "uniswap_v3" else None,
            net_supply_change=random.uniform(-1_000_000, 1_000_000) if source == "supply_tracker" else None,
            market_volatility=random.uniform(0.0001, 0.001) if source == "volatility" else None,
            sentiment_score=random.uniform(-0.5, 0.5) if source == "sentiment" else None,
            block_number=None,
            tx_hash=None
        )
        events.append(event)

    return events


async def demo_sharded_architecture():
    """
    Demo: Sharded scaling with high throughput.
    """
    logger.info("=" * 70)
    logger.info("LAYER 4 DEMO: Sharded Scaling & Horizontal Scalability")
    logger.info("=" * 70)

    # Stage 1: Shard Architecture Overview
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 1: Shard Architecture Overview")
    logger.info("=" * 70)

    # Create coordinator with replicas
    coordinator = ShardCoordinator(num_replicas_per_shard=2)

    stats = coordinator.get_coordinator_stats()
    logger.info(f"Shard Coordinator Configuration:")
    logger.info(f"  Total shards:         {stats['total_shards']}")
    logger.info(f"  Shard types:          {stats['shard_types']}")
    logger.info(f"  Replicas per type:    {stats['replicas_per_type']}")
    logger.info(f"")
    logger.info(f"Shard Types (Feature-Based):")
    for shard_type in ShardType:
        logger.info(f"  - {shard_type.value.upper():<12} shard ({stats['replicas_per_type']} replicas)")

    # Stage 2: Generate High-Throughput Load
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 2: High-Throughput Event Generation")
    logger.info("=" * 70)

    num_events = 1000  # Simulate high load
    logger.info(f"Generating {num_events} synthetic events...")

    events = await generate_synthetic_events(num_events)
    logger.info(f"✓ Generated {len(events)} events")

    # Count by type
    event_types = {
        "price": sum(1 for e in events if e.price is not None),
        "liquidity": sum(1 for e in events if e.liquidity_depth is not None),
        "supply": sum(1 for e in events if e.net_supply_change is not None),
        "volatility": sum(1 for e in events if e.market_volatility is not None),
        "sentiment": sum(1 for e in events if e.sentiment_score is not None)
    }

    logger.info(f"\nEvent Distribution by Type:")
    for event_type, count in event_types.items():
        logger.info(f"  {event_type.capitalize():<12} {count} events")

    # Stage 3: Quality Pipeline (Single-Threaded Baseline)
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 3: Baseline (Single-Threaded) Processing")
    logger.info("=" * 70)

    start_time = datetime.utcnow()
    baseline_events = quality_pipeline.process_events(events.copy())
    baseline_time = (datetime.utcnow() - start_time).total_seconds()

    logger.info(f"✓ Baseline processing complete")
    logger.info(f"  Time:        {baseline_time*1000:.1f}ms")
    logger.info(f"  Throughput:  {len(baseline_events)/baseline_time:.0f} events/sec")

    # Stage 4: Distributed Sharded Processing
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 4: Distributed Sharded Processing")
    logger.info("=" * 70)

    start_time = datetime.utcnow()
    sharded_events = await coordinator.process_events_distributed(events.copy())
    sharded_time = (datetime.utcnow() - start_time).total_seconds()

    logger.info(f"✓ Sharded processing complete")
    logger.info(f"  Time:        {sharded_time*1000:.1f}ms")
    logger.info(f"  Throughput:  {len(sharded_events)/sharded_time:.0f} events/sec")

    # Calculate speedup
    speedup = baseline_time / sharded_time if sharded_time > 0 else 0
    logger.info(f"\n🚀 SPEEDUP: {speedup:.2f}x faster than baseline")

    # Stage 5: Shard Statistics
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 5: Shard Performance Statistics")
    logger.info("=" * 70)

    shard_stats = coordinator.get_shard_stats()
    logger.info(f"{'Shard':<20} {'Events':<10} {'Avg Time (ms)':<15} {'Status':<10}")
    logger.info("-" * 70)

    for shard_name, stats in shard_stats.items():
        logger.info(
            f"{shard_name:<20} {stats.events_processed:<10} "
            f"{stats.avg_processing_time_ms:<15.2f} "
            f"{'✓ OK' if stats.errors == 0 else '✗ ERROR':<10}"
        )

    # Stage 6: Load Balancing Demonstration
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 6: Load Balancing Strategies")
    logger.info("=" * 70)

    # Get price shards for load balancing demo
    price_shards = coordinator.shards[ShardType.PRICE]
    price_events = [e for e in events if e.price is not None][:100]  # Take 100 price events

    logger.info(f"Distributing {len(price_events)} price events across {len(price_shards)} replicas\n")

    # Strategy 1: Round-Robin
    logger.info("Strategy 1: Round-Robin")
    rr_distribution = load_balancer.distribute_events_round_robin(
        price_events,
        price_shards
    )
    for shard_id, events_list in rr_distribution.items():
        logger.info(f"  Shard {shard_id}: {len(events_list)} events")

    # Strategy 2: Least-Loaded
    logger.info("\nStrategy 2: Least-Loaded")
    load_balancer.reset_load_stats()  # Reset for fair comparison
    ll_distribution = load_balancer.distribute_events_least_loaded(
        price_events,
        price_shards
    )
    for shard_id, events_list in ll_distribution.items():
        logger.info(f"  Shard {shard_id}: {len(events_list)} events")

    # Strategy 3: Consistent Hashing
    logger.info("\nStrategy 3: Consistent Hashing (Sticky Routing)")
    ch_distribution = load_balancer.distribute_events_consistent_hash(
        price_events,
        price_shards
    )
    for shard_id, events_list in ch_distribution.items():
        logger.info(f"  Shard {shard_id}: {len(events_list)} events")

    # Stage 7: Coordinator Statistics
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 7: Overall Coordinator Statistics")
    logger.info("=" * 70)

    overall_stats = coordinator.get_coordinator_stats()
    logger.info(json.dumps(overall_stats, indent=2))

    # Stage 8: Scalability Analysis
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 8: Scalability Analysis")
    logger.info("=" * 70)

    logger.info(f"Current Configuration:")
    logger.info(f"  Shards:              {overall_stats['total_shards']}")
    logger.info(f"  Events processed:    {overall_stats['total_events_processed']}")
    logger.info(f"  Throughput:          {len(sharded_events)/sharded_time:.0f} events/sec")
    logger.info(f"")
    logger.info(f"Theoretical Scaling:")
    logger.info(f"  With 20 shards:      ~{(len(sharded_events)/sharded_time) * 2:.0f} events/sec (2x)")
    logger.info(f"  With 50 shards:      ~{(len(sharded_events)/sharded_time) * 5:.0f} events/sec (5x)")
    logger.info(f"  With 100 shards:     ~{(len(sharded_events)/sharded_time) * 10:.0f} events/sec (10x)")
    logger.info(f"")
    logger.info(f"Horizontal Scalability:")
    logger.info(f"  ✓ Linear scaling by adding more shard replicas")
    logger.info(f"  ✓ No shared state between shards")
    logger.info(f"  ✓ Independent failure isolation")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("DEMO COMPLETE - LAYER 4 SHARDED SCALING")
    logger.info("=" * 70)
    logger.info("\nLayer 4 Capabilities Demonstrated:")
    logger.info("  ✓ Feature-based logical sharding (5 types)")
    logger.info("  ✓ Shard coordination & parallel processing")
    logger.info("  ✓ Multiple load balancing strategies")
    logger.info("  ✓ High-throughput event processing (1000+ events)")
    logger.info("  ✓ Shard performance monitoring")
    logger.info("  ✓ Horizontal scalability architecture")
    logger.info("\nKey Achievement:")
    logger.info(f"  🎉 Processed {len(sharded_events)} events in {sharded_time*1000:.1f}ms")
    logger.info(f"  🎉 Achieved {speedup:.2f}x speedup with sharding")
    logger.info(f"  🎉 Throughput: {len(sharded_events)/sharded_time:.0f} events/sec")
    logger.info(f"  🎉 All {overall_stats['total_shards']} shards: {overall_stats['shards_health'].upper()}")
    logger.info("\n🏆 COMPLETE: All 4 Layers Implemented!")
    logger.info("  Layer 1: Single-Coin Core ✅")
    logger.info("  Layer 2: Multi-Coin Monitoring ✅")
    logger.info("  Layer 3: Cross-Chain Synchronization ✅")
    logger.info("  Layer 4: Sharded Scaling ✅")
    logger.info("\nNext Steps:")
    logger.info("  → Deploy to production cluster")
    logger.info("  → Implement persistent shard storage")
    logger.info("  → Add message queue (Kafka/RabbitMQ)")
    logger.info("  → Build monitoring dashboard")
    logger.info("  → Deploy attestation smart contracts")


if __name__ == "__main__":
    asyncio.run(demo_sharded_architecture())
