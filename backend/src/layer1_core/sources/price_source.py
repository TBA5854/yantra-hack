"""
Price data source using CoinGecko API.

Fetches real-time price data for stablecoins.
"""

from datetime import datetime
from typing import Optional, List
import aiohttp
import logging

from src.common.schema import RiskEvent
from src.common.config import config
from src.layer1_core.quality.pipeline import backpressure_handler

logger = logging.getLogger(__name__)


class PriceSource:
    """
    Fetches price data from CoinGecko API.

    CoinGecko provides free-tier access with rate limits.
    """

    def __init__(self):
        self.source_config = config.PRICE_SOURCES["coingecko"]
        self.base_url = self.source_config["base_url"]
        self.api_key = self.source_config.get("api_key")
        self.timeout = self.source_config["timeout"]

        # CoinGecko coin IDs
        self.coin_id_map = {
            "USDC": "usd-coin",
            "USDT": "tether",
            "DAI": "dai"
        }

    async def fetch_price(
        self,
        coin: str,
        chain: str = "ethereum"
    ) -> Optional[RiskEvent]:
        """
        Fetch current price for a stablecoin.

        Args:
            coin: Stablecoin symbol (e.g., 'USDC')
            chain: Blockchain name (for event metadata)

        Returns:
            RiskEvent with price data, or None if fetch failed
        """
        coin_id = self.coin_id_map.get(coin)
        if not coin_id:
            logger.warning(f"Unknown coin: {coin}")
            return None

        try:
            event = await backpressure_handler.execute_with_backoff(
                source_id=f"coingecko_{coin}",
                coro_func=self._fetch_price_internal,
                coin=coin,
                coin_id=coin_id,
                chain=chain
            )
            return event

        except Exception as e:
            logger.error(f"Failed to fetch price for {coin}: {e}")
            return None

    async def _fetch_price_internal(
        self,
        coin: str,
        coin_id: str,
        chain: str
    ) -> RiskEvent:
        """Internal method to fetch price from CoinGecko API."""
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_last_updated_at": "true"
        }

        headers = {}
        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()

        # Parse response
        coin_data = data.get(coin_id, {})
        if not coin_data:
            raise ValueError(f"No data returned for {coin_id}")

        price = coin_data.get("usd")
        volume = coin_data.get("usd_24h_vol")
        last_updated = coin_data.get("last_updated_at")

        if price is None:
            raise ValueError(f"No price data for {coin_id}")

        # Create RiskEvent
        event = RiskEvent(
            timestamp=datetime.utcfromtimestamp(last_updated) if last_updated else datetime.utcnow(),
            coin=coin,
            chain=chain,
            source="coingecko",
            price=price,
            volume=volume,
            # Off-chain data - no block information
            block_number=None,
            tx_hash=None
        )

        logger.info(f"Fetched price for {coin}: ${price:.4f}")
        return event

    async def fetch_prices_batch(
        self,
        coins: List[str],
        chain: str = "ethereum"
    ) -> List[RiskEvent]:
        """
        Fetch prices for multiple coins in a single batch.

        More efficient than individual fetches.
        """
        events = []

        # CoinGecko supports batch queries
        coin_ids = [self.coin_id_map.get(coin) for coin in coins]
        coin_ids = [cid for cid in coin_ids if cid]  # Filter None

        if not coin_ids:
            return []

        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
                "include_24hr_vol": "true",
                "include_last_updated_at": "true"
            }

            headers = {}
            if self.api_key:
                headers["x-cg-pro-api-key"] = self.api_key

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            # Parse responses
            for coin in coins:
                coin_id = self.coin_id_map.get(coin)
                if not coin_id:
                    continue

                coin_data = data.get(coin_id, {})
                if not coin_data:
                    continue

                price = coin_data.get("usd")
                volume = coin_data.get("usd_24h_vol")
                last_updated = coin_data.get("last_updated_at")

                if price is None:
                    continue

                event = RiskEvent(
                    timestamp=datetime.utcfromtimestamp(last_updated) if last_updated else datetime.utcnow(),
                    coin=coin,
                    chain=chain,
                    source="coingecko",
                    price=price,
                    volume=volume,
                    block_number=None,
                    tx_hash=None
                )
                events.append(event)

            logger.info(f"Fetched batch prices for {len(events)} coins")

        except Exception as e:
            logger.error(f"Batch price fetch failed: {e}")

        return events


# Singleton instance
price_source = PriceSource()
