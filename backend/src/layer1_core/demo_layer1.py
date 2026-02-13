"""
Layer 1 Demo: Single-Coin Core

Demonstrates the perfected single-coin risk monitoring pipeline:
1. Fetch price data from CoinGecko
2. Apply data quality pipeline
3. Update TCS (Temporal Confidence Score)
4. Window state machine
5. Generate aggregated snapshot
"""

import asyncio
import logging
from datetime import datetime, timedelta

from src.common.config import config
from src.common.schema import WindowState
from src.layer1_core.sources.price_source import price_source
from src.layer1_core.quality.pipeline import quality_pipeline
from src.layer1_core.tcs.calculator import tcs_calculator
from src.layer1_core.pipeline.window_manager import WindowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_single_window():
    """
    Demo: Fetch prices, process through quality pipeline, and aggregate in a window.

    This demonstrates the core Layer 1 functionality without blockchain connections.
    """
    logger.info("=" * 70)
    logger.info("LAYER 1 DEMO: Single-Coin Core (USDC on Ethereum)")
    logger.info("=" * 70)

    # Initialize window manager
    window_manager = WindowManager(window_size_sec=60)  # 1-minute windows for demo

    # Coins to monitor
    coins = ["USDC", "USDT", "DAI"]
    chain = "ethereum"

    logger.info(f"\nFetching prices for {len(coins)} stablecoins...")

    # Fetch prices (simulates real-time data ingestion)
    events = await price_source.fetch_prices_batch(coins, chain=chain)

    if not events:
        logger.error("Failed to fetch any price data. Check API keys and network.")
        return

    logger.info(f"✓ Fetched {len(events)} price events")

    # Display raw events
    logger.info("\n" + "=" * 70)
    logger.info("RAW EVENTS (Before Quality Pipeline)")
    logger.info("=" * 70)
    for event in events:
        logger.info(
            f"  {event.coin:6s} | ${event.price:.6f} | "
            f"vol=${event.volume:,.0f} | source={event.source}"
        )

    # Stage 1: Quality Pipeline
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 1: Data Quality Pipeline")
    logger.info("=" * 70)

    quality_events = quality_pipeline.process_events(events)
    logger.info(f"✓ Quality pipeline processed {len(quality_events)} events")
    logger.info(f"  - Outliers detected: {sum(1 for e in quality_events if e.is_outlier)}")
    logger.info(f"  - Events filtered: {len(events) - len(quality_events)}")

    # Stage 2: Calculate TCS for each event
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 2: Temporal Confidence Score (TCS) Calculation")
    logger.info("=" * 70)

    for event in quality_events:
        tcs_calculator.update_event_tcs(event)

    logger.info("✓ TCS calculated for all events")
    for event in quality_events:
        logger.info(
            f"  {event.coin:6s} | TCS={event.temporal_confidence:.3f} | "
            f"tier={event.finality_tier} | quality={event.quality_score:.2f}"
        )

    # Stage 3: Add events to window
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 3: Window State Machine")
    logger.info("=" * 70)

    for event in quality_events:
        window_manager.add_event(event)

    current_window = window_manager.current_window
    logger.info(f"✓ Added {len(quality_events)} events to window: {current_window.window_id}")
    logger.info(f"  - Window state: {current_window.state.value}")
    logger.info(f"  - Window start: {current_window.window_start.isoformat()}")
    logger.info(f"  - Window end: {current_window.window_end.isoformat()}")

    # Stage 4: Simulate window closure and aggregation
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 4: Window Aggregation (Simulated)")
    logger.info("=" * 70)

    # Fast-forward time to close window (for demo purposes)
    logger.info("Simulating window closure...")

    # Manually transition window to FINAL (normally done by state machine)
    current_window.state = WindowState.PROVISIONAL
    for event in current_window.events:
        event.window_state = WindowState.PROVISIONAL.value
        event.is_finalized = True  # Simulate finality for demo
        event.finality_tier = "tier3"
        event.temporal_confidence = 1.0

    current_window.transition_to_final()

    # Display aggregated snapshot
    snapshot = current_window.snapshot
    if snapshot:
        logger.info("✓ Window finalized - Aggregated Snapshot Generated")
        logger.info(f"\n{'-' * 70}")
        logger.info("AGGREGATED RISK SNAPSHOT")
        logger.info(f"{'-' * 70}")
        logger.info(f"Coin:                {snapshot.coin}")
        logger.info(f"Chains:              {', '.join(snapshot.chains)}")
        logger.info(f"Window ID:           {snapshot.window_id}")
        logger.info(f"Window State:        {snapshot.window_state}")
        logger.info(f"")
        logger.info(f"PRICE METRICS:")
        logger.info(f"  Average Price:     ${snapshot.avg_price:.6f}" if snapshot.avg_price else "  Average Price:     N/A")
        logger.info(f"  Min Price:         ${snapshot.min_price:.6f}" if snapshot.min_price else "  Min Price:         N/A")
        logger.info(f"  Max Price:         ${snapshot.max_price:.6f}" if snapshot.max_price else "  Max Price:         N/A")
        logger.info(f"")
        logger.info(f"LIQUIDITY & VOLUME:")
        logger.info(f"  Total Liquidity:   ${snapshot.total_liquidity:,.0f}" if snapshot.total_liquidity else "  Total Liquidity:   N/A")
        logger.info(f"  Total Volume:      ${snapshot.total_volume:,.0f}" if snapshot.total_volume else "  Total Volume:      N/A")
        logger.info(f"")
        logger.info(f"TEMPORAL CONFIDENCE:")
        logger.info(f"  TCS:               {snapshot.temporal_confidence:.3f}")
        logger.info(f"  Status:            {tcs_calculator.get_tcs_status(snapshot.temporal_confidence)}")
        if snapshot.confidence_breakdown:
            logger.info(f"  Breakdown:")
            logger.info(f"    - Finality:      {snapshot.confidence_breakdown['finality_weight']:.3f}")
            logger.info(f"    - Chain Conf:    {snapshot.confidence_breakdown['chain_confidence']:.3f}")
            logger.info(f"    - Completeness:  {snapshot.confidence_breakdown['completeness']:.3f}")
            logger.info(f"    - Staleness:     {snapshot.confidence_breakdown['staleness_penalty']:.3f}")
        logger.info(f"")
        logger.info(f"DEPEG ALERT:")
        logger.info(f"  Depegged:          {snapshot.is_depegged}")
        if snapshot.depeg_severity:
            logger.info(f"  Severity:          {snapshot.depeg_severity:.4f} ({snapshot.depeg_severity * 100:.2f}%)")
        logger.info(f"")
        logger.info(f"METADATA:")
        logger.info(f"  Events Aggregated: {snapshot.num_events_aggregated}")
        logger.info(f"  Sources:           {', '.join(snapshot.sources_included)}")
        logger.info(f"{'-' * 70}")

        # Check if should attest
        should_attest = tcs_calculator.should_attest(snapshot.temporal_confidence)
        logger.info(f"\nAttestation Decision: {'✓ ATTEST (tier2+)' if should_attest else '✗ DO NOT ATTEST (low confidence)'}")

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("DEMO COMPLETE")
    logger.info("=" * 70)
    logger.info("\nLayer 1 Capabilities Demonstrated:")
    logger.info("  ✓ Multi-source price data ingestion (CoinGecko)")
    logger.info("  ✓ Data quality pipeline (normalization, deduplication, outlier detection)")
    logger.info("  ✓ Temporal Confidence Score (TCS) calculation")
    logger.info("  ✓ Window state machine (OPEN → PROVISIONAL → FINAL)")
    logger.info("  ✓ Cross-source aggregation with confidence metrics")
    logger.info("  ✓ Depeg detection and alerting")
    logger.info("  ✓ Attestation decision logic")
    logger.info("\nNext Steps:")
    logger.info("  → Add more data sources (liquidity, supply, sentiment)")
    logger.info("  → Implement blockchain finality tracking")
    logger.info("  → Connect to real-time event streams")
    logger.info("  → Progress to Layer 2 (Multi-Coin Monitoring)")


