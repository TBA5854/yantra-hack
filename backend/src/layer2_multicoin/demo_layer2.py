"""
Layer 2 Demo: Multi-Coin Monitoring

Demonstrates cross-coin analysis capabilities:
1. Coin registry management
2. Cross-coin comparison
3. Contagion risk detection
4. Market stress assessment
5. Divergence detection
"""

import asyncio
import logging
from datetime import datetime
import json

from src.common.config import config
from src.layer1_core.sources.price_source import price_source
from src.layer1_core.sources.liquidity_source import liquidity_source
from src.layer1_core.sources.volatility_source import volatility_source
from src.layer1_core.sources.sentiment_source import sentiment_source
from src.layer1_core.quality.pipeline import quality_pipeline
from src.layer1_core.tcs.calculator import tcs_calculator
from src.layer2_multicoin.coin_registry.registry import coin_registry
from src.layer2_multicoin.aggregation.cross_coin_analyzer import cross_coin_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def collect_all_data(coins: list, chain: str = "ethereum"):
    """Collect data from all 5 sources for multiple coins."""
    all_events = []

    # Price
    price_events = await price_source.fetch_prices_batch(coins, chain=chain)
    all_events.extend(price_events)

    # Liquidity
    liquidity_events = await liquidity_source.fetch_liquidity_batch(coins, chain=chain)
    all_events.extend(liquidity_events)

    # Volatility
    volatility_events = await volatility_source.calculate_volatility_batch(coins, chain=chain)
    all_events.extend(volatility_events)

    # Sentiment
    sentiment_events = await sentiment_source.fetch_sentiment_batch(coins, chain=chain)
    all_events.extend(sentiment_events)

    # Supply (mock)
    import random
    from src.common.schema import RiskEvent
    for coin in coins:
        event = RiskEvent(
            timestamp=datetime.utcnow(),
            coin=coin,
            chain=chain,
            source="supply_tracker_mock",
            net_supply_change=random.uniform(-1_000_000, 1_000_000),
            block_number=None,
            tx_hash=None
        )
        all_events.append(event)

    return all_events


