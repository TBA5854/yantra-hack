"""
Stablecoin Risk Monitoring Pipeline - Main Driver

Orchestrates the entire detailed monitoring pipeline:
1. Data Collection (Price, Liquidity, Volatility, Sentiment)
2. Quality Assurance (Validation, Deduplication)
3. Window Aggregation (Time-windowed risk snapshots)
4. Cross-Chain Synchronization (TCS-weighted aggregation)
5. Blockchain Monitoring (Reorg detection & recovery)
"""

import asyncio
import logging
import signal
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Set

# Configuration & Schema
from src.common.config import config
from src.common.schema import RiskEvent, WindowState

# Feature Modules
from src.confidence.tcs_calculator import tcs_calculator
from src.confidence.finality_tracker import finality_registry
from src.data_collection.sources.price_source import price_source
from src.data_collection.sources.liquidity_source import liquidity_source
from src.data_collection.sources.volatility_source import volatility_source
from src.data_collection.sources.sentiment_source import sentiment_source
from src.data_collection.quality.pipeline import quality_pipeline
from src.aggregation.window_manager import WindowManager
from src.aggregation.cross_chain_aggregator import cross_chain_aggregator
from src.blockchain.block_monitor import (
    EthereumBlockMonitor,
    ArbitrumBlockMonitor,
    SolanaBlockMonitor
)
from src.blockchain.reorg_handler import reorg_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PipelineDriver")


