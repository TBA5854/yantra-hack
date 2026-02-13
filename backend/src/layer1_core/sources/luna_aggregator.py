"""
Luna Crash Data Aggregator

Combines data from all collectors into a unified dataset:
1. Price data (CoinGecko)
2. On-chain events (Terra blockchain)
3. Market metrics (Binance)

Outputs:
- Unified CSV with all metrics aligned by timestamp
- JSON with metadata and event annotations
- Summary statistics and crash timeline
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict
import json
import csv
from pathlib import Path
import pandas as pd

from src.layer1_core.sources.luna_crash_config import luna_config, LUNA_CRASH_TIMELINE
from src.layer1_core.sources.luna_price_collector import LunaPriceCollector
from src.layer1_core.sources.luna_onchain_collector import LunaOnChainCollector
from src.layer1_core.sources.luna_market_collector import LunaMarketCollector
from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


class LunaDataAggregator:
    """Aggregates all Luna crash data sources into unified dataset."""

    def __init__(self):
        self.config = luna_config
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Collectors
        self.price_collector = LunaPriceCollector()
        self.onchain_collector = LunaOnChainCollector()
        self.market_collector = LunaMarketCollector()

    async def collect_all_data(self) -> Dict[str, any]:
        """
        Run all data collectors.

        Returns:
            Dict with all collected data
        """
        logger.info("=" * 70)
        logger.info("LUNA CRASH DATA COLLECTION - FULL PIPELINE")
        logger.info("=" * 70)
        logger.info(f"Period: {self.config.start_date} to {self.config.end_date}")
        logger.info(f"Duration: {self.config.get_date_range_days()} days")
        logger.info("")

        # Step 1: Collect price data
        logger.info("STEP 1: Collecting price data from CoinGecko...")
        price_raw = await self.price_collector.collect_all_prices()
        price_events = self.price_collector.convert_to_risk_events(price_raw)

        # Step 2: Collect on-chain data
        logger.info("\nSTEP 2: Collecting on-chain supply data...")
        onchain_events = await self.onchain_collector.collect_all_onchain_data()

        # Step 3: Collect market data
        logger.info("\nSTEP 3: Collecting market data from Binance...")
        market_events = await self.market_collector.collect_all_market_data()

        return {
            "price_raw": price_raw,
            "price_events": price_events,
            "onchain_events": onchain_events,
            "market_events": market_events
        }

    def merge_data_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """
        Merge all data sources into a single pandas DataFrame.

        Aligns by timestamp and coin, creating a unified view.

        Args:
            data: Dict from collect_all_data()

        Returns:
            Unified pandas DataFrame
        """
        logger.info("\n" + "=" * 70)
        logger.info("MERGING DATA SOURCES")
        logger.info("=" * 70)

        # Convert price events to DataFrame
        price_data = []
        for event in data['price_events']:
            price_data.append({
                'timestamp': event.timestamp,
                'coin': event.coin,
                'price_coingecko': event.price,
                'market_cap': event.market_cap,
                'volume_coingecko': event.volume_24h
            })
        df_price = pd.DataFrame(price_data)

        # Convert market events to DataFrame
        market_data = []
        for symbol, events in data['market_events'].items():
            coin = symbol.replace("USDT", "")
            for event in events:
                meta = event.metadata or {}
                market_data.append({
                    'timestamp': event.timestamp,
                    'coin': coin,
                    'price_binance': event.price,
                    'open': meta.get('open'),
                    'high': meta.get('high'),
                    'low': meta.get('low'),
                    'volume_binance': event.volume_24h,
                    'num_trades': meta.get('num_trades'),
                    'buy_pressure': meta.get('buy_pressure'),
                    'price_change_pct': meta.get('price_change_pct')
                })
        df_market = pd.DataFrame(market_data)

        # Merge price and market data
        if not df_price.empty and not df_market.empty:
            # Round timestamps to nearest 5 minutes for alignment
            df_price['timestamp_round'] = pd.to_datetime(df_price['timestamp']).dt.round('5min')
            df_market['timestamp_round'] = pd.to_datetime(df_market['timestamp']).dt.round('5min')

            df_merged = pd.merge(
                df_price,
                df_market,
                on=['timestamp_round', 'coin'],
                how='outer',
                suffixes=('_coingecko', '_binance')
            )

            # Use binance timestamp as primary (more granular)
            df_merged['timestamp'] = df_merged['timestamp_binance'].fillna(
                df_merged['timestamp_coingecko']
            )

            # Drop helper columns
            df_merged = df_merged.drop(
                columns=['timestamp_round', 'timestamp_coingecko', 'timestamp_binance']
            )
        else:
            df_merged = pd.concat([df_price, df_market], ignore_index=True)

        # Add on-chain supply data
        onchain_data = []
        for event in data['onchain_events']:
            onchain_data.append({
                'date': event.timestamp.date(),
                'coin': event.coin,
                'net_supply_change': event.net_supply_change
            })
        df_onchain = pd.DataFrame(onchain_data)

        # Merge with daily aggregation
        if not df_merged.empty and not df_onchain.empty:
            df_merged['date'] = pd.to_datetime(df_merged['timestamp']).dt.date

            df_final = pd.merge(
                df_merged,
                df_onchain,
                on=['date', 'coin'],
                how='left'
            )
        else:
            df_final = df_merged

        # Sort by timestamp
        df_final = df_final.sort_values(['coin', 'timestamp'])

        # Calculate derived metrics
        if 'price_binance' in df_final.columns and 'price_coingecko' in df_final.columns:
            # Use Binance price as primary (more accurate for trading), fallback to CoinGecko
            df_final['price'] = df_final['price_binance'].fillna(df_final['price_coingecko'])
        elif 'price_binance' in df_final.columns:
            df_final['price'] = df_final['price_binance']
        elif 'price_coingecko' in df_final.columns:
            df_final['price'] = df_final['price_coingecko']
        else:
            logger.warning("No price data available in merged dataset")
            df_final['price'] = None

        # For UST, calculate peg deviation
        if 'coin' in df_final.columns:
            ust_mask = df_final['coin'] == 'UST'
            if ust_mask.any() and 'price' in df_final.columns:
                df_final.loc[ust_mask, 'peg_deviation'] = abs(1.0 - df_final.loc[ust_mask, 'price'])
                df_final.loc[ust_mask, 'peg_deviation_bps'] = df_final.loc[ust_mask, 'peg_deviation'] * 10000

        logger.info(f"✓ Merged data: {len(df_final)} rows")
        logger.info(f"  LUNA rows: {len(df_final[df_final['coin'] == 'LUNA'])}")
        logger.info(f"  UST rows:  {len(df_final[df_final['coin'] == 'UST'])}")

        return df_final

    async def save_unified_dataset(self, df: pd.DataFrame):
        """Save unified dataset to CSV."""
        output_file = self.output_dir / "luna_crash_unified.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved unified dataset to {output_file}")

        # Also save as parquet for faster loading
        parquet_file = self.output_dir / "luna_crash_unified.parquet"
        df.to_parquet(parquet_file, index=False)
        logger.info(f"✓ Saved parquet format to {parquet_file}")

    async def generate_summary_stats(self, df: pd.DataFrame):
        """Generate summary statistics."""
        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY STATISTICS")
        logger.info("=" * 70)

        for coin in ['LUNA', 'UST']:
            coin_df = df[df['coin'] == coin]
            if coin_df.empty:
                continue

            logger.info(f"\n{coin}:")

            if 'price' in coin_df.columns:
                logger.info(f"  First price:  ${coin_df['price'].iloc[0]:.8f}")
                logger.info(f"  Last price:   ${coin_df['price'].iloc[-1]:.8f}")
                logger.info(f"  Min price:    ${coin_df['price'].min():.8f}")
                logger.info(f"  Max price:    ${coin_df['price'].max():.8f}")

                price_change = (
                    (coin_df['price'].iloc[-1] - coin_df['price'].iloc[0])
                    / coin_df['price'].iloc[0] * 100
                )
                logger.info(f"  Total change: {price_change:+.1f}%")

            if 'volume_binance' in coin_df.columns:
                total_volume = coin_df['volume_binance'].sum()
                logger.info(f"  Total volume: ${total_volume/1e9:.2f}B")

            if coin == 'UST' and 'peg_deviation_bps' in coin_df.columns:
                max_depeg = coin_df['peg_deviation_bps'].max()
                logger.info(f"  Max depeg:    {max_depeg:.0f} bps (${1 - max_depeg/10000:.4f})")

        # Save summary
        summary_file = self.output_dir / "summary_stats.json"
        summary = {
            "collection_date": datetime.now(timezone.utc).isoformat(),
            "period": {
                "start": self.config.start_date.isoformat(),
                "end": self.config.end_date.isoformat(),
                "days": self.config.get_date_range_days()
            },
            "data_points": {
                "total": len(df),
                "luna": len(df[df['coin'] == 'LUNA']),
                "ust": len(df[df['coin'] == 'UST'])
            },
            "timeline": LUNA_CRASH_TIMELINE
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"\n✓ Saved summary to {summary_file}")

    async def run_full_pipeline(self):
        """Run complete data collection and aggregation pipeline."""
        logger.info("\n" + "🚀 " * 35)
        logger.info("STARTING LUNA CRASH DATA COLLECTION PIPELINE")
        logger.info("🚀 " * 35 + "\n")

        # Collect all data
        data = await self.collect_all_data()

        # Merge into DataFrame
        df = self.merge_data_to_dataframe(data)

        # Save unified dataset
        await self.save_unified_dataset(df)

        # Generate summary
        await self.generate_summary_stats(df)

        logger.info("\n" + "=" * 70)
        logger.info("✅ PIPELINE COMPLETE")
        logger.info("=" * 70)
        logger.info(f"\nOutput directory: {self.output_dir}")
        logger.info("\nGenerated files:")
        logger.info("  - luna_crash_unified.csv (main dataset)")
        logger.info("  - luna_crash_unified.parquet (fast loading)")
        logger.info("  - summary_stats.json (metadata)")
        logger.info("  - luna_*_raw.json (raw API responses)")
        logger.info("  - luna_*_klines.json (Binance klines)")


async def main():
    """Main entry point."""
    aggregator = LunaDataAggregator()
    await aggregator.run_full_pipeline()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main())
