"""
Unified Crashed Stablecoin Data Collector

Collects historical crash data and recent data for 5 failed algorithmic stablecoins:
- USDD (June 2022 depeg)
- USDN (April 2022 Waves crash)
- BAC (January 2021 collapse)
- SETD (February 2021 depeg)

Reuses existing Luna crash collection infrastructure.

Usage:
    # Collect all datasets
    python -m src.data_collection.sources.collect_crashed_coins

    # Collect specific coin
    python -m src.data_collection.sources.collect_crashed_coins --coin USDD

    # Collect only crash periods
    python -m src.data_collection.sources.collect_crashed_coins --crash-only
"""

import asyncio
import logging
import argparse
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from src.data_collection.sources.crashed_coin_configs import (
    CRASHED_COIN_CONFIGS,
    CrashedCoinConfig,
    get_all_crash_configs,
    get_all_recent_configs,
    get_configs_for_coin
)
from src.data_collection.sources.luna_market_collector import LunaMarketCollector
from src.data_collection.sources.cryptocompare_collector import cryptocompare_collector
from src.common.schema import RiskEvent

import pandas as pd
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class CrashedCoinCollector:
    """Collects data for crashed stablecoins using Luna crash infrastructure"""

    def __init__(self, config: CrashedCoinConfig):
        self.config = config
        self.market_collector = LunaMarketCollector() if config.binance_symbol else None
        self.events: List[RiskEvent] = []

    async def collect_binance_data(self) -> List[RiskEvent]:
        """Collect data from Binance klines (if available)"""
        if not self.market_collector or not self.config.binance_symbol:
            logger.info(f"  ⏭️  No Binance symbol for {self.config.coin}, skipping Binance")
            return []

        logger.info(f"  📊 Fetching Binance klines for {self.config.binance_symbol}...")

        try:
            # Convert dates to milliseconds
            start_ms = int(self.config.start_date.timestamp() * 1000)
            end_ms = int(self.config.end_date.timestamp() * 1000)

            # Fetch klines (raw data)
            all_klines = []
            current_start = start_ms

            while current_start < end_ms:
                chunk = await self.market_collector.fetch_klines(
                    symbol=self.config.binance_symbol,
                    interval="5m",
                    start_time=current_start,
                    end_time=end_ms
                )

                if not chunk:
                    break

                all_klines.extend(chunk)

                # Move to next chunk
                last_close_time = chunk[-1][6]
                current_start = last_close_time + 1

                # Rate limiting
                await asyncio.sleep(0.1)

            # Convert to RiskEvents
            events = self.market_collector.parse_klines_to_events(
                symbol=self.config.binance_symbol,
                klines=all_klines
            )

            logger.info(f"  ✓ Collected {len(events)} Binance klines")
            return events

        except Exception as e:
            logger.error(f"  ❌ Binance collection failed: {e}")
            return []

    async def collect_coingecko_data(self) -> List[RiskEvent]:
        """Collect data from CoinGecko (fallback or primary if no Binance)"""
        logger.info(f"  🦎 Fetching CoinGecko data for {self.config.coingecko_id}...")

        try:
            import aiohttp
            import os

            # Use free API with Demo key (Demo keys use api.coingecko.com, not pro-api)
            api_key = os.getenv("COINGECKO_API_KEY")
            url = f"https://api.coingecko.com/api/v3/coins/{self.config.coingecko_id}/market_chart/range"

            if api_key:
                headers = {"x-cg-demo-api-key": api_key}
                logger.info(f"  ℹ️  Using CoinGecko API with Demo key")
            else:
                headers = {}
                logger.info(f"  ℹ️  Using CoinGecko Free API (no key, may be rate limited)")

            params = {
                "vs_currency": "usd",
                "from": int(self.config.start_date.timestamp()),
                "to": int(self.config.end_date.timestamp())
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"  ❌ CoinGecko API error: {response.status}")
                        logger.error(f"  Response: {error_text[:200]}")
                        return []

                    data = await response.json()

                    # Extract price data
                    prices = data.get("prices", [])
                    volumes = data.get("total_volumes", [])
                    market_caps = data.get("market_caps", [])

                    events = []

                    # Create volume and market cap lookups (by timestamp)
                    volume_dict = {int(v[0]): v[1] for v in volumes}
                    mcap_dict = {int(m[0]): m[1] for m in market_caps}

                    for price_point in prices:
                        timestamp_ms = int(price_point[0])
                        price = float(price_point[1])
                        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

                        event = RiskEvent(
                            timestamp=timestamp,
                            coin=self.config.coin,
                            source="coingecko",
                            price=price,
                            volume_24h=volume_dict.get(timestamp_ms),
                            market_cap=mcap_dict.get(timestamp_ms),
                        )
                        events.append(event)

                    logger.info(f"  ✓ Collected {len(events)} CoinGecko data points")
                    return events

        except Exception as e:
            logger.error(f"  ❌ CoinGecko collection failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def collect_cryptocompare_data(self) -> List[RiskEvent]:
        """Collect data from CryptoCompare (free historical data)"""
        # Extract symbol from coin ID (e.g., "USDD" from "usdd")
        coin_symbol = self.config.coin

        logger.info(f"  📈 Trying CryptoCompare for {coin_symbol}...")

        try:
            events = await cryptocompare_collector.fetch_historical_hourly(
                coin_symbol=coin_symbol,
                start_date=self.config.start_date,
                end_date=self.config.end_date,
                coin_name=self.config.coin
            )

            if events:
                logger.info(f"  ✓ CryptoCompare success: {len(events)} data points")
            return events

        except Exception as e:
            logger.error(f"  ❌ CryptoCompare failed: {e}")
            return []

    async def collect_all_sources(self) -> List[RiskEvent]:
        """Collect data from all available sources with fallback chain"""
        all_events = []

        # Priority 1: Try Binance first (most reliable, 5-min granularity)
        binance_events = await self.collect_binance_data()
        if binance_events:
            all_events.extend(binance_events)
            self.events = all_events
            return all_events

        # Priority 2: Try CryptoCompare (free, hourly granularity, historical access)
        logger.info(f"  ℹ️  No Binance data, trying CryptoCompare...")
        cryptocompare_events = await self.collect_cryptocompare_data()
        if cryptocompare_events:
            all_events.extend(cryptocompare_events)
            self.events = all_events
            return all_events

        # Priority 3: Fall back to CoinGecko (limited historical access)
        logger.info(f"  ℹ️  No CryptoCompare data, falling back to CoinGecko...")
        coingecko_events = await self.collect_coingecko_data()
        all_events.extend(coingecko_events)

        self.events = all_events
        return all_events

    def _interpolate_to_5min(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Interpolate hourly data to 5-minute granularity.

        Uses linear interpolation for price and volume data to create
        realistic 5-minute intervals from hourly data.
        """
        if df.empty:
            return df

        logger.info(f"  🔄 Interpolating {len(df)} hourly points to 5-min granularity...")

        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)

        # Create 5-minute range
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()
        five_min_range = pd.date_range(start=start_time, end=end_time, freq='5min')

        # Create new dataframe with 5-min timestamps
        interpolated_df = pd.DataFrame({'timestamp': five_min_range})

        # Set timestamp as index for interpolation
        df_indexed = df.set_index('timestamp')

        # Get coin and source values (should be constant)
        coin_val = df['coin'].iloc[0] if 'coin' in df.columns and len(df) > 0 else None
        source_val = df['source'].iloc[0] if 'source' in df.columns and len(df) > 0 else None

        # Interpolate numeric columns only
        numeric_cols = ['price', 'volume_24h', 'market_cap']
        for col in numeric_cols:
            if col in df_indexed.columns:
                # Convert to numeric if needed
                series = pd.to_numeric(df_indexed[col], errors='coerce')
                # Reindex to 5-min frequency and interpolate
                interpolated_df[col] = series.reindex(
                    interpolated_df['timestamp']
                ).interpolate(method='linear')

        # Set constant columns
        interpolated_df['coin'] = coin_val
        interpolated_df['source'] = source_val

        # Fill remaining columns with None
        for col in ['liquidity_depth', 'net_supply_change', 'market_volatility', 'sentiment_score']:
            interpolated_df[col] = None

        logger.info(f"  ✓ Interpolated to {len(interpolated_df)} 5-min data points")

        return interpolated_df

    def aggregate_and_save(self):
        """Aggregate events and save to CSV, Parquet, JSON"""
        if not self.events:
            logger.warning(f"  ⚠️  No events to save for {self.config.name}")
            return

        logger.info(f"  💾 Saving {len(self.events)} events to {self.config.output_dir}...")

        # Create output directory
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Convert events to DataFrame
        df = self._events_to_dataframe(self.events)

        # Interpolate to 5-min granularity if data is hourly
        if len(df) > 0:
            # Check if data is hourly (avg time diff ~1 hour)
            df_sorted = df.sort_values('timestamp')
            if len(df_sorted) > 1:
                time_diffs = df_sorted['timestamp'].diff().dt.total_seconds() / 60  # minutes
                avg_interval = time_diffs.mean()

                if avg_interval > 30:  # If average interval > 30 min, likely hourly
                    logger.info(f"  ℹ️  Detected hourly data (avg interval: {avg_interval:.1f} min)")
                    df = self._interpolate_to_5min(df)

        # Calculate derived metrics
        df = self._calculate_metrics(df)

        # Save to multiple formats
        coin_lower = self.config.coin.lower()

        # CSV
        csv_path = output_path / f"{coin_lower}_unified.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"  ✓ Saved CSV: {csv_path}")

        # Parquet
        parquet_path = output_path / f"{coin_lower}_unified.parquet"
        df.to_parquet(parquet_path, index=False)
        logger.info(f"  ✓ Saved Parquet: {parquet_path}")

        # Summary stats JSON
        summary = self._generate_summary(df)
        summary_path = output_path / "summary_stats.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"  ✓ Saved summary: {summary_path}")

        logger.info(f"  🎉 Complete! {len(df)} records saved")

    def _events_to_dataframe(self, events: List[RiskEvent]) -> pd.DataFrame:
        """Convert RiskEvent list to DataFrame"""
        data = []
        for event in events:
            data.append({
                "timestamp": event.timestamp,
                "coin": event.coin,
                "source": event.source,
                "price": event.price,
                "volume_24h": event.volume_24h,
                "market_cap": event.market_cap,
                "liquidity_depth": event.liquidity_depth,
                "net_supply_change": event.net_supply_change,
                "market_volatility": event.market_volatility,
                "sentiment_score": event.sentiment_score,
            })

        df = pd.DataFrame(data)

        # Sort by timestamp
        if not df.empty:
            df = df.sort_values("timestamp").reset_index(drop=True)

        return df

    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate derived metrics (peg deviation, price change, etc.)"""
        if df.empty:
            return df

        # Peg deviation (absolute difference from $1.00)
        if "price" in df.columns:
            df["peg_deviation"] = (df["price"] - 1.0).abs()
            df["peg_deviation_bps"] = df["peg_deviation"] * 10000  # Basis points

            # Price change percentage
            df["price_change_pct"] = df["price"].pct_change() * 100

        return df

    def _generate_summary(self, df: pd.DataFrame) -> dict:
        """Generate summary statistics"""
        if df.empty:
            return {
                "config": self.config.name,
                "coin": self.config.coin,
                "total_records": 0,
                "error": "No data collected"
            }

        summary = {
            "config": self.config.name,
            "coin": self.config.coin,
            "period": {
                "start": self.config.start_date.isoformat(),
                "end": self.config.end_date.isoformat(),
            },
            "total_records": len(df),
            "sources": df["source"].value_counts().to_dict(),
            "price_stats": {},
            "depeg_stats": {},
        }

        # Price statistics
        if "price" in df.columns and df["price"].notna().any():
            summary["price_stats"] = {
                "min": float(df["price"].min()),
                "max": float(df["price"].max()),
                "mean": float(df["price"].mean()),
                "start": float(df["price"].iloc[0]),
                "end": float(df["price"].iloc[-1]),
                "change_pct": float((df["price"].iloc[-1] / df["price"].iloc[0] - 1) * 100),
            }

        # Depeg statistics
        if "peg_deviation_bps" in df.columns and df["peg_deviation_bps"].notna().any():
            summary["depeg_stats"] = {
                "max_depeg_bps": float(df["peg_deviation_bps"].max()),
                "mean_depeg_bps": float(df["peg_deviation_bps"].mean()),
                "min_price": float(df["price"].min()),
                "worst_depeg_timestamp": df.loc[df["peg_deviation_bps"].idxmax(), "timestamp"].isoformat(),
            }

        return summary


async def collect_dataset(config: CrashedCoinConfig):
    """Collect a single dataset"""
    logger.info("=" * 70)
    logger.info(f"COLLECTING: {config.name.upper()}")
    logger.info("=" * 70)
    logger.info(f"Coin: {config.coin}")
    logger.info(f"Period: {config.start_date.date()} to {config.end_date.date()}")
    logger.info(f"Description: {config.description}")

    collector = CrashedCoinCollector(config)

    # Collect from all sources
    events = await collector.collect_all_sources()

    if not events:
        logger.error(f"❌ Failed to collect any data for {config.name}")
        return False

    # Aggregate and save
    collector.aggregate_and_save()

    logger.info("=" * 70)
    logger.info(f"✅ {config.name.upper()} COMPLETE")
    logger.info("=" * 70)
    logger.info("")

    return True


async def collect_all_datasets(
    coin: Optional[str] = None,
    crash_only: bool = False,
    recent_only: bool = False
):
    """Collect all configured datasets"""
    logger.info("=" * 70)
    logger.info("CRASHED STABLECOIN DATA COLLECTION")
    logger.info("=" * 70)

    # Determine which configs to collect
    if coin:
        configs = get_configs_for_coin(coin.upper())
        logger.info(f"Mode: Single coin ({coin.upper()})")
    elif crash_only:
        configs = get_all_crash_configs()
        logger.info("Mode: Crash periods only")
    elif recent_only:
        configs = get_all_recent_configs()
        logger.info("Mode: Recent periods only")
    else:
        configs = list(CRASHED_COIN_CONFIGS.values())
        logger.info("Mode: All datasets")

    logger.info(f"Total datasets to collect: {len(configs)}")
    logger.info("")

    # Collect each dataset sequentially
    successful = 0
    failed = 0

    for config in configs:
        success = await collect_dataset(config)
        if success:
            successful += 1
        else:
            failed += 1

        # Brief pause between datasets
        await asyncio.sleep(1)

    # Final summary
    logger.info("=" * 70)
    logger.info("COLLECTION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total datasets: {len(configs)}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info("=" * 70)


def main():
    """Main entry point with CLI arguments"""
    parser = argparse.ArgumentParser(
        description="Collect historical crash data for failed stablecoins"
    )
    parser.add_argument(
        "--coin",
        type=str,
        help="Collect only specific coin (USDD, USDN, BAC, SETD)",
    )
    parser.add_argument(
        "--crash-only",
        action="store_true",
        help="Collect only crash periods (skip recent)",
    )
    parser.add_argument(
        "--recent-only",
        action="store_true",
        help="Collect only recent periods (skip crash)",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run collection
    asyncio.run(collect_all_datasets(
        coin=args.coin,
        crash_only=args.crash_only,
        recent_only=args.recent_only
    ))


if __name__ == "__main__":
    main()
