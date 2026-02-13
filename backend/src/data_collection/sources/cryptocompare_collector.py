"""
CryptoCompare Historical Data Collector

Free alternative to CoinGecko for historical price data.
- No API key required
- Supports data back to 2015
- Hourly and daily granularity
- Rate limit: 100,000 calls/month (free tier)
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from typing import List, Optional

from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


class CryptoCompareCollector:
    """Collects historical price data from CryptoCompare API."""

    def __init__(self):
        self.base_url = "https://min-api.cryptocompare.com/data/v2"

    async def fetch_historical_hourly(
        self,
        coin_symbol: str,
        start_date: datetime,
        end_date: datetime,
        coin_name: Optional[str] = None
    ) -> List[RiskEvent]:
        """
        Fetch hourly historical data from CryptoCompare.

        Args:
            coin_symbol: Coin symbol (e.g., "USDD", "USDN")
            start_date: Start datetime (UTC)
            end_date: End datetime (UTC)
            coin_name: Optional coin name override for RiskEvent

        Returns:
            List of RiskEvents with hourly data
        """
        logger.info(f"  📈 Fetching CryptoCompare data for {coin_symbol}...")

        try:
            import os

            # Calculate how many hours we need
            duration_hours = int((end_date - start_date).total_seconds() / 3600)
            end_ts = int(end_date.timestamp())

            url = f"{self.base_url}/histohour"
            params = {
                "fsym": coin_symbol,  # From symbol
                "tsym": "USD",        # To symbol
                "limit": min(duration_hours, 2000),  # Max 2000 per request
                "toTs": end_ts
            }

            # Add API key if available
            api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
            headers = {}
            if api_key:
                headers["authorization"] = f"Apikey {api_key}"
                logger.info(f"  ℹ️  Using CryptoCompare API key")
            else:
                logger.info(f"  ℹ️  Using CryptoCompare without API key (rate limited)")

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"  ❌ CryptoCompare API error: {response.status}")
                        return []

                    data = await response.json()

                    # Check for error response
                    if data.get("Response") == "Error":
                        error_msg = data.get("Message", "Unknown error")
                        logger.error(f"  ❌ CryptoCompare error: {error_msg}")
                        return []

                    # Extract OHLCV data
                    candles = data.get("Data", {}).get("Data", [])

                    if not candles:
                        logger.warning(f"  ⚠️  No data returned for {coin_symbol}")
                        return []

                    # Filter to requested time range
                    events = []
                    start_ts = int(start_date.timestamp())

                    for candle in candles:
                        timestamp_unix = candle["time"]

                        # Skip if outside requested range
                        if timestamp_unix < start_ts or timestamp_unix > end_ts:
                            continue

                        # Skip if all zeros (no trading data)
                        if candle["close"] == 0 and candle["volumefrom"] == 0:
                            continue

                        timestamp = datetime.fromtimestamp(timestamp_unix, tz=timezone.utc)

                        event = RiskEvent(
                            timestamp=timestamp,
                            coin=coin_name or coin_symbol,
                            source="cryptocompare",
                            price=float(candle["close"]),
                            volume_24h=float(candle["volumeto"]),  # Volume in USD
                            market_cap=None,  # Not provided by CryptoCompare
                        )
                        events.append(event)

                    logger.info(f"  ✓ Collected {len(events)} CryptoCompare data points")
                    return events

        except Exception as e:
            logger.error(f"  ❌ CryptoCompare collection failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def fetch_historical_daily(
        self,
        coin_symbol: str,
        start_date: datetime,
        end_date: datetime,
        coin_name: Optional[str] = None
    ) -> List[RiskEvent]:
        """
        Fetch daily historical data from CryptoCompare.

        Same as hourly but with daily granularity (useful for longer periods).
        """
        logger.info(f"  📈 Fetching CryptoCompare daily data for {coin_symbol}...")

        try:
            duration_days = (end_date - start_date).days
            end_ts = int(end_date.timestamp())

            url = f"{self.base_url}/histoday"
            params = {
                "fsym": coin_symbol,
                "tsym": "USD",
                "limit": min(duration_days, 2000),
                "toTs": end_ts
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"  ❌ CryptoCompare API error: {response.status}")
                        return []

                    data = await response.json()

                    if data.get("Response") == "Error":
                        error_msg = data.get("Message", "Unknown error")
                        logger.error(f"  ❌ CryptoCompare error: {error_msg}")
                        return []

                    candles = data.get("Data", {}).get("Data", [])

                    if not candles:
                        logger.warning(f"  ⚠️  No data returned for {coin_symbol}")
                        return []

                    events = []
                    start_ts = int(start_date.timestamp())

                    for candle in candles:
                        timestamp_unix = candle["time"]

                        if timestamp_unix < start_ts or timestamp_unix > end_ts:
                            continue

                        if candle["close"] == 0 and candle["volumefrom"] == 0:
                            continue

                        timestamp = datetime.fromtimestamp(timestamp_unix, tz=timezone.utc)

                        event = RiskEvent(
                            timestamp=timestamp,
                            coin=coin_name or coin_symbol,
                            source="cryptocompare",
                            price=float(candle["close"]),
                            volume_24h=float(candle["volumeto"]),
                            market_cap=None,
                        )
                        events.append(event)

                    logger.info(f"  ✓ Collected {len(events)} CryptoCompare daily data points")
                    return events

        except Exception as e:
            logger.error(f"  ❌ CryptoCompare daily collection failed: {e}")
            import traceback
            traceback.print_exc()
            return []


# Singleton instance
cryptocompare_collector = CryptoCompareCollector()


async def demo_cryptocompare():
    """Demo: Fetch USDD crash data from CryptoCompare."""
    from datetime import datetime, timezone

    collector = CryptoCompareCollector()

    # USDD crash: June 12-18, 2022
    start = datetime(2022, 6, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2022, 6, 18, 23, 59, 59, tzinfo=timezone.utc)

    events = await collector.fetch_historical_hourly("USDD", start, end)

    print(f"\nCollected {len(events)} events for USDD crash period")
    if events:
        print(f"First event: {events[0].timestamp} - ${events[0].price}")
        print(f"Last event: {events[-1].timestamp} - ${events[-1].price}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo_cryptocompare())
