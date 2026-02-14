#!/usr/bin/env python3
"""
Stream stablecoin data collection events to CSV file.

Collects data at regular intervals and appends to CSV.
"""
import asyncio
import csv
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


def setup_csv_file(filename: str) -> tuple[Path, bool]:
    """
    Setup CSV file with headers if it doesn't exist.
    
    Returns:
        (filepath, is_new_file)
    """
    filepath = Path(filename)
    is_new = not filepath.exists()
    
    if is_new:
        # Create file with headers
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'coin',
                'chain',
                'source',
                'price',
                'volume_24h',
                'market_cap',
                'liquidity_depth',
                'net_supply_change',
                'market_volatility',
                'sentiment_score',
                'temporal_confidence',
                'finality_tier',
                'block_number',
                'tx_hash'
            ])
        logger.info(f"✅ Created new CSV file: {filepath}")
    else:
        logger.info(f"📝 Appending to existing CSV file: {filepath}")
    
    return filepath, is_new


def write_events_to_csv(filepath: Path, events: list):
    """Write events to CSV file."""
    if not events:
        return
    
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        for event in events:
            writer.writerow([
                event.timestamp.isoformat() if event.timestamp else '',
                event.coin,
                event.chain,
                event.source,
                f"{event.price:.6f}" if event.price is not None else '',
                f"{event.volume_24h:.2f}" if event.volume_24h is not None else '',
                f"{event.market_cap:.2f}" if event.market_cap is not None else '',
                f"{event.liquidity_depth:.2f}" if event.liquidity_depth is not None else '',
                f"{event.net_supply_change:.2f}" if event.net_supply_change is not None else '',
                f"{event.market_volatility:.6f}" if event.market_volatility is not None else '',
                f"{event.sentiment_score:.3f}" if event.sentiment_score is not None else '',
                f"{event.temporal_confidence:.3f}" if hasattr(event, 'temporal_confidence') else '',
                event.finality_tier if hasattr(event, 'finality_tier') else '',
                event.block_number if event.block_number else '',
                event.tx_hash if event.tx_hash else ''
            ])


async def stream_to_csv(
    filename: str = "stablecoin_events.csv",
    coins: list = None,
    chains: list = None,
    poll_interval: int = 60,
    max_cycles: int = None
):
    """
    Stream stablecoin data to CSV file.
    
    Args:
        filename: CSV filename to write to
        coins: List of coins to monitor (default: ["USDC"])
        chains: List of chains to monitor (default: ["ethereum"])
        poll_interval: Seconds between collection cycles
        max_cycles: Maximum number of cycles (None = infinite)
    """
    coins = coins or ["USDC"]
    chains = chains or ["ethereum"]
    
    logger.info("=" * 70)
    logger.info("🚀 Starting Stablecoin Data Stream to CSV")
    logger.info("=" * 70)
    logger.info(f"📊 Monitoring: {', '.join(coins)} on {', '.join(chains)}")
    logger.info(f"⏱️  Poll interval: {poll_interval} seconds")
    logger.info(f"📁 Output file: {filename}")
    if max_cycles:
        logger.info(f"🔄 Max cycles: {max_cycles}")
    else:
        logger.info(f"🔄 Running continuously (Ctrl+C to stop)")
    logger.info("=" * 70)
    logger.info("")
    
    # Setup CSV file
    filepath, is_new = setup_csv_file(filename)
    
    # Initialize orchestrator
    orchestrator = DataCollectionOrchestrator(
        coins=coins,
        chains=chains,
        enable_quality_pipeline=True
    )
    
    cycle = 0
    total_events = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"📡 Collection Cycle #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Collect data
            events = await orchestrator.collect_all_coins_chains_once()
            
            if events:
                # Write to CSV
                write_events_to_csv(filepath, events)
                total_events += len(events)
                
                logger.info(f"✅ Collected {len(events)} events (total: {total_events})")
                
                # Show summary
                summary = orchestrator.summarize_events(events)
                logger.info(f"   Prices: {summary.get('avg_prices', {})}")
            else:
                logger.warning(f"⚠️  No events collected in cycle #{cycle}")
            
            # Check if we've reached max cycles
            if max_cycles and cycle >= max_cycles:
                logger.info(f"🏁 Reached max cycles ({max_cycles}). Stopping.")
                break
            
            # Wait before next cycle
            logger.info(f"⏳ Waiting {poll_interval} seconds until next cycle...")
            logger.info("")
            await asyncio.sleep(poll_interval)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("⏹️  Stream stopped by user (Ctrl+C)")
    finally:
        logger.info("=" * 70)
        logger.info(f"📊 FINAL STATISTICS")
        logger.info("=" * 70)
        logger.info(f"Total cycles: {cycle}")
        logger.info(f"Total events collected: {total_events}")
        logger.info(f"CSV file: {filepath.absolute()}")
        logger.info(f"File size: {filepath.stat().st_size:,} bytes")
        logger.info("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Stream stablecoin data to CSV")
    parser.add_argument(
        "--output", "-o",
        default=f"stablecoin_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output CSV filename"
    )
    parser.add_argument(
        "--coins",
        nargs="+",
        default=["USDC"],
        help="Coins to monitor (default: USDC)"
    )
    parser.add_argument(
        "--chains",
        nargs="+",
        default=["ethereum"],
        help="Chains to monitor (default: ethereum)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="Poll interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--cycles", "-c",
        type=int,
        default=None,
        help="Maximum number of cycles (default: infinite)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(stream_to_csv(
        filename=args.output,
        coins=args.coins,
        chains=args.chains,
        poll_interval=args.interval,
        max_cycles=args.cycles
    ))
