"""
Crashed Stablecoin Configuration Registry

Configuration for collecting historical crash data and recent data for 5 failed stablecoins:
- UST (Terra USD) - May 2022 collapse
- USDD (Decentralized USD) - June 2022 depeg
- USDN (Neutrino USD) - April 2022 Waves crash
- BAC (Basis Cash) - January 2021 collapse
- SETD (SetDollar) - February 2021 depeg

For each coin, we collect:
1. Crash week data (7 days during the depeg event)
2. Recent week data (last 7 days - current state)
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List


@dataclass
class CrashedCoinConfig:
    """Configuration for a single crashed stablecoin data collection period"""

    # Identity
    name: str  # e.g., "usdd_crash", "usdd_recent"
    coin: str  # e.g., "USDD", "UST"

    # Time period
    start_date: datetime
    end_date: datetime

    # Data sources
    binance_symbol: Optional[str]  # e.g., "USDDUSDT" (None if delisted)
    coingecko_id: str  # e.g., "usdd"

    # Output
    output_dir: str  # e.g., "data/usdd_crash/"

    # Metadata
    description: str  # Human-readable description


# Configuration registry for all 10 datasets (5 coins × 2 periods)
CRASHED_COIN_CONFIGS = {
    # ========== USDD (Decentralized USD) - June 2022 Depeg ==========
    "usdd_crash": CrashedCoinConfig(
        name="usdd_crash",
        coin="USDD",
        start_date=datetime(2022, 6, 12, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2022, 6, 18, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol="USDDUSDT",
        coingecko_id="usdd",
        output_dir="data/usdd_crash/",
        description="USDD crash week (June 12-18, 2022) - Tron algorithmic stablecoin depeg"
    ),

    "usdd_recent": CrashedCoinConfig(
        name="usdd_recent",
        coin="USDD",
        start_date=datetime(2026, 2, 7, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 2, 14, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol="USDDUSDT",
        coingecko_id="usdd",
        output_dir="data/usdd_recent/",
        description="USDD recent week (Feb 7-14, 2026) - Current state"
    ),

    # ========== USDN (Neutrino USD) - April 2022 Waves Crash ==========
    "usdn_crash": CrashedCoinConfig(
        name="usdn_crash",
        coin="USDN",
        start_date=datetime(2022, 4, 3, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2022, 4, 9, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol=None,  # Not listed on Binance
        coingecko_id="neutrino",
        output_dir="data/usdn_crash/",
        description="USDN crash week (April 3-9, 2022) - Waves blockchain stablecoin collapse"
    ),

    "usdn_recent": CrashedCoinConfig(
        name="usdn_recent",
        coin="USDN",
        start_date=datetime(2026, 2, 7, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 2, 14, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol=None,
        coingecko_id="neutrino",
        output_dir="data/usdn_recent/",
        description="USDN recent week (Feb 7-14, 2026) - Current state"
    ),

    # ========== BAC (Basis Cash) - January 2021 Collapse ==========
    "bac_crash": CrashedCoinConfig(
        name="bac_crash",
        coin="BAC",
        start_date=datetime(2021, 1, 10, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2021, 1, 16, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol=None,  # Never listed on Binance
        coingecko_id="basis-cash",
        output_dir="data/bac_crash/",
        description="BAC crash week (Jan 10-16, 2021) - Basis Cash algorithmic stablecoin failure"
    ),

    "bac_recent": CrashedCoinConfig(
        name="bac_recent",
        coin="BAC",
        start_date=datetime(2026, 2, 7, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 2, 14, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol=None,
        coingecko_id="basis-cash",
        output_dir="data/bac_recent/",
        description="BAC recent week (Feb 7-14, 2026) - Current state (likely dead)"
    ),

    # ========== SETD (SetDollar) - February 2021 Depeg ==========
    "setd_crash": CrashedCoinConfig(
        name="setd_crash",
        coin="SETD",
        start_date=datetime(2021, 2, 14, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2021, 2, 20, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol=None,  # Never listed on Binance
        coingecko_id="set-dollar",
        output_dir="data/setd_crash/",
        description="SETD crash week (Feb 14-20, 2021) - SetDollar algorithmic stablecoin depeg"
    ),

    "setd_recent": CrashedCoinConfig(
        name="setd_recent",
        coin="SETD",
        start_date=datetime(2026, 2, 7, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2026, 2, 14, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol=None,
        coingecko_id="set-dollar",
        output_dir="data/setd_recent/",
        description="SETD recent week (Feb 7-14, 2026) - Current state (likely dead)"
    ),

    # ==============================================
    # LUNA/UST - Terra Ecosystem Collapse (May 2022)
    # ==============================================

    # LUNA Crash Week (May 7-13, 2022)
    "luna_crash": CrashedCoinConfig(
        name="luna_crash",
        coin="LUNA",
        start_date=datetime(2022, 5, 7, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2022, 5, 13, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol="LUNAUSDT",
        coingecko_id="terra-luna",
        output_dir="data/luna_crash/",
        description="LUNA crash week (May 7-13, 2022) - Terra ecosystem collapse"
    ),

    # UST Crash Week (May 7-13, 2022)
    "ust_crash": CrashedCoinConfig(
        name="ust_crash",
        coin="UST",
        start_date=datetime(2022, 5, 7, 0, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2022, 5, 13, 23, 59, 59, tzinfo=timezone.utc),
        binance_symbol="USTUSDT",
        coingecko_id="terrausd",
        output_dir="data/luna_crash/",  # Same directory as LUNA
        description="UST crash week (May 7-13, 2022) - Terra stablecoin depeg"
    ),
}


def get_config(name: str) -> CrashedCoinConfig:
    """Get configuration by name"""
    if name not in CRASHED_COIN_CONFIGS:
        raise ValueError(f"Unknown config: {name}. Available: {list(CRASHED_COIN_CONFIGS.keys())}")
    return CRASHED_COIN_CONFIGS[name]


def get_all_crash_configs() -> List[CrashedCoinConfig]:
    """Get all crash period configs (excludes recent)"""
    return [cfg for name, cfg in CRASHED_COIN_CONFIGS.items() if "_crash" in name]


def get_all_recent_configs() -> List[CrashedCoinConfig]:
    """Get all recent period configs"""
    return [cfg for name, cfg in CRASHED_COIN_CONFIGS.items() if "_recent" in name]


def get_configs_for_coin(coin: str) -> List[CrashedCoinConfig]:
    """Get all configs for a specific coin (crash + recent)"""
    return [cfg for cfg in CRASHED_COIN_CONFIGS.values() if cfg.coin == coin]


def print_config_summary():
    """Print summary of all configurations"""
    print("=" * 70)
    print("CRASHED STABLECOIN DATA COLLECTION CONFIGURATIONS")
    print("=" * 70)

    for name, config in CRASHED_COIN_CONFIGS.items():
        print(f"\n📊 {name.upper()}")
        print(f"   Coin: {config.coin}")
        print(f"   Period: {config.start_date.date()} to {config.end_date.date()}")
        print(f"   Binance: {config.binance_symbol or 'N/A (use CoinGecko only)'}")
        print(f"   CoinGecko ID: {config.coingecko_id}")
        print(f"   Output: {config.output_dir}")
        print(f"   Description: {config.description}")

    print("\n" + "=" * 70)
    print(f"Total configurations: {len(CRASHED_COIN_CONFIGS)}")
    print(f"Crash periods: {len(get_all_crash_configs())}")
    print(f"Recent periods: {len(get_all_recent_configs())}")
    print("=" * 70)


if __name__ == "__main__":
    print_config_summary()
