"""
Volatility calculator for stablecoins.

Calculates rolling volatility metrics from price history.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import deque
import statistics
import logging

from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


class VolatilityCalculator:
    """
    Calculates market volatility for stablecoins.

    Uses rolling window of price data to compute standard deviation.
    """

    def __init__(self, window_size: int = 24):
        """
        Initialize volatility calculator.

        Args:
            window_size: Number of data points for rolling window (default: 24 hours)
        """
        self.window_size = window_size

        # Store recent prices for each coin
        self.price_history: Dict[str, deque] = {}

    def add_price_point(self, coin: str, price: float, timestamp: datetime):
        """Add a price point to the history."""
        if coin not in self.price_history:
            self.price_history[coin] = deque(maxlen=self.window_size)

        self.price_history[coin].append((timestamp, price))

    def calculate_volatility(
        self,
        coin: str,
        chain: str = "ethereum"
    ) -> Optional[RiskEvent]:
        """
        Calculate volatility for a coin based on recent price history.

        Args:
            coin: Stablecoin symbol
            chain: Blockchain name

        Returns:
            RiskEvent with volatility metric, or None if insufficient data
        """
        if coin not in self.price_history:
            logger.debug(f"No price history for {coin}")
            return None

        prices = [price for _, price in self.price_history[coin]]

        if len(prices) < 2:
            logger.debug(f"Insufficient price data for {coin} volatility (need ≥2 points)")
            return None

        # Calculate standard deviation (volatility)
        try:
            volatility = statistics.stdev(prices)
        except statistics.StatisticsError:
            logger.warning(f"Could not calculate volatility for {coin}")
            return None

        # Calculate additional metrics
        mean_price = statistics.mean(prices)
        price_range = max(prices) - min(prices)

        # Relative volatility (coefficient of variation)
        relative_volatility = (volatility / mean_price) if mean_price > 0 else 0

        event = RiskEvent(
            timestamp=datetime.utcnow(),
            coin=coin,
            chain=chain,
            source="volatility_calculator",
            market_volatility=relative_volatility,  # Relative volatility (%)
            price=mean_price,  # Include average price for context
            # Metadata
            block_number=None,
            tx_hash=None
        )

        logger.info(
            f"Calculated volatility for {coin}: "
            f"σ={volatility:.6f} ({relative_volatility*100:.4f}%), "
            f"range=${price_range:.6f}, n={len(prices)}"
        )

        return event

    def calculate_volatility_batch(
        self,
        coins: List[str],
        chain: str = "ethereum"
    ) -> List[RiskEvent]:
        """Calculate volatility for multiple coins."""
        events = []

        for coin in coins:
            event = self.calculate_volatility(coin, chain)
            if event:
                events.append(event)

        return events

    def get_history_size(self, coin: str) -> int:
        """Get number of price points in history for a coin."""
        if coin not in self.price_history:
            return 0
        return len(self.price_history[coin])


class MockVolatilitySource:
    """
    Mock volatility source for testing.

    Generates realistic synthetic volatility data.
    """

    def __init__(self):
        # Typical volatility for stablecoins (very low)
        self.typical_volatility = {
            "USDC": 0.0005,  # 0.05% daily volatility
            "USDT": 0.0008,  # 0.08% daily volatility
            "DAI": 0.0006,   # 0.06% daily volatility
        }

    async def calculate_volatility(
        self,
        coin: str,
        chain: str = "ethereum"
    ) -> Optional[RiskEvent]:
        """Generate mock volatility data."""
        import random

        base_volatility = self.typical_volatility.get(coin, 0.0007)

        # Add some random variation (±20%)
        volatility = base_volatility * (1.0 + random.uniform(-0.2, 0.2))

        event = RiskEvent(
            timestamp=datetime.utcnow(),
            coin=coin,
            chain=chain,
            source="volatility_mock",
            market_volatility=volatility,
            block_number=None,
            tx_hash=None
        )

        logger.info(f"[MOCK] Calculated volatility for {coin}: {volatility*100:.4f}%")
        return event

    async def calculate_volatility_batch(
        self,
        coins: List[str],
        chain: str = "ethereum"
    ) -> List[RiskEvent]:
        """Generate mock volatility for multiple coins."""
        events = []
        for coin in coins:
            event = await self.calculate_volatility(coin, chain)
            if event:
                events.append(event)
        return events


# Create singleton instances
volatility_calculator = VolatilityCalculator(window_size=24)
volatility_source = MockVolatilitySource()