async def demo_multi_coin_analysis():
    """
    Demo: Multi-coin monitoring and cross-coin analysis.
    """
    logger.info("=" * 70)
    logger.info("LAYER 2 DEMO: Multi-Coin Monitoring & Cross-Coin Analysis")
    logger.info("=" * 70)

    coins = ["USDC", "USDT", "DAI"]
    chain = "ethereum"

    # Stage 1: Coin Registry Overview
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 1: Coin Registry Overview")
    logger.info("=" * 70)

    summary = coin_registry.get_registry_summary()
    logger.info(f"Total coins:      {summary['total_coins']}")
    logger.info(f"Active coins:     {summary['active_coins']}")
    logger.info(f"Chains supported: {', '.join(summary['chains_supported'])}")

    # Show coin details
    logger.info(f"\nRegistered Coins:")
    for coin in coins:
        config_obj = coin_registry.get_coin_config(coin)
        if config_obj:
            logger.info(f"  {coin:6s} - {config_obj.name}")
            logger.info(f"          Chains: {', '.join(config_obj.chains)}")
            logger.info(f"          Depeg threshold: {config_obj.depeg_threshold*100:.1f}%")

    # Stage 2: Collect Data for All Coins
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 2: Data Collection (All 5 Sources)")
    logger.info("=" * 70)

    all_events = await collect_all_data(coins, chain)
    logger.info(f"✓ Collected {len(all_events)} events from all sources")

    # Quality pipeline
    all_events = quality_pipeline.process_events(all_events)
    logger.info(f"✓ Quality pipeline processed {len(all_events)} events")

    # Calculate TCS
    for event in all_events:
        tcs_calculator.update_event_tcs(event)

    # Stage 3: Update Coin Registry with Latest Data
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 3: Update Coin Status in Registry")
    logger.info("=" * 70)

    # Group events by coin
    events_by_coin = {coin: [] for coin in coins}
    for event in all_events:
        if event.coin in events_by_coin:
            events_by_coin[event.coin].append(event)

    # Update registry for each coin
    for coin, events in events_by_coin.items():
        # Extract metrics
        prices = [e.price for e in events if e.price is not None]
        liquidities = [e.liquidity_depth for e in events if e.liquidity_depth is not None]
        volumes = [e.volume for e in events if e.volume is not None]
        volatilities = [e.market_volatility for e in events if e.market_volatility is not None]
        sentiments = [e.sentiment_score for e in events if e.sentiment_score is not None]
        tcs_scores = [e.temporal_confidence for e in events]

        # Aggregate
        avg_price = sum(prices) / len(prices) if prices else None
        total_liquidity = sum(liquidities) if liquidities else None
        daily_volume = sum(volumes) if volumes else None
        avg_volatility = sum(volatilities) / len(volatilities) if volatilities else None
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else None
        avg_tcs = sum(tcs_scores) / len(tcs_scores) if tcs_scores else 0.0

        # Check depeg
        coin_config = coin_registry.get_coin_config(coin)
        is_depegged = False
        depeg_severity = 0.0
        if avg_price and coin_config:
            depeg_severity = abs(avg_price - 1.0)
            is_depegged = depeg_severity >= coin_config.depeg_threshold

        # Update registry
        coin_registry.update_coin_status(
            coin,
            current_price=avg_price,
            total_liquidity=total_liquidity,
            daily_volume=daily_volume,
            market_volatility=avg_volatility,
            sentiment_score=avg_sentiment,
            temporal_confidence=avg_tcs,
            is_depegged=is_depegged,
            depeg_severity=depeg_severity,
            sources_available=set(e.source for e in events),
            chains_available=set(e.chain for e in events)
        )

        logger.info(f"✓ Updated {coin}: price=${avg_price:.6f}, TCS={avg_tcs:.3f}, depegged={is_depegged}")

    # Stage 4: Cross-Coin Comparison
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 4: Cross-Coin Comparison")
    logger.info("=" * 70)

    comparisons = cross_coin_analyzer.compare_all_pairs()
    logger.info(f"✓ Compared {len(comparisons)} coin pairs\n")

    for comparison in comparisons:
        logger.info(f"{comparison.coin1} vs {comparison.coin2}:")
        logger.info(f"  Price difference:  ${comparison.price_diff:.6f}")
        logger.info(f"  Health diff:       {comparison.health_score_diff:.3f}")
        logger.info(f"  TCS diff:          {comparison.tcs_diff:.3f}")
        if comparison.is_diverging:
            logger.warning(f"  ⚠️ DIVERGING:      {comparison.divergence_severity*100:.2f}%")
        else:
            logger.info(f"  Diverging:         No")

    # Stage 5: Contagion Risk Detection
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 5: Contagion Risk Detection")
    logger.info("=" * 70)

    is_contagion, affected_coins = cross_coin_analyzer.detect_contagion_risk()

    if is_contagion:
        logger.error(f"🚨 CONTAGION RISK DETECTED!")
        logger.error(f"   Affected coins: {', '.join(affected_coins)}")
    else:
        logger.info(f"✓ No contagion risk detected")
        if affected_coins:
            logger.info(f"  Depegged coins: {', '.join(affected_coins)} (below threshold)")
        else:
            logger.info(f"  All coins maintaining peg")

    # Stage 6: Market Stress Assessment
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 6: Market-Wide Stress Assessment")
    logger.info("=" * 70)

    stress_signal = cross_coin_analyzer.assess_market_stress()

    logger.info(f"Market Stress Level:    {stress_signal.severity.upper()}")
    logger.info(f"Severity Score:         {stress_signal.severity_score:.3f} / 1.0")
    logger.info(f"")
    logger.info(f"Contributing Factors:")
    logger.info(f"  Depegged coins:       {stress_signal.depegged_count}")
    logger.info(f"  Avg depeg severity:   {stress_signal.avg_depeg_severity*100:.2f}%")
    logger.info(f"  Avg health score:     {stress_signal.avg_health_score:.3f}")
    logger.info(f"  Avg TCS:              {stress_signal.avg_tcs:.3f}")
    if stress_signal.avg_sentiment is not None:
        sentiment_label = (
            "POSITIVE" if stress_signal.avg_sentiment > 0.2 else
            "NEUTRAL" if stress_signal.avg_sentiment > -0.2 else
            "NEGATIVE"
        )
        logger.info(f"  Avg sentiment:        {stress_signal.avg_sentiment:.3f} ({sentiment_label})")
    logger.info(f"  Total liquidity:      ${stress_signal.total_liquidity:,.0f}" if stress_signal.total_liquidity else "  Total liquidity:      N/A")
    logger.info(f"  Liquidity crisis:     {stress_signal.liquidity_crisis}")

    # Stage 7: Individual Coin Health Scores
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 7: Individual Coin Health Scores")
    logger.info("=" * 70)

    logger.info(f"{'Coin':<8} {'Price':<12} {'Health':<10} {'TCS':<8} {'Status':<12}")
    logger.info("-" * 70)

    for coin in coins:
        status = coin_registry.get_coin_status(coin)
        if not status:
            continue

        price_str = f"${status.current_price:.6f}" if status.current_price else "N/A"
        health_str = f"{status.health_score:.3f}"
        tcs_str = f"{status.temporal_confidence:.3f}"

        # Status label
        if status.is_depegged:
            status_label = "⚠️ DEPEGGED"
        elif status.health_score < 0.5:
            status_label = "⚠️ AT RISK"
        elif status.health_score < 0.8:
            status_label = "⚠️ MODERATE"
        else:
            status_label = "✓ HEALTHY"

        logger.info(f"{coin:<8} {price_str:<12} {health_str:<10} {tcs_str:<8} {status_label:<12}")

    # Stage 8: Market Overview (JSON)
    logger.info("\n" + "=" * 70)
    logger.info("STAGE 8: Complete Market Overview (JSON)")
    logger.info("=" * 70)

    overview = cross_coin_analyzer.get_market_overview()
    logger.info(json.dumps(overview, indent=2, default=str))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("DEMO COMPLETE - LAYER 2 MULTI-COIN MONITORING")
    logger.info("=" * 70)
    logger.info("\nLayer 2 Capabilities Demonstrated:")
    logger.info("  ✓ Coin registry management")
    logger.info("  ✓ Multi-coin data collection (5 sources × 3 coins)")
    logger.info("  ✓ Cross-coin price comparison")
    logger.info("  ✓ Divergence detection")
    logger.info("  ✓ Contagion risk assessment")
    logger.info("  ✓ Market-wide stress signals")
    logger.info("  ✓ Individual coin health scores")
    logger.info("  ✓ JSON API for market overview")
    logger.info("\nKey Achievement:")
    logger.info(f"  🎉 Successfully monitored {len(coins)} stablecoins simultaneously")
    logger.info(f"  🎉 Market stress: {stress_signal.severity.upper()} (score={stress_signal.severity_score:.2f})")
    logger.info(f"  🎉 Contagion risk: {'DETECTED' if is_contagion else 'NOT DETECTED'}")
    logger.info("\nNext Steps:")
    logger.info("  → Progress to Layer 3 (Cross-Chain Synchronization)")
    logger.info("  → Implement historical trend analysis")
    logger.info("  → Build real-time alerting system")
    logger.info("  → Create dashboard visualization")


if __name__ == "__main__":
    asyncio.run(demo_multi_coin_analysis())
