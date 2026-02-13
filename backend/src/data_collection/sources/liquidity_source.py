"""
Liquidity data source using Uniswap V3 pools.

Fetches liquidity depth from DEX pools to measure market depth.
"""

from datetime import datetime
from typing import Optional, List, Dict
import aiohttp
import logging

from src.common.schema import RiskEvent
from src.common.config import config
from src.data_collection.quality.pipeline import backpressure_handler

logger = logging.getLogger(__name__)


class LiquiditySource:
    """
    Fetches liquidity data from Uniswap V3 via The Graph.

    Measures available liquidity depth for stablecoins.
    """

    def __init__(self):
        self.source_config = config.LIQUIDITY_SOURCES["uniswap_v3"]
        self.subgraph_url = self.source_config["subgraph_url"]
        self.timeout = 10

        # Pool addresses for major stablecoin pairs (USDC/USDT, etc.)
        self.pool_addresses = {
            "USDC": "0x3416cf6c708da44db2624d63ea0aaef7113527c6",  # USDC/USDT 0.01% pool
            "USDT": "0x3416cf6c708da44db2624d63ea0aaef7113527c6",  # USDC/USDT 0.01% pool
            "DAI": "0x5777d92f208679db4b9778590fa3cab3ac9e2168",   # DAI/USDC 0.01% pool
        }

    async def fetch_liquidity(
        self,
        coin: str,
        chain: str = "ethereum"
    ) -> Optional[RiskEvent]:
        """
        Fetch liquidity depth for a stablecoin.

        Args:
            coin: Stablecoin symbol (e.g., 'USDC')
            chain: Blockchain name

        Returns:
            RiskEvent with liquidity data, or None if fetch failed
        """
        if chain not in self.source_config["chains"]:
            logger.warning(f"Chain {chain} not supported for Uniswap V3")
            return None

        pool_address = self.pool_addresses.get(coin)
        if not pool_address:
            logger.warning(f"No pool address configured for {coin}")
            return None

        try:
            event = await backpressure_handler.execute_with_backoff(
                source_id=f"uniswap_v3_{coin}",
                coro_func=self._fetch_liquidity_internal,
                coin=coin,
                pool_address=pool_address,
                chain=chain
            )
            return event

        except Exception as e:
            logger.error(f"Failed to fetch liquidity for {coin}: {e}")
            return None

    async def _fetch_liquidity_internal(
        self,
        coin: str,
        pool_address: str,
        chain: str
    ) -> RiskEvent:
        """Internal method to fetch liquidity from The Graph."""

        # GraphQL query for pool liquidity
        query = """
        query GetPoolLiquidity($poolAddress: String!) {
          pool(id: $poolAddress) {
            liquidity
            volumeUSD
            totalValueLockedUSD
            token0 {
              symbol
            }
            token1 {
              symbol
            }
          }
        }
        """

        variables = {
            "poolAddress": pool_address.lower()
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.subgraph_url,
                json={"query": query, "variables": variables},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()

        # Parse response
        if "errors" in data:
            raise ValueError(f"GraphQL errors: {data['errors']}")

        pool_data = data.get("data", {}).get("pool")
        if not pool_data:
            raise ValueError(f"No pool data for {pool_address}")

        liquidity = float(pool_data.get("liquidity", 0))
        tvl = float(pool_data.get("totalValueLockedUSD", 0))
        volume = float(pool_data.get("volumeUSD", 0))

        # Create RiskEvent
        event = RiskEvent(
            timestamp=datetime.utcnow(),
            coin=coin,
            chain=chain,
            source="uniswap_v3",
            liquidity_depth=tvl,  # Use TVL as liquidity depth proxy
            volume=volume,
            # Off-chain data - no block information
            block_number=None,
            tx_hash=None
        )

        logger.info(f"Fetched liquidity for {coin}: TVL=${tvl:,.0f}, Volume=${volume:,.0f}")
        return event

    async def fetch_liquidity_batch(
        self,
        coins: List[str],
        chain: str = "ethereum"
    ) -> List[RiskEvent]:
        """
        Fetch liquidity for multiple coins.

        Note: The Graph doesn't support batch queries well,
        so we fetch sequentially with backpressure handling.
        """
        events = []

        for coin in coins:
            event = await self.fetch_liquidity(coin, chain)
            if event:
                events.append(event)

        logger.info(f"Fetched liquidity for {len(events)} coins")
        return events


class MockLiquiditySource:
    """
    Mock liquidity source for testing without The Graph dependency.

    Generates realistic synthetic liquidity data.
    """

    def __init__(self):
        # Realistic TVL ranges for major stablecoins
        self.typical_tvl = {
            "USDC": 500_000_000,  # $500M
            "USDT": 300_000_000,  # $300M
            "DAI": 100_000_000,   # $100M
        }

    async def fetch_liquidity(
        self,
        coin: str,
        chain: str = "ethereum"
    ) -> Optional[RiskEvent]:
        """Fetch mock liquidity data."""
        import random

        base_tvl = self.typical_tvl.get(coin, 50_000_000)

        # Add ±10% variance
        tvl = base_tvl * (1.0 + random.uniform(-0.1, 0.1))

        # Volume is typically 5-10% of TVL daily
        volume = tvl * random.uniform(0.05, 0.10)

        event = RiskEvent(
            timestamp=datetime.utcnow(),
            coin=coin,
            chain=chain,
            source="uniswap_v3_mock",
            liquidity_depth=tvl,
            volume=volume,
            block_number=None,
            tx_hash=None
        )

        logger.info(f"[MOCK] Fetched liquidity for {coin}: TVL=${tvl:,.0f}")
        return event

    async def fetch_liquidity_batch(
        self,
        coins: List[str],
        chain: str = "ethereum"
    ) -> List[RiskEvent]:
        """Fetch mock liquidity for multiple coins."""
        events = []
        for coin in coins:
            event = await self.fetch_liquidity(coin, chain)
            if event:
                events.append(event)
        return events


# Use real Uniswap V3 data from The Graph subgraph
try:
    liquidity_source = LiquiditySource()
    logger.info("✅ Using real Uniswap V3 liquidity data from The Graph")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize real liquidity source: {e}, falling back to mock")
    liquidity_source = MockLiquiditySource()
