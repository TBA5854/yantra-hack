"""
Luna Crash Market Metrics Collector

Collects detailed market metrics from exchanges during the crash:
- Trading volume (buy vs sell pressure)
- Order book depth (liquidity collapse)
- Funding rates (perpetual futures)
- Open interest (derivatives exposure)

Primary source: Binance API (historical klines and metrics)
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import json
from pathlib import Path

from .config import luna_config
from .models import RiskEvent

logger = logging.getLogger(__name__)


class LunaMarketCollector:
    """Collects market metrics from exchanges during Luna crash."""

    def __init__(self):
        self.config = luna_config

        # Binance API
        self.binance_url = "https://api.binance.com/api/v3"

        # Ensure output directory exists
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_klines(
        self,
        symbol: str,
        interval: str = "5m",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[List]:
        """
        Fetch candlestick (kline) data from Binance.

        Args:
            symbol: Trading pair (e.g., "LUNAUSDT")
            interval: Candlestick interval ("1m", "5m", "1h", etc.)
            start_time: Start timestamp (ms)
            end_time: End timestamp (ms)

        Returns:
            List of klines [timestamp, open, high, low, close, volume, ...]
        """
        url = f"{self.binance_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": 1000  # Max per request
        }

        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.warning(
                            f"Binance API error for {symbol}: {response.status}"
                        )
                        return []
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return []

    async def fetch_all_klines(self, symbol: str) -> List[List]:
        """
        Fetch all klines for the crash period (May 2-13, 2022).

        Binance klines endpoint has a 1000 record limit, so we need to
        paginate through the time range.

        Args:
            symbol: Trading pair

        Returns:
            All klines for the period
        """
        all_klines = []

        # Convert config dates to milliseconds
        start_ms = int(self.config.start_date.timestamp() * 1000)
        end_ms = int(self.config.end_date.timestamp() * 1000)

        # Fetch in chunks (Binance limit: 1000 records per request)
        # 5min intervals: 1000 * 5 = 5000 mins = ~3.5 days
        # We need to loop until we reach end_ms
        
        current_start = start_ms
        while current_start < end_ms:
            logger.info(f"  Fetching from {datetime.fromtimestamp(current_start/1000, tz=timezone.utc)}...")
            
            chunk = await self.fetch_klines(
                symbol=symbol,
                interval="5m",
                start_time=current_start,
                end_time=end_ms
            )
            
            if not chunk:
                break
                
            all_klines.extend(chunk)
            
            # Start next chunk from the last close time + 1ms
            # kline[6] is close time (ms)
            last_close_time = chunk[-1][6]
            current_start = last_close_time + 1
            
            # Rate limiting
            await asyncio.sleep(0.1)

        logger.info(f"✓ Fetched {len(all_klines)} klines for {symbol}")

        return all_klines

    def parse_klines_to_events(self, symbol: str, klines: List[List]) -> List[RiskEvent]:
        """
        Convert Binance klines to RiskEvents.

        Binance kline format:
        [
            timestamp,        # 0: Open time
            open,             # 1: Open price
            high,             # 2: High price
            low,              # 3: Low price
            close,            # 4: Close price
            volume,           # 5: Volume
            close_time,       # 6: Close time
            quote_volume,     # 7: Quote asset volume
            num_trades,       # 8: Number of trades
            taker_buy_base,   # 9: Taker buy base asset volume
            taker_buy_quote,  # 10: Taker buy quote asset volume
            ignore            # 11: Unused field
        ]

        Args:
            symbol: Trading pair (e.g., "LUNAUSDT")
            klines: List of kline arrays

        Returns:
            List of RiskEvents
        """
        events = []

        # Extract coin from symbol (LUNAUSDT -> LUNA)
        coin = symbol.replace("USDT", "")

        for kline in klines:
            timestamp_ms = kline[0]
            open_price = float(kline[1])
            high = float(kline[2])
            low = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])
            quote_volume = float(kline[7])
            num_trades = int(kline[8])
            taker_buy_volume = float(kline[9])

            # Calculate buy/sell pressure
            # If taker buy > 50% of volume -> buy pressure
            # If taker buy < 50% of volume -> sell pressure
            buy_pressure = taker_buy_volume / volume if volume > 0 else 0.5

            timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

            event = RiskEvent(
                timestamp=timestamp,
                coin=coin,
                chain="binance",  # Exchange, not blockchain
                source="binance_spot",
                price=close_price,
                volume_24h=quote_volume,  # Using quote volume (USDT volume)
                block_number=None,
                tx_hash=None,
                confirmation_count=None,
                finality_tier="tier3",  # Exchange data is final
                event_version=1,
                invalidated=False,
                # Custom fields (will be stored as metadata)
                metadata={
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "volume_base": volume,
                    "num_trades": num_trades,
                    "buy_pressure": buy_pressure,
                    "price_change_pct": ((close_price - open_price) / open_price * 100)
                    if open_price > 0 else 0
                }
            )

            events.append(event)

        return events

    async def collect_all_market_data(self) -> Dict[str, List[RiskEvent]]:
        """
        Collect market data for all configured symbols.

        Returns:
            Dict mapping symbol to list of RiskEvents
        """
        logger.info("=" * 70)
        logger.info("COLLECTING LUNA CRASH MARKET DATA (BINANCE)")
        logger.info("=" * 70)

        all_events = {}

        for symbol in self.config.binance_symbols:
            logger.info(f"\nFetching {symbol}...")

            # Fetch klines
            klines = await self.fetch_all_klines(symbol)

            if klines:
                # Convert to events
                events = self.parse_klines_to_events(symbol, klines)
                all_events[symbol] = events

                # Save raw klines
                output_file = self.output_dir / f"{symbol.lower()}_klines.json"
                with open(output_file, 'w') as f:
                    json.dump(klines, f)

                logger.info(f"✓ Parsed {len(events)} events from {symbol}")

            # Rate limiting (Binance: 1200 req/min)
            await asyncio.sleep(0.1)

        logger.info("\n" + "=" * 70)
        logger.info(f"COLLECTION COMPLETE: {len(all_events)} symbols")
        logger.info("=" * 70)

        return all_events

    async def save_market_data_csv(self, all_events: Dict[str, List[RiskEvent]]):
        """Save market data to CSV."""
        import csv

        output_file = self.output_dir / "luna_crash_market.csv"

        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                "timestamp",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume_usdt",
                "num_trades",
                "buy_pressure",
                "price_change_pct"
            ])

            for symbol, events in all_events.items():
                for event in events:
                    meta = event.metadata or {}
                    writer.writerow([
                        event.timestamp.isoformat(),
                        symbol,
                        meta.get('open'),
                        meta.get('high'),
                        meta.get('low'),
                        event.price,
                        event.volume_24h,
                        meta.get('num_trades'),
                        meta.get('buy_pressure'),
                        meta.get('price_change_pct')
                    ])

        logger.info(f"✓ Saved market data to {output_file}")


async def demo_luna_market_collection():
    """Demo: Collect Luna crash market data."""
    collector = LunaMarketCollector()

    # Collect data
    all_events = await collector.collect_all_market_data()

    # Save to CSV
    await collector.save_market_data_csv(all_events)

    # Print statistics
    logger.info("\n" + "=" * 70)
    logger.info("MARKET DATA STATISTICS")
    logger.info("=" * 70)

    for symbol, events in all_events.items():
        if events:
            first = events[0]
            last = events[-1]

            price_change = (last.price - first.price) / first.price * 100

            total_volume = sum(e.volume_24h or 0 for e in events)
            avg_buy_pressure = sum(
                e.metadata.get('buy_pressure', 0.5) for e in events
            ) / len(events)

            logger.info(f"\n{symbol}:")
            logger.info(f"  Data points:     {len(events)}")
            logger.info(f"  Price change:    {price_change:+.1f}%")
            logger.info(
                f"  First price:     ${first.price:.8f} "
                f"({first.timestamp.strftime('%Y-%m-%d %H:%M')})"
            )
            logger.info(
                f"  Last price:      ${last.price:.8f} "
                f"({last.timestamp.strftime('%Y-%m-%d %H:%M')})"
            )
            logger.info(f"  Total volume:    ${total_volume/1e9:.2f}B")
            logger.info(f"  Avg buy pressure: {avg_buy_pressure:.1%}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(demo_luna_market_collection())
