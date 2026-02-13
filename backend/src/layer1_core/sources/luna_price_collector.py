"""
Luna Crash Price Data Collector

Collects historical price data for LUNA and UST from CoinGecko API during the crash period.

Uses CoinGecko's /coins/{id}/market_chart/range endpoint to fetch:
- Price (USD)
- Market cap
- Trading volume

Data collected at 5-minute intervals from May 2-13, 2022.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
from pathlib import Path

from src.layer1_core.sources.luna_crash_config import luna_config
from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


class LunaPriceCollector:
    """Collects historical price data for LUNA/UST crash."""

    def __init__(self):
        self.config = luna_config
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit_delay = 1.5  # CoinGecko free tier: ~50 req/min

        # Ensure output directory exists
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_price_range(
        self,
        coin_id: str,
        from_timestamp: int,
        to_timestamp: int
    ) -> Optional[Dict]:
        """
        Fetch historical price data from CoinGecko.

        Args:
            coin_id: CoinGecko coin ID (e.g., "terra-luna")
            from_timestamp: Start timestamp (Unix seconds)
            to_timestamp: End timestamp (Unix seconds)

        Returns:
            Dict with prices, market_caps, total_volumes arrays
        """
        url = f"{self.base_url}/coins/{coin_id}/market_chart/range"
        params = {
            "vs_currency": "usd",
            "from": from_timestamp,
            "to": to_timestamp
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"✓ Fetched {len(data.get('prices', []))} price points for {coin_id}"
                        )
                        return data
                    elif response.status == 429:
                        logger.warning("Rate limited by CoinGecko, waiting 60s...")
                        await asyncio.sleep(60)
                        return None
                    else:
                        logger.error(
                            f"CoinGecko API error for {coin_id}: {response.status}"
                        )
                        return None

        except Exception as e:
            logger.error(f"Error fetching price data for {coin_id}: {e}")
            return None

    async def collect_all_prices(self) -> Dict[str, Dict]:
        """
        Collect price data for all configured assets.

        Returns:
            Dict mapping asset symbol to price data
        """
        logger.info("=" * 70)
        logger.info("COLLECTING LUNA CRASH PRICE DATA")
        logger.info("=" * 70)
        logger.info(f"Period: {self.config.start_date} to {self.config.end_date}")
        logger.info(f"Assets: {', '.join([a['symbol'] for a in self.config.assets])}")

        # Convert dates to Unix timestamps
        from_ts = int(self.config.start_date.timestamp())
        to_ts = int(self.config.end_date.timestamp())

        all_data = {}

        for asset in self.config.assets:
            symbol = asset['symbol']
            coin_id = asset['coingecko_id']

            logger.info(f"\nFetching {symbol} ({coin_id})...")

            data = await self.fetch_price_range(coin_id, from_ts, to_ts)

            if data:
                all_data[symbol] = data

                # Save raw data to file
                output_file = self.output_dir / f"{symbol.lower()}_price_raw.json"
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info(f"✓ Saved raw data to {output_file}")

            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)

        logger.info("\n" + "=" * 70)
        logger.info(f"COLLECTION COMPLETE: {len(all_data)} assets")
        logger.info("=" * 70)

        return all_data

    def convert_to_risk_events(self, raw_data: Dict[str, Dict]) -> List[RiskEvent]:
        """
        Convert CoinGecko price data to RiskEvent format.

        Args:
            raw_data: Dict mapping symbol to CoinGecko API response

        Returns:
            List of RiskEvent objects
        """
        events = []

        for symbol, data in raw_data.items():
            prices = data.get('prices', [])
            market_caps = data.get('market_caps', [])
            volumes = data.get('total_volumes', [])

            # CoinGecko returns [timestamp_ms, value] pairs
            for i, (ts_ms, price) in enumerate(prices):
                # Convert timestamp from milliseconds to datetime
                timestamp = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

                # Get corresponding market cap and volume
                market_cap = market_caps[i][1] if i < len(market_caps) else None
                volume = volumes[i][1] if i < len(volumes) else None

                # Determine chain (UST was on Terra, LUNA is Terra Classic now)
                chain = "terra_classic" if symbol == "LUNA" else "terra"

                event = RiskEvent(
                    timestamp=timestamp,
                    coin=symbol,
                    chain=chain,
                    source="coingecko",
                    price=price,
                    market_cap=market_cap,
                    volume_24h=volume,
                    block_number=None,  # Historical API data has no block number
                    tx_hash=None,
                    confirmation_count=None,
                    finality_tier="tier3",  # Historical data is final
                    event_version=1,
                    invalidated=False
                )

                events.append(event)

        logger.info(f"✓ Converted {len(events)} price points to RiskEvents")
        return events

    async def save_events_to_csv(self, events: List[RiskEvent]):
        """Save RiskEvents to CSV for analysis."""
        import csv

        output_file = self.output_dir / "luna_crash_prices.csv"

        # Group events by coin
        luna_events = [e for e in events if e.coin == "LUNA"]
        ust_events = [e for e in events if e.coin == "UST"]

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "timestamp",
                "luna_price_usd",
                "luna_market_cap",
                "luna_volume_24h",
                "ust_price_usd",
                "ust_peg_deviation",
                "ust_market_cap",
                "ust_volume_24h"
            ])

            # Merge LUNA and UST data by timestamp
            # Assuming they have the same timestamps from CoinGecko
            for luna_event, ust_event in zip(luna_events, ust_events):
                ust_peg_dev = abs(1.0 - ust_event.price) if ust_event.price else None

                writer.writerow([
                    luna_event.timestamp.isoformat(),
                    luna_event.price,
                    luna_event.market_cap,
                    luna_event.volume_24h,
                    ust_event.price,
                    ust_peg_dev,
                    ust_event.market_cap,
                    ust_event.volume_24h
                ])

        logger.info(f"✓ Saved {len(luna_events)} data points to {output_file}")


async def demo_luna_price_collection():
    """Demo: Collect Luna crash price data."""
    collector = LunaPriceCollector()

    # Collect raw data
    raw_data = await collector.collect_all_prices()

    # Convert to RiskEvents
    events = collector.convert_to_risk_events(raw_data)

    # Save to CSV
    await collector.save_events_to_csv(events)

    # Print sample data
    logger.info("\n" + "=" * 70)
    logger.info("SAMPLE DATA (first 5 points)")
    logger.info("=" * 70)

    for event in events[:10]:  # Show first 10 (5 LUNA + 5 UST)
        logger.info(
            f"{event.timestamp.strftime('%Y-%m-%d %H:%M')} | "
            f"{event.coin:4} | ${event.price:12.8f} | "
            f"Vol: ${event.volume_24h/1e6:8.2f}M"
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(demo_luna_price_collection())