async def demo_continuous_monitoring():
    """
    Demo: Continuous monitoring with automatic window rotation.

    Runs for 3 minutes, fetching prices every 30 seconds and rotating windows.
    """
    logger.info("=" * 70)
    logger.info("LAYER 1 DEMO: Continuous Monitoring (3 minutes)")
    logger.info("=" * 70)

    window_manager = WindowManager(window_size_sec=60)
    coins = ["USDC", "USDT", "DAI"]
    chain = "ethereum"

    # Run for 3 minutes
    duration = 180  # seconds
    fetch_interval = 30  # seconds
    start_time = datetime.utcnow()

    iteration = 0

    while (datetime.utcnow() - start_time).total_seconds() < duration:
        iteration += 1
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Iteration {iteration} - {datetime.utcnow().isoformat()}")
        logger.info(f"{'=' * 70}")

        # Fetch prices
        events = await price_source.fetch_prices_batch(coins, chain=chain)

        if events:
            # Quality pipeline
            events = quality_pipeline.process_events(events)

            # TCS calculation
            for event in events:
                tcs_calculator.update_event_tcs(event)

            # Add to window
            for event in events:
                window_manager.add_event(event)

            logger.info(f"✓ Processed {len(events)} events")

            # Check for window transitions
            current_window = window_manager.current_window
            if current_window:
                logger.info(
                    f"  Window: {current_window.window_id} | "
                    f"State: {current_window.state.value} | "
                    f"Events: {len(current_window.events)}"
                )

        # Wait for next fetch
        await asyncio.sleep(fetch_interval)

    logger.info("\n" + "=" * 70)
    logger.info("CONTINUOUS MONITORING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total iterations: {iteration}")
    logger.info(f"Total windows: {len(window_manager.windows)}")


if __name__ == "__main__":
    # Run single window demo
    asyncio.run(demo_single_window())

    # Uncomment to run continuous monitoring demo:
    # asyncio.run(demo_continuous_monitoring())
