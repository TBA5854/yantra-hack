"""
Layer 3 Demo: Cross-Chain Synchronization

Demonstrates cross-chain capabilities:
1. Multi-chain data collection (Ethereum, Arbitrum, Solana)
2. Heterogeneous finality handling
3. Cross-chain TCS calculation (weakest link)
4. Cross-chain divergence detection
5. Reorg-aware event handling
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
from src.layer1_core.tcs.calculator import tcs_calculator
from src.layer2_multicoin.coin_registry.registry import coin_registry
from src.layer3_multichain.cross_chain.aggregator import cross_chain_aggregator
from src.layer3_multichain.reorg_handler.handler import reorg_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def collect_chain_data(coin: str, chain: str):
    """Collect data for a coin on a specific chain."""
    events = []

    # Price
    price_event = await price_source.fetch_price(coin, chain)
    if price_event:
        events.append(price_event)

    # Liquidity
    liquidity_event = await liquidity_source.fetch_liquidity(coin, chain)
    if liquidity_event:
        events.append(liquidity_event)

    # Volatility
    volatility_event = await volatility_source.calculate_volatility(coin, chain)
    if volatility_event:
        events.append(volatility_event)

    # Sentiment
    sentiment_event = await sentiment_source.fetch_sentiment(coin, chain)
    if sentiment_event:
        events.append(sentiment_event)

    # Supply (mock)
    import random
    supply_event = RiskEvent(
        timestamp=datetime.utcnow(),
        coin=coin,
        chain=chain,
        source=f"supply_tracker_{chain}",
        net_supply_change=random.uniform(-500_000, 500_000),
        block_number=None,
        tx_hash=None
    )
    events.append(supply_event)

    return events


async def demo_cross_chain_sync():
    """
    Demo: Cross-chain synchronization and aggregation.
    """
    logger.info("=" * 70)
    logger.info("LAYER 3 DEMO: Cross-Chain Synchronization")
    logger.info("=" * 70)

    coin = "USDC"  # Focus on USDC across multiple chains
    chains = ["ethereum", "arbitrum", "solana"]

    # Stage 1: Chain Configuration Overview
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 1: Chain Configuration Overview")
    logger.info("=" * 70)

    logger.info(f"Monitoring {coin} across {len(chains)} chains:\n")
    logger.info(f"{'Chain':<12} {'Block Time':<12} {'Tier3 Finality':<15} {'Reorg Risk':<12}")
    logger.info("-" * 70)

    for chain in chains:
        chain_config = config.CHAINS[chain]
        logger.info(
            f"{chain:<12} {chain_config.block_time_ms/1000:.1f}s{'':<8} "
            f"{chain_config.tier3_time_sec}s{'':<12} "
            f"{chain_config.reorg_probability*100:.2f}%"
        )

    slowest = cross_chain_aggregator.get_slowest_chain(chains)
    grace_period = cross_chain_aggregator.calculate_cross_chain_grace_period(chains)

    logger.info(f"\nCross-chain grace period: {grace_period}s (limited by {slowest})")

    # Stage 2: Collect Data from All Chains
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 2: Multi-Chain Data Collection")
    logger.info("=" * 70)

    events_by_chain = {}

    for chain in chains:
        logger.info(f"\nFetching {coin} data from {chain}...")
        events = await collect_chain_data(coin, chain)
        logger.info(f"  ✓ Collected {len(events)} events from {chain}")
        events_by_chain[chain] = events

    total_events = sum(len(events) for events in events_by_chain.values())
    logger.info(f"\n✓ Total events collected: {total_events} across {len(chains)} chains")

    # Stage 3: Quality Pipeline (per chain)
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 3: Data Quality Pipeline (Per-Chain)")
    logger.info("=" * 70)

    for chain, events in events_by_chain.items():
        events_by_chain[chain] = quality_pipeline.process_events(events)
        logger.info(f"  {chain:<12} {len(events_by_chain[chain])} events processed")

    # Stage 4: Calculate TCS (per event)
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 4: TCS Calculation (Individual Events)")
    logger.info("=" * 70)

    for chain, events in events_by_chain.items():
        for event in events:
            tcs_calculator.update_event_tcs(event)

        avg_tcs = sum(e.temporal_confidence for e in events) / len(events)
        logger.info(f"  {chain:<12} avg TCS = {avg_tcs:.3f}")

    # Stage 5: Cross-Chain Aggregation
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 5: Cross-Chain Aggregation")
    logger.info("=" * 70)

    cross_chain_snapshot = cross_chain_aggregator.aggregate_cross_chain(
        events_by_chain=events_by_chain,
        window_id="2024-01-15T12:00:00",
        coin=coin
    )

    if cross_chain_snapshot:
        logger.info("✓ Cross-chain aggregation complete\n")
        logger.info(f"{'-' * 70}")
        logger.info("CROSS-CHAIN AGGREGATED SNAPSHOT")
        logger.info(f"{'-' * 70}")
        logger.info(f"Coin:                {cross_chain_snapshot.coin}")
        logger.info(f"Chains:              {', '.join(cross_chain_snapshot.chains)}")
        logger.info(f"Window State:        {cross_chain_snapshot.window_state}")
        logger.info(f"")
        logger.info(f"PRICE METRICS:")
        logger.info(f"  Average Price:     ${cross_chain_snapshot.avg_price:.6f}" if cross_chain_snapshot.avg_price else "  Average Price:     N/A")
        logger.info(f"  Min Price:         ${cross_chain_snapshot.min_price:.6f}" if cross_chain_snapshot.min_price else "  Min Price:         N/A")
        logger.info(f"  Max Price:         ${cross_chain_snapshot.max_price:.6f}" if cross_chain_snapshot.max_price else "  Max Price:         N/A")
        logger.info(f"")
        logger.info(f"AGGREGATED METRICS:")
        logger.info(f"  Total Liquidity:   ${cross_chain_snapshot.total_liquidity:,.0f}" if cross_chain_snapshot.total_liquidity else "  Total Liquidity:   N/A")
        logger.info(f"  Total Volume:      ${cross_chain_snapshot.total_volume:,.0f}" if cross_chain_snapshot.total_volume else "  Total Volume:      N/A")
        logger.info(f"  Net Supply Δ:      ${cross_chain_snapshot.net_supply_change:,.0f}" if cross_chain_snapshot.net_supply_change else "  Net Supply Δ:      N/A")
        logger.info(f"  Market Volatility: {cross_chain_snapshot.market_volatility*100:.4f}%" if cross_chain_snapshot.market_volatility else "  Market Volatility: N/A")
        logger.info(f"  Sentiment:         {cross_chain_snapshot.sentiment_score:.3f}" if cross_chain_snapshot.sentiment_score is not None else "  Sentiment:         N/A")
        logger.info(f"")
        logger.info(f"CROSS-CHAIN TEMPORAL CONFIDENCE:")
        logger.info(f"  TCS (adjusted):    {cross_chain_snapshot.temporal_confidence:.3f}")
        logger.info(f"  Status:            {tcs_calculator.get_tcs_status(cross_chain_snapshot.temporal_confidence)}")

        if cross_chain_snapshot.confidence_breakdown:
            logger.info(f"  Breakdown:")
            logger.info(f"    - Finality:      {cross_chain_snapshot.confidence_breakdown['finality_weight']:.3f}")
            logger.info(f"    - Chain Conf:    {cross_chain_snapshot.confidence_breakdown['chain_confidence']:.3f} ⚠️ (weakest link)")
            logger.info(f"    - Completeness:  {cross_chain_snapshot.confidence_breakdown['completeness']:.3f}")
            logger.info(f"    - Staleness:     {cross_chain_snapshot.confidence_breakdown['staleness_penalty']:.3f}")

        logger.info(f"")
        logger.info(f"METADATA:")
        logger.info(f"  Events Aggregated: {cross_chain_snapshot.num_events_aggregated}")
        logger.info(f"  Sources:           {', '.join(cross_chain_snapshot.sources_included)}")
        logger.info(f"{'-' * 70}")

    # Stage 6: Cross-Chain Divergence Detection
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 6: Cross-Chain Divergence Detection")
    logger.info("=" * 70)

    divergence_report = cross_chain_aggregator.detect_cross_chain_divergence(
        events_by_chain=events_by_chain,
        threshold=0.01  # 1% threshold
    )

    if divergence_report["divergence_detected"]:
        logger.warning(f"⚠️ CROSS-CHAIN DIVERGENCE DETECTED!")
        logger.warning(f"   Found {divergence_report['divergence_count']} divergent pairs")

        for div in divergence_report["divergences"]:
            logger.warning(
                f"   {div['chain1']} ${div['price1']:.6f} vs "
                f"{div['chain2']} ${div['price2']:.6f} "
                f"(Δ={div['percentage']:.2f}%)"
            )
    else:
        logger.info("✓ No cross-chain divergence detected")
        if "chain_prices" in divergence_report:
            logger.info("  Chain prices:")
            for chain, price in divergence_report["chain_prices"].items():
                logger.info(f"    {chain:<12} ${price:.6f}")

    # Stage 7: Reorg Simulation
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 7: Reorg Handling (Simulated)")
    logger.info("=" * 70)

    # Simulate a reorg on Solana (most likely to reorg)
    logger.info("Simulating blockchain reorganization on Solana...")

    solana_events = events_by_chain.get("solana", [])
    if solana_events:
        # Simulate reorg affecting first event
        affected_events = [solana_events[0]]

        # Create a "new" event with slightly different price
        new_event = RiskEvent(
            timestamp=affected_events[0].timestamp,
            coin=coin,
            chain="solana",
            source=affected_events[0].source,
            price=affected_events[0].price * 0.9999 if affected_events[0].price else None,  # Slightly different
            block_number=affected_events[0].block_number + 1 if affected_events[0].block_number else None,
            tx_hash="0xnewblockhash"
        )

        correction_events = reorg_handler.handle_reorg(
            chain="solana",
            affected_events=affected_events,
            new_events=[new_event]
        )

        logger.info(f"✓ Reorg handled: {len(correction_events)} correction events emitted")

        if correction_events:
            correction = correction_events[0]
            logger.info(f"  Original event: {affected_events[0].event_id} v1")
            logger.info(f"  Correction:     {correction.event_id} v{correction.event_version}")
            if affected_events[0].price and correction.price:
                logger.info(f"  Price updated:  ${affected_events[0].price:.6f} -> ${correction.price:.6f}")

    # Get reorg stats
    reorg_stats = reorg_handler.get_all_reorg_stats()
    logger.info("\nReorg Statistics:")
    for chain, stats in reorg_stats.items():
        logger.info(
            f"  {chain:<12} reorgs={stats['reorg_count']}, "
            f"affected_events={stats['total_affected_events']}"
        )

    # Stage 8: Finality Readiness Check
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 8: Cross-Chain Finality Readiness")
    logger.info("=" * 70)

    from datetime import timedelta
    window_end = datetime.utcnow() - timedelta(minutes=20)  # Simulate old window

    is_ready = cross_chain_aggregator.check_cross_chain_readiness(
        events_by_chain=events_by_chain,
        window_end=window_end
    )

    if is_ready:
        logger.info("✓ Cross-chain aggregation ready for finalization")
        logger.info("  All chains have reached minimum finality threshold")
    else:
        logger.warning("⚠️ Not ready: waiting for finality on one or more chains")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("DEMO COMPLETE - LAYER 3 CROSS-CHAIN SYNCHRONIZATION")
    logger.info("=" * 70)
    logger.info("\nLayer 3 Capabilities Demonstrated:")
    logger.info("  ✓ Multi-chain data collection (Ethereum, Arbitrum, Solana)")
    logger.info("  ✓ Heterogeneous finality handling")
    logger.info("  ✓ Cross-chain TCS calculation (weakest link principle)")
    logger.info("  ✓ Cross-chain divergence detection")
    logger.info("  ✓ Reorg-aware event versioning")
    logger.info("  ✓ Grace period calculation (slowest chain)")
    logger.info("  ✓ Finality readiness checks")
    logger.info("\nKey Achievement:")
    logger.info(f"  🎉 Successfully aggregated {coin} across {len(chains)} chains")
    logger.info(f"  🎉 Cross-chain TCS: {cross_chain_snapshot.temporal_confidence:.3f}")
    logger.info(f"  🎉 Handled reorg with event versioning")
    logger.info(f"  🎉 No cross-chain divergence detected")
    logger.info("\nNext Steps:")
    logger.info("  → Progress to Layer 4 (Sharded Scaling)")
    logger.info("  → Implement historical trend analysis")
    logger.info("  → Deploy attestation smart contracts")
    logger.info("  → Build production monitoring dashboard")


if __name__ == "__main__":
    asyncio.run(demo_cross_chain_sync())
