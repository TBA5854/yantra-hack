#!/usr/bin/env python3
"""
Quick 10-second demo of live stablecoin data collection
"""
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_collection.orchestrator import DataCollectionOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def run_10sec_demo():
    """Run data collection for 10 seconds and log results."""
    
    logger.info("=" * 70)
    logger.info("🚀 Starting 10-Second Stablecoin Data Collection Demo")
    logger.info("=" * 70)
    
    # Initialize orchestrator for USDC on Ethereum
    orchestrator = DataCollectionOrchestrator(
        coins=["USDC"],
        chains=["ethereum"],
        enable_quality_pipeline=True
    )
    
    logger.info(f"⚙️  Configured for: USDC on Ethereum")
    logger.info(f"⏰ Start time: {datetime.now()}")
    logger.info(f"⏱️  Duration: 10 seconds")
    logger.info("")
    
    # Collect data once
    logger.info("📡 Collecting data from all sources...")
    events = await orchestrator.collect_all_coins_chains_once()
    
    if events:
        logger.info(f"✅ Collected {len(events)} events")
        logger.info("")
        
        # Print summary
        summary = orchestrator.summarize_events(events)
        orchestrator.print_summary(summary)
        
        # Print detailed event info
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 DETAILED EVENT DATA")
        logger.info("=" * 70)
        
        for i, event in enumerate(events, 1):
            logger.info(f"\n🔹 Event {i}:")
            logger.info(f"   Coin: {event.coin}")
            logger.info(f"   Chain: {event.chain}")
            logger.info(f"   Source: {event.source}")
            logger.info(f"   Timestamp: {event.timestamp}")
            
            if event.price is not None:
                logger.info(f"   Price: ${event.price:.6f}")
            if event.volume_24h is not None:
                logger.info(f"   Volume 24h: ${event.volume_24h:,.0f}")
            if event.market_cap is not None:
                logger.info(f"   Market Cap: ${event.market_cap:,.0f}")
            if event.liquidity_depth is not None:
                logger.info(f"   Liquidity Depth: ${event.liquidity_depth:,.0f}")
            if event.net_supply_change is not None:
                logger.info(f"   Supply Change: {event.net_supply_change:+,.0f}")
            if event.market_volatility is not None:
                logger.info(f"   Volatility: {event.market_volatility:.4f}")
            if event.sentiment_score is not None:
                logger.info(f"   Sentiment: {event.sentiment_score:+.2f}")
            
            # TCS info
            if hasattr(event, 'temporal_confidence'):
                logger.info(f"   TCS: {event.temporal_confidence:.3f}")
            if hasattr(event, 'finality_tier'):
                logger.info(f"   Finality: {event.finality_tier}")
    else:
        logger.warning("⚠️  No events collected")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"✅ Demo completed at: {datetime.now()}")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_10sec_demo())
