"""
Luna Crash Data Collection Configuration

Defines parameters for collecting historical data from the Terra (LUNA/UST) crash
during May 2-13, 2022.

This module configures:
- Time range: May 2-13, 2022 (5 days before crash + crash week)
- Assets: LUNA (Terra Classic), UST (TerraUSD)
- Data sources: CoinGecko, Terra blockchain, Binance
- Metrics: Price, volume, supply, on-chain events
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

# Local import
# from src.common.schema import RiskEvent  # Removed external dependency if not needed here directly,
# but config actually just defines constants.
# Looking at the file content (from memory/previous view), it doesn't import RiskEvent.
# Let's check if it does.



@dataclass
class LunaCrashConfig:
    """Configuration for Luna crash data collection."""

    # Time range: May 2-13, 2022 (UTC)
    # May 2-6: Pre-crash period (baseline)
    # May 7-13: Crash week (UST depeg + LUNA collapse)
    start_date: datetime = datetime(2022, 5, 7, 0, 0, 0, tzinfo=timezone.utc)
    end_date: datetime = datetime(2022, 5, 13, 23, 59, 59, tzinfo=timezone.utc)

    # Assets to track
    assets: Optional[List[Dict[str, str]]] = None

    # Data collection intervals
    price_interval_minutes: int = 5  # Collect price every 5 minutes during crash
    onchain_interval_minutes: int = 10  # Aggregate on-chain data every 10 min

    # CoinGecko API configuration
    coingecko_ids: Optional[Dict[str, str]] = None

    # Terra blockchain configuration
    terra_chain_id: str = "columbus-5"  # Terra Classic chain ID
    terra_rpc_url: str = "https://terra-classic-rpc.publicnode.com"

    # Binance API configuration
    binance_symbols: Optional[List[str]] = None

    # Output configuration
    output_dir: str = "/home/tba/projects/web3/data/luna_crash"

    def __post_init__(self):
        """Initialize default values."""
        if self.assets is None:
            self.assets = [
                {
                    "symbol": "LUNA",
                    "name": "Terra Classic",
                    "type": "volatile",
                    "coingecko_id": "terra-luna",
                    "binance_symbol": "LUNAUSDT"
                },
                {
                    "symbol": "UST",
                    "name": "TerraUSD",
                    "type": "stablecoin",
                    "coingecko_id": "terrausd",
                    "binance_symbol": "USTUSDT"
                }
            ]

        if self.coingecko_ids is None:
            self.coingecko_ids = {
                "LUNA": "terra-luna",
                "UST": "terrausd"
            }

        if self.binance_symbols is None:
            self.binance_symbols = ["LUNAUSDT", "USTUSDT"]

    def get_date_range_days(self) -> int:
        """Calculate number of days in collection period."""
        return (self.end_date - self.start_date).days + 1

    def get_total_intervals(self) -> int:
        """Calculate total number of price collection intervals."""
        total_minutes = (self.end_date - self.start_date).total_seconds() / 60
        return int(total_minutes / self.price_interval_minutes)

    def to_dict(self) -> dict:
        """Export configuration as dictionary."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "duration_days": self.get_date_range_days(),
            "assets": self.assets,
            "price_interval_minutes": self.price_interval_minutes,
            "onchain_interval_minutes": self.onchain_interval_minutes,
            "total_price_intervals": self.get_total_intervals(),
            "terra_chain_id": self.terra_chain_id,
            "terra_rpc_url": self.terra_rpc_url,
            "binance_symbols": self.binance_symbols,
            "output_dir": self.output_dir
        }


# Key events during the crash (for reference/annotation)
LUNA_CRASH_TIMELINE = {
    "2022-05-07": "UST begins to depeg (drops to $0.985)",
    "2022-05-08": "UST falls to $0.60, LUNA drops 50%",
    "2022-05-09": "UST at $0.30, LUNA Foundation Guard deploys BTC reserves",
    "2022-05-10": "UST at $0.20, LUNA down 96%, hyperinflation begins",
    "2022-05-11": "UST at $0.10, LUNA supply explodes from 350M to 6.5T",
    "2022-05-12": "Terra blockchain halted, LUNA price near $0.0001",
    "2022-05-13": "Chain restarted, post-mortem analysis begins"
}


# Critical metrics to track
CRITICAL_METRICS = [
    "ust_peg_deviation",      # How far UST deviated from $1
    "luna_price_usd",         # LUNA price in USD
    "luna_market_cap",        # Total market cap
    "luna_circulating_supply",  # Circulating supply (exploded during crash)
    "trading_volume_24h",     # 24h trading volume
    "ust_mint_burn_net",      # Net UST mints/burns (arbitrage mechanism)
    "luna_mint_burn_net",     # Net LUNA mints/burns (death spiral)
]


# Singleton configuration instance
luna_config = LunaCrashConfig()


if __name__ == "__main__":
    """Print configuration for verification."""
    import json

    print("=" * 70)
    print("LUNA CRASH DATA COLLECTION CONFIGURATION")
    print("=" * 70)
    print(json.dumps(luna_config.to_dict(), indent=2))

    print("\n" + "=" * 70)
    print("CRASH TIMELINE")
    print("=" * 70)
    for date, event in LUNA_CRASH_TIMELINE.items():
        print(f"{date}: {event}")

    print("\n" + "=" * 70)
    print(f"Total data points to collect: {luna_config.get_total_intervals()}")
    print(f"Duration: {luna_config.get_date_range_days()} days")
    print("=" * 70)
