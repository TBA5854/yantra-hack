"""
Unified Data Collection Orchestrator

Coordinates all data sources for multi-chain stablecoin monitoring:
- Price data (CoinGecko)
- Liquidity data (Uniswap V3 / mock)
- Supply events (Web3 on-chain)
- Volatility (calculated)
- Sentiment (Twitter/Reddit / mock)

Runs all sources in parallel and emits unified RiskEvents.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, AsyncIterator
from collections import defaultdict

from src.common.config import Config
from src.common.schema import RiskEvent
from src.data_collection.sources.price_source import price_source
from src.data_collection.sources.liquidity_source import liquidity_source
from src.data_collection.sources.supply_source import MultiChainSupplyMonitor
from src.data_collection.sources.volatility_source import volatility_source
from src.data_collection.sources.sentiment_source import sentiment_source
from src.data_collection.quality.pipeline import DataQualityPipeline

logger = logging.getLogger(__name__)


class DataCollectionOrchestrator:
    """
    Orchestrates all data collection sources across multiple chains and coins.

    Features:
    - Parallel data fetching from all sources
    - Quality pipeline integration
    - Real-time and batch modes
    - Automatic retry and error handling
    """

    def __init__(
        self,
        coins: List[str] = None,
        chains: List[str] = None,
        enable_quality_pipeline: bool = True
    ):
        """
        Initialize data collection orchestrator.

        Args:
            coins: List of coins to monitor (defaults to all configured)
            chains: List of chains to monitor (defaults to all configured)
            enable_quality_pipeline: Whether to run quality checks
        """
        self.coins = coins or list(Config.COINS.keys())
        self.chains = chains or ["ethereum", "arbitrum"]
        self.enable_quality_pipeline = enable_quality_pipeline

        # Initialize quality pipeline
        if self.enable_quality_pipeline:
            self.quality_pipeline = DataQualityPipeline()
        else:
            self.quality_pipeline = None

        # Initialize supply monitor
        self.supply_monitor = MultiChainSupplyMonitor(
            coins=self.coins,
            chains=self.chains,
            mode="mock"  # TODO: Switch to "live" when ready
        )

        logger.info(f"Initialized orchestrator for {len(self.coins)} coins on {len(self.chains)} chains")

    async def collect_all_sources_once(
        self,
        coin: str,
        chain: str
    ) -> List[RiskEvent]:
        """
        Collect data from all sources for a single coin/chain pair (one snapshot).

        Args:
            coin: Coin symbol (e.g., 'USDC')
            chain: Chain name (e.g., 'ethereum')

        Returns:
            List of RiskEvents from all sources
        """
        events = []

        # Collect from each source in parallel
        tasks = [
            price_source.fetch_price(coin, chain),
            liquidity_source.fetch_liquidity(coin, chain),
            volatility_source.calculate_volatility(coin, chain),
            sentiment_source.fetch_sentiment(coin, chain)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Source failed for {coin} on {chain}: {result}")
                continue
            if result:
                events.append(result)

        # Note: Supply events are fetched separately via block monitoring
        # (they are event-driven, not polled)

        return events

    async def collect_all_coins_chains_once(self) -> List[RiskEvent]:
        """
        Collect data from all sources for all configured coin/chain pairs.

        Returns:
            List of RiskEvents from all coins/chains/sources
        """
        logger.info("=" * 70)
        logger.info("COLLECTING DATA FROM ALL SOURCES")
        logger.info("=" * 70)
        logger.info(f"Coins: {', '.join(self.coins)}")
        logger.info(f"Chains: {', '.join(self.chains)}")

        all_events = []

        # Collect for each coin/chain combination
        for coin in self.coins:
            for chain in self.chains:
                logger.info(f"\n📊 Fetching {coin} on {chain}...")

                events = await self.collect_all_sources_once(coin, chain)

                if events:
                    logger.info(f"  ✓ Collected {len(events)} events from {len(events)} sources")
                    all_events.extend(events)
                else:
                    logger.warning(f"  ⚠️ No data collected for {coin} on {chain}")

        # Apply quality pipeline if enabled
        if self.quality_pipeline and all_events:
            logger.info(f"\n🔍 Applying quality pipeline to {len(all_events)} events...")
            all_events = self.quality_pipeline.process_events(all_events)
            logger.info(f"  ✓ {len(all_events)} events passed quality checks")

        logger.info(f"\n" + "=" * 70)
        logger.info(f"✅ COLLECTION COMPLETE: {len(all_events)} total events")
        logger.info("=" * 70)

        return all_events

    async def stream_all_sources(
        self,
        poll_interval: int = 60
    ) -> AsyncIterator[RiskEvent]:
        """
        Continuously stream data from all sources.

        Args:
            poll_interval: Seconds between collection cycles

        Yields:
            RiskEvents as they are collected
        """
        logger.info("=" * 70)
        logger.info("STARTING CONTINUOUS DATA COLLECTION STREAM")
        logger.info("=" * 70)
        logger.info(f"Poll interval: {poll_interval}s")
        logger.info(f"Coins: {', '.join(self.coins)}")
        logger.info(f"Chains: {', '.join(self.chains)}")

        iteration = 0

        while True:
            try:
                iteration += 1
                logger.info(f"\n📡 Collection iteration #{iteration} at {datetime.now(timezone.utc).isoformat()}")

                # Collect all data
                events = await self.collect_all_coins_chains_once()

                # Yield each event
                for event in events:
                    yield event

                # Wait before next collection
                logger.info(f"\n⏳ Sleeping for {poll_interval}s...")
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error in collection stream: {e}")
                await asyncio.sleep(poll_interval)

    def summarize_events(self, events: List[RiskEvent]) -> Dict:
        """
        Generate summary statistics for collected events.

        Args:
            events: List of RiskEvents

        Returns:
            Dict with summary statistics
        """
        summary = {
            "total_events": len(events),
            "by_coin": defaultdict(int),
            "by_chain": defaultdict(int),
            "by_source": defaultdict(int),
            "avg_price": {},
            "avg_liquidity": {},
            "supply_changes": {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        for event in events:
            summary["by_coin"][event.coin] += 1
            summary["by_chain"][event.chain] += 1
            summary["by_source"][event.source] += 1

            # Aggregate price data
            if event.price is not None:
                key = f"{event.coin}_{event.chain}"
                if key not in summary["avg_price"]:
                    summary["avg_price"][key] = []
                summary["avg_price"][key].append(event.price)

            # Aggregate liquidity data
            if event.liquidity_depth is not None:
                key = f"{event.coin}_{event.chain}"
                if key not in summary["avg_liquidity"]:
                    summary["avg_liquidity"][key] = []
                summary["avg_liquidity"][key].append(event.liquidity_depth)

            # Aggregate supply changes
            if event.net_supply_change is not None:
                key = f"{event.coin}_{event.chain}"
                if key not in summary["supply_changes"]:
                    summary["supply_changes"][key] = 0
                summary["supply_changes"][key] += event.net_supply_change

        # Calculate averages
        for key, prices in summary["avg_price"].items():
            summary["avg_price"][key] = sum(prices) / len(prices) if prices else None

        for key, liquidity in summary["avg_liquidity"].items():
            summary["avg_liquidity"][key] = sum(liquidity) / len(liquidity) if liquidity else None

        # Convert defaultdicts to regular dicts
        summary["by_coin"] = dict(summary["by_coin"])
        summary["by_chain"] = dict(summary["by_chain"])
        summary["by_source"] = dict(summary["by_source"])

        return summary

    def print_summary(self, summary: Dict):
        """Print formatted summary to logger."""
        logger.info("\n" + "=" * 70)
        logger.info("COLLECTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total events: {summary['total_events']}")

        logger.info(f"\nBy coin:")
        for coin, count in summary["by_coin"].items():
            logger.info(f"  {coin}: {count} events")

        logger.info(f"\nBy chain:")
        for chain, count in summary["by_chain"].items():
            logger.info(f"  {chain}: {count} events")

        logger.info(f"\nBy source:")
        for source, count in summary["by_source"].items():
            logger.info(f"  {source}: {count} events")

        if summary["avg_price"]:
            logger.info(f"\nAverage prices:")
            for key, price in summary["avg_price"].items():
                if price:
                    logger.info(f"  {key}: ${price:.6f}")

        if summary["avg_liquidity"]:
            logger.info(f"\nAverage liquidity:")
            for key, liq in summary["avg_liquidity"].items():
                if liq:
                    logger.info(f"  {key}: ${liq:,.2f}")

        if summary["supply_changes"]:
            logger.info(f"\nNet supply changes:")
            for key, change in summary["supply_changes"].items():
                logger.info(f"  {key}: {change:+,.2f}")


async def demo_orchestrator():
    """Demo: Run data collection orchestrator."""
    logger.info("=" * 70)
    logger.info("DATA COLLECTION ORCHESTRATOR DEMO")
    logger.info("=" * 70)

    # Create orchestrator for USDC and USDT on Ethereum and Arbitrum
    orchestrator = DataCollectionOrchestrator(
        coins=["USDC", "USDT"],
        chains=["ethereum", "arbitrum"],
        enable_quality_pipeline=True
    )

    # Collect data once
    logger.info("\n🔄 Running one-time collection...")
    events = await orchestrator.collect_all_coins_chains_once()

    # Generate and print summary
    summary = orchestrator.summarize_events(events)
    orchestrator.print_summary(summary)

    # Demo streaming (just 2 iterations)
    logger.info("\n\n📡 Starting streaming demo (2 iterations, 5s interval)...")
    iteration = 0
    async for event in orchestrator.stream_all_sources(poll_interval=5):
        logger.info(
            f"  Stream event {iteration}: {event.coin} on {event.chain} "
            f"from {event.source} - price: ${event.price:.6f if event.price else 'N/A'}"
        )
        iteration += 1
        if iteration >= 8:  # 2 iterations * 4 sources = 8 events
            break

    logger.info("\n" + "=" * 70)
    logger.info("✅ DEMO COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(demo_orchestrator())
