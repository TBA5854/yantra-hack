#!/usr/bin/env python3
"""
Generic cryptocurrency data collector for ML model training.

Collects price data for any coin supported by CoinGecko (BTC, ETH, etc.)
Bypasses stablecoin-specific features.
"""
import asyncio
import csv
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# CoinGecko coin ID mappings
COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDC": "usd-coin",
    "USDT": "tether",
    "DAI": "dai",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "SOL": "solana",
    "MATIC": "matic-network",
}


async def fetch_crypto_price(coin_symbol: str, api_key: str = None):
    """
    Fetch cryptocurrency price from CoinGecko.
    
    Args:
        coin_symbol: Crypto symbol (BTC, ETH, etc.)
        api_key: Optional CoinGecko API key
    
    Returns:
        Dict with price data
    """
    coin_id = COIN_IDS.get(coin_symbol.upper())
    if not coin_id:
        logger.error(f"Unknown coin: {coin_symbol}")
        return None
    
    # Use demo API
    base_url = "https://api.coingecko.com/api/v3"
    
    url = f"{base_url}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_last_updated_at": "true"
    }
    
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                data = await response.json()
        
        coin_data = data.get(coin_id, {})
        if not coin_data:
            logger.error(f"No data returned for {coin_symbol}")
            return None
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "coin": coin_symbol.upper(),
            "price_usd": coin_data.get("usd"),
            "volume_24h": coin_data.get("usd_24h_vol"),
            "market_cap": coin_data.get("usd_market_cap"),
            "change_24h_percent": coin_data.get("usd_24h_change"),
            "last_updated": datetime.utcfromtimestamp(coin_data.get("last_updated_at", 0)).isoformat() if coin_data.get("last_updated_at") else None
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch {coin_symbol}: {e}")
        return None


async def collect_training_data(
    coins: list,
    output_file: str,
    interval: int = 60,
    cycles: int = None,
    api_key: str = None
):
    """
    Collect cryptocurrency data for model training.
    
    Args:
        coins: List of coin symbols (BTC, ETH, etc.)
        output_file: CSV filename
        interval: Seconds between collections
        cycles: Number of cycles (None = infinite)
        api_key: Optional CoinGecko API key
    """
    filepath = Path(output_file)
    
    # Create CSV with headers if new file
    if not filepath.exists():
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'coin',
                'price_usd',
                'volume_24h',
                'market_cap',
                'change_24h_percent',
                'last_updated'
            ])
        logger.info(f"✅ Created CSV: {filepath}")
    else:
        logger.info(f"📝 Appending to: {filepath}")
    
    logger.info("=" * 70)
    logger.info("🚀 Crypto Data Collection for ML Training")
    logger.info("=" * 70)
    logger.info(f"📊 Coins: {', '.join(coins)}")
    logger.info(f"⏱️  Interval: {interval}s")
    logger.info(f"🔄 Cycles: {cycles if cycles else 'infinite'}")
    logger.info("=" * 70)
    logger.info("")
    
    cycle = 0
    total_records = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"📡 Cycle #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Collect data for all coins
            for coin in coins:
                data = await fetch_crypto_price(coin, api_key)
                
                if data:
                    # Write to CSV
                    with open(filepath, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            data['timestamp'],
                            data['coin'],
                            data['price_usd'],
                            data['volume_24h'],
                            data['market_cap'],
                            data['change_24h_percent'],
                            data['last_updated']
                        ])
                    
                    total_records += 1
                    logger.info(
                        f"  ✅ {coin}: ${data['price_usd']:,.2f} "
                        f"({data['change_24h_percent']:+.2f}% 24h)"
                    )
                else:
                    logger.warning(f"  ⚠️  Failed to collect {coin}")
            
            # Check if done
            if cycles and cycle >= cycles:
                logger.info(f"🏁 Reached {cycles} cycles. Stopping.")
                break
            
            # Wait
            logger.info(f"⏳ Waiting {interval}s...")
            logger.info("")
            await asyncio.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Stopped by user (Ctrl+C)")
    
    finally:
        logger.info("=" * 70)
        logger.info("📊 COLLECTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Total cycles: {cycle}")
        logger.info(f"Total records: {total_records}")
        logger.info(f"CSV file: {filepath.absolute()}")
        logger.info(f"File size: {filepath.stat().st_size:,} bytes")
        logger.info("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Collect crypto data for ML training"
    )
    parser.add_argument(
        "--coins",
        nargs="+",
        default=["BTC"],
        help="Coins to collect (BTC, ETH, USDC, etc.)"
    )
    parser.add_argument(
        "--output", "-o",
        default=f"crypto_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output CSV filename"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="Collection interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--cycles", "-c",
        type=int,
        default=None,
        help="Number of cycles (default: infinite)"
    )
    parser.add_argument(
        "--api-key",
        default="CG-cYgwjJpKpbVZbBeQgBmyT5S1",
        help="CoinGecko API key"
    )
    
    args = parser.parse_args()
    
    asyncio.run(collect_training_data(
        coins=args.coins,
        output_file=args.output,
        interval=args.interval,
        cycles=args.cycles,
        api_key=args.api_key
    ))