class RiskMonitoringPipeline:
    """
    Main orchestration driver for the stablecoin risk monitoring system.
    """

    def __init__(self, coins: List[str], chains: List[str]):
        self.coins = coins
        self.chains = chains
        self.is_running = False
        
        # Components
        self.window_manager = WindowManager(window_size_sec=config.WINDOW_CONFIG["window_size_sec"])
        self.block_monitors = {}
        
        # Initialize block monitors for requested chains
        if "ethereum" in chains:
            self.block_monitors["ethereum"] = EthereumBlockMonitor(
                "ethereum", finality_registry.get_tracker("ethereum")
            )
        if "arbitrum" in chains:
            self.block_monitors["arbitrum"] = ArbitrumBlockMonitor(
                "arbitrum", finality_registry.get_tracker("arbitrum")
            )
        if "solana" in chains:
            self.block_monitors["solana"] = SolanaBlockMonitor(
                "solana", finality_registry.get_tracker("solana")
            )

    async def start(self):
        """Start the pipeline and all sub-components."""
        self.is_running = True
        logger.info(f"🚀 Starting Risk Monitoring Pipeline for {self.coins} on {self.chains}")

        # 1. Start Block Monitors (Background Tasks)
        monitor_tasks = []
        for chain, monitor in self.block_monitors.items():
            monitor_tasks.append(asyncio.create_task(monitor.start_monitoring()))
            
        # 2. Start Data Collection Loops
        collection_tasks = [
            asyncio.create_task(self._run_price_collection()),
            asyncio.create_task(self._run_liquidity_collection()),
            asyncio.create_task(self._run_volatility_collection()),
            asyncio.create_task(self._run_sentiment_collection())
        ]

        # 3. Start Window State Machine
        window_task = asyncio.create_task(self.window_manager.run_state_machine())

        # 4. Start Cross-Chain Aggregation Loop
        aggregation_task = asyncio.create_task(self._run_cross_chain_aggregation())

        # 5. Main Event Loop (Keep alive and monitor health)
        try:
            await asyncio.gather(
                *monitor_tasks,
                *collection_tasks,
                window_task,
                aggregation_task
            )
        except asyncio.CancelledError:
            logger.info("Pipeline tasks cancelled, shutting down...")
        except Exception as e:
            logger.critical(f"Critical pipeline failure: {e}", exc_info=True)
            self.stop()

    def stop(self):
        """Signal pipeline to stop."""
        logger.info("Stopping pipeline...")
        self.is_running = False
        
        # Stop block monitors
        for monitor in self.block_monitors.values():
            asyncio.create_task(monitor.stop_monitoring())

    async def _process_event(self, event: RiskEvent):
        """Process a raw event through quality pipeline and into window manager."""
        # 1. Validate & Deduplicate
        # pipeline processing returns a list of approved events (usually 0 or 1)
        processed_events = quality_pipeline.process_events([event])
        
        if not processed_events:
            return

        # 2. Add to Window Manager (Temporal Aggregation)
        for valid_event in processed_events:
            self.window_manager.add_event(valid_event)

            # 3. Register with Block Monitor (for Reorg Protection)
            if valid_event.chain in self.block_monitors:
                self.block_monitors[valid_event.chain].register_event(valid_event)

    async def _run_price_collection(self):
        """Poll price data sources."""
        logger.info("Starting Price Collection")
        while self.is_running:
            try:
                for coin in self.coins:
                    # Fetch from all chains
                    for chain in self.chains:
                        event = await price_source.fetch_price(coin, chain)
                        if event:
                            await self._process_event(event)
            except Exception as e:
                logger.error(f"Price collection error: {e}")
            
            await asyncio.sleep(config.SOURCE_CONFIG["price_interval_sec"])

    async def _run_liquidity_collection(self):
        """Poll liquidity data sources."""
        logger.info("Starting Liquidity Collection")
        while self.is_running:
            try:
                for coin in self.coins:
                    # Fetch from all chains
                    for chain in self.chains:
                        event = await liquidity_source.fetch_liquidity(coin, chain)
                        if event:
                            await self._process_event(event)
            except Exception as e:
                logger.error(f"Liquidity collection error: {e}")
            
            await asyncio.sleep(config.SOURCE_CONFIG["liquidity_interval_sec"])

    async def _run_volatility_collection(self):
        """Poll volatility data sources."""
        logger.info("Starting Volatility Collection")
        while self.is_running:
            try:
                for coin in self.coins:
                    # Volatility is often calculated per chain or globally
                    # Here we calculate for primary chain (Ethereum) or all
                    for chain in self.chains:
                        event = await volatility_source.calculate_volatility(coin, chain)
                        if event:
                            await self._process_event(event)
            except Exception as e:
                logger.error(f"Volatility collection error: {e}")
            
            await asyncio.sleep(config.SOURCE_CONFIG["volatility_interval_sec"])

    async def _run_sentiment_collection(self):
        """Poll sentiment data sources."""
        logger.info("Starting Sentiment Collection")
        while self.is_running:
            try:
                for coin in self.coins:
                    # Sentiment is usually global, but can be chain-specific
                    event = await sentiment_source.fetch_sentiment(coin, "ethereum")
                    if event:
                        await self._process_event(event)
            except Exception as e:
                logger.error(f"Sentiment collection error: {e}")
            
            await asyncio.sleep(config.SOURCE_CONFIG["sentiment_interval_sec"])

    async def _run_cross_chain_aggregation(self):
        """Periodic cross-chain aggregation of finalized windows."""
        logger.info("Starting Cross-Chain Aggregation Loop")
        while self.is_running:
            try:
                # 1. Get finalized snapshots from Window Manager
                snapshots = self.window_manager.get_finalized_snapshots()
                
                # Group by Window ID and Coin
                grouped_snapshots = {} # (window_id, coin) -> {chain: [events]}
                
                # In a real impl, we'd query the raw events for these snapshots
                # For this driver, we assume WindowManager exposes a way to get events
                # Or we look at the snapshots themselves if they contained raw events
                # (Simplification for this driver: Just logging finalized windows)
                
                if snapshots:
                    logger.info(f"✅ Collected {len(snapshots)} finalized window snapshots")
                    # Here we would feed these into cross_chain_aggregator
                    
                    # Cleanup old windows
                    self.window_manager.cleanup_old_windows(max_age_hours=1)
                
            except Exception as e:
                logger.error(f"Aggregation loop error: {e}")
            
            await asyncio.sleep(10)


async def main():
    parser = argparse.ArgumentParser(description="Stablecoin Risk Monitoring Pipeline")
    parser.add_argument("--coins", type=str, default="USDC,USDT,DAI", help="Comma-separated list of coins")
    parser.add_argument("--chains", type=str, default="ethereum,arbitrum,solana", help="Comma-separated list of chains")
    parser.add_argument("--duration", type=int, default=0, help="Run duration in seconds (0 for infinite)")
    
    args = parser.parse_args()
    
    coins = [c.strip() for c in args.coins.split(",")]
    chains = [c.strip() for c in args.chains.split(",")]
    
    pipeline = RiskMonitoringPipeline(coins, chains)
    
    # Handle signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(pipeline)))
    
    driver_task = asyncio.create_task(pipeline.start())
    
    if args.duration > 0:
        logger.info(f"Running for {args.duration} seconds...")
        await asyncio.sleep(args.duration)
        await shutdown(pipeline)
    else:
        try:
            await driver_task
        except asyncio.CancelledError:
            pass

async def shutdown(pipeline):
    """Graceful shutdown sequence."""
    logger.info("🛑 Shutting down pipeline...")
    pipeline.stop()
    
    # Give tasks a moment to cancel
    await asyncio.sleep(1)
    
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Pipeline shutdown complete.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
