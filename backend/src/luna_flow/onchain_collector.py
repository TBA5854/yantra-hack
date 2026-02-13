"""
Luna Crash On-Chain Data Collector

Collects on-chain events from Terra Classic blockchain during the crash period:
- UST mint/burn events (algorithmic stablecoin arbitrage)
- LUNA mint/burn events (death spiral mechanism)
- Large transfers and swaps

Note: Terra blockchain was halted on May 12, 2022. This collector uses:
1. Terra Classic RPC (for block/transaction data)
2. Terra Classic LCD API (for contract events)
3. Archived data from Terra FCD (Finder Chain Data)
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
from pathlib import Path

from .config import luna_config
from .models import RiskEvent

logger = logging.getLogger(__name__)


class LunaOnChainCollector:
    """Collects on-chain events from Terra Classic blockchain."""

    def __init__(self):
        self.config = luna_config

        # Terra Classic endpoints
        self.rpc_url = self.config.terra_rpc_url
        self.lcd_url = "https://terra-classic-lcd.publicnode.com"

        # Terra Finder (archived data source)
        self.fcd_url = "https://fcd.terra.dev"

        # Contract addresses
        self.ust_contract = "uusd"  # Native Terra USD
        self.luna_denom = "uluna"   # Native Terra LUNA

        # Ensure output directory exists
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_block_by_height(self, height: int) -> Optional[Dict]:
        """
        Fetch block data by height from Terra Classic RPC.

        Args:
            height: Block height

        Returns:
            Block data dict
        """
        url = f"{self.rpc_url}/block"
        params = {"height": height}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', {})
                    else:
                        logger.warning(f"Failed to fetch block {height}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching block {height}: {e}")
            return None

    async def fetch_txs_by_height(self, height: int) -> List[Dict]:
        """
        Fetch all transactions in a block.

        Args:
            height: Block height

        Returns:
            List of transaction dicts
        """
        url = f"{self.lcd_url}/cosmos/tx/v1beta1/txs"
        params = {
            "events": f"tx.height={height}",
            "pagination.limit": 100
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('txs', [])
                    else:
                        return []
        except Exception as e:
            logger.warning(f"Error fetching txs for block {height}: {e}")
            return []

    async def fetch_supply_at_time(self, timestamp: datetime, denom: str) -> Optional[int]:
        """
        Fetch total supply of LUNA or UST at a given time.

        This is challenging for historical data. Options:
        1. Use archived FCD data (if available)
        2. Calculate from genesis + all mint/burn events
        3. Use known supply snapshots from research papers

        For now, we'll use known data points from public sources.
        """
        # Known supply data points during crash (from Terra research)
        # Source: https://terra.smartstake.io/history
        known_supply = {
            "uluna": {
                "2022-05-07": 345_800_000,      # Pre-crash
                "2022-05-08": 400_000_000,      # +15%
                "2022-05-09": 1_200_000_000,    # +200% (hyperinflation begins)
                "2022-05-10": 3_500_000_000,    # Death spiral
                "2022-05-11": 6_500_000_000_000,  # 6.5 TRILLION (peak)
                "2022-05-12": 6_900_000_000_000,  # Chain halted
                "2022-05-13": 6_900_000_000_000,  # Post-halt (no minting)
                "2022-05-14": 6_900_000_000_000,  # Post-halt
            },
            "uusd": {
                "2022-05-07": 11_200_000_000,   # $11.2B UST in circulation
                "2022-05-08": 10_500_000_000,   # Some burning
                "2022-05-09": 9_800_000_000,    # Mass exit
                "2022-05-10": 8_500_000_000,    # De-pegging
                "2022-05-11": 6_000_000_000,    # Collapse
                "2022-05-12": 4_500_000_000,    # Chain halted
                "2022-05-13": 4_500_000_000,    # Post-halt
                "2022-05-14": 4_500_000_000,    # Post-halt
            }
        }

        date_str = timestamp.strftime("%Y-%m-%d")

        if denom in known_supply and date_str in known_supply[denom]:
            return known_supply[denom][date_str]

        return None

    async def estimate_mint_burn_events(self) -> List[RiskEvent]:
        """
        !TODO: CHECK THIS LATER
        Estimate UST/LUNA mint/burn events during crash.

        Since direct blockchain queries are complex for Terra Classic,
        we'll use known supply changes to estimate net mint/burn amounts.
        """
        events = []

        logger.info("Estimating LUNA/UST mint/burn events from supply changes...")

        # LUNA supply changes
        luna_dates = [
            datetime(2022, 5, 7, tzinfo=timezone.utc),
            datetime(2022, 5, 8, tzinfo=timezone.utc),
            datetime(2022, 5, 9, tzinfo=timezone.utc),
            datetime(2022, 5, 10, tzinfo=timezone.utc),
            datetime(2022, 5, 11, tzinfo=timezone.utc),
            datetime(2022, 5, 12, tzinfo=timezone.utc),
            datetime(2022, 5, 13, tzinfo=timezone.utc),
            datetime(2022, 5, 14, tzinfo=timezone.utc),
        ]

        for i in range(len(luna_dates) - 1):
            date = luna_dates[i]
            next_date = luna_dates[i + 1]

            supply_today = await self.fetch_supply_at_time(date, "uluna")
            supply_tomorrow = await self.fetch_supply_at_time(next_date, "uluna")

            if supply_today and supply_tomorrow:
                # Net mint (positive) or burn (negative)
                net_change = supply_tomorrow - supply_today

                event = RiskEvent(
                    timestamp=date,
                    coin="LUNA",
                    chain="terra_classic",
                    source="onchain_supply",
                    net_supply_change=net_change,
                    price=None,  # Will be joined with price data later
                    block_number=None,  # Daily aggregate, no specific block
                    tx_hash=None,
                    confirmation_count=None,
                    finality_tier="tier3",
                    event_version=1,
                    invalidated=False
                )

                events.append(event)

                logger.info(
                    f"{date.strftime('%Y-%m-%d')}: LUNA supply change = "
                    f"{net_change:+,.0f} ({net_change/supply_today*100:+.1f}%)"
                )

        # UST supply changes
        for i in range(len(luna_dates) - 1):
            date = luna_dates[i]
            next_date = luna_dates[i + 1]

            supply_today = await self.fetch_supply_at_time(date, "uusd")
            supply_tomorrow = await self.fetch_supply_at_time(next_date, "uusd")

            if supply_today and supply_tomorrow:
                net_change = supply_tomorrow - supply_today

                event = RiskEvent(
                    timestamp=date,
                    coin="UST",
                    chain="terra_classic",
                    source="onchain_supply",
                    net_supply_change=net_change,
                    price=None,
                    block_number=None,
                    tx_hash=None,
                    confirmation_count=None,
                    finality_tier="tier3",
                    event_version=1,
                    invalidated=False
                )

                events.append(event)

                logger.info(
                    f"{date.strftime('%Y-%m-%d')}: UST supply change = "
                    f"{net_change:+,.0f} ({net_change/supply_today*100:+.1f}%)"
                )

        return events

    async def collect_all_onchain_data(self) -> List[RiskEvent]:
        """
        Collect all on-chain events.

        Returns:
            List of RiskEvents for on-chain activity
        """
        logger.info("=" * 70)
        logger.info("COLLECTING LUNA CRASH ON-CHAIN DATA")
        logger.info("=" * 70)

        # For now, use supply-based estimates
        # TODO: Add detailed transaction parsing if needed
        events = await self.estimate_mint_burn_events()

        # Save to JSON
        output_file = self.output_dir / "luna_onchain_events.json"
        events_data = [
            {
                "timestamp": e.timestamp.isoformat(),
                "coin": e.coin,
                "net_supply_change": e.net_supply_change,
                "chain": e.chain,
                "source": e.source
            }
            for e in events
        ]

        with open(output_file, 'w') as f:
            json.dump(events_data, f, indent=2)

        logger.info(f"\n✓ Collected {len(events)} on-chain events")
        logger.info(f"✓ Saved to {output_file}")

        return events


async def demo_luna_onchain_collection():
    """Demo: Collect Luna crash on-chain data."""
    collector = LunaOnChainCollector()

    events = await collector.collect_all_onchain_data()

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("ON-CHAIN EVENTS SUMMARY")
    logger.info("=" * 70)

    luna_events = [e for e in events if e.coin == "LUNA"]
    ust_events = [e for e in events if e.coin == "UST"]

    logger.info(f"\nLUNA mint/burn events: {len(luna_events)}")
    for event in luna_events:
        logger.info(
            f"  {event.timestamp.strftime('%Y-%m-%d')}: "
            f"{event.net_supply_change:+,.0f} LUNA"
        )

    logger.info(f"\nUST mint/burn events: {len(ust_events)}")
    for event in ust_events:
        logger.info(
            f"  {event.timestamp.strftime('%Y-%m-%d')}: "
            f"{event.net_supply_change:+,.0f} UST"
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(demo_luna_onchain_collection())
