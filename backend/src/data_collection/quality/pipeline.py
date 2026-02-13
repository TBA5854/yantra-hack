"""
Data quality pipeline for multi-source risk data.

Implements:
1. Normalization - standardize data formats and bounds
2. Deduplication - remove duplicate events within time window
3. Outlier detection - flag statistical outliers using z-score
4. Backpressure handling - exponential backoff for API failures
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from collections import defaultdict
import statistics
import logging
import asyncio

from src.common.schema import RiskEvent
from src.common.config import config

logger = logging.getLogger(__name__)


class DataQualityPipeline:
    """
    Comprehensive data quality pipeline for risk events.

    Processes events through multiple quality stages before aggregation.
    """

    def __init__(self):
        self.quality_config = config.QUALITY_CONFIG

        # Deduplication tracking
        self.seen_events: Dict[str, datetime] = {}  # event_signature -> last_seen_time

        # Outlier detection parameters
        self.outlier_threshold = self.quality_config["outlier_z_threshold"]

        # Price bounds for stablecoins
        self.price_min, self.price_max = self.quality_config["price_bounds"]

    def process_events(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """
        Process a batch of events through all quality stages.

        Pipeline stages:
        1. Normalization
        2. Deduplication
        3. Outlier detection

        Returns:
            List of quality-processed events (some may be filtered out)
        """
        if not events:
            return []

        logger.debug(f"Processing {len(events)} events through quality pipeline")

        # Stage 1: Normalize
        events = self._normalize_events(events)

        # Stage 2: Deduplicate
        events = self._deduplicate_events(events)

        # Stage 3: Detect outliers
        events = self._detect_outliers(events)

        logger.info(
            f"Quality pipeline processed {len(events)} events "
            f"(outliers: {sum(1 for e in events if e.is_outlier)})"
        )

        return events

    def _normalize_events(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """
        Stage 1: Normalize event data.

        - Clamp prices to reasonable bounds
        - Convert timestamps to UTC
        - Standardize coin symbols (uppercase)
        - Standardize chain names (lowercase)
        """
        normalized = []

        for event in events:
            # Normalize coin symbol
            event.coin = event.coin.upper() if event.coin else ""

            # Normalize chain name
            event.chain = event.chain.lower() if event.chain else ""

            # Normalize price (clamp to bounds for stablecoins)
            if event.price is not None:
                if event.price < self.price_min:
                    logger.warning(
                        f"Clamping low price {event.price:.4f} to {self.price_min} "
                        f"for {event.coin} from {event.source}"
                    )
                    event.price = self.price_min
                elif event.price > self.price_max:
                    logger.warning(
                        f"Clamping high price {event.price:.4f} to {self.price_max} "
                        f"for {event.coin} from {event.source}"
                    )
                    event.price = self.price_max

            # Ensure timestamp is UTC
            if event.timestamp.tzinfo is not None:
                event.timestamp = event.timestamp.replace(tzinfo=None)

            # Calculate quality score (starts at 1.0)
            event.quality_score = 1.0

            normalized.append(event)

        return normalized

    def _deduplicate_events(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """
        Stage 2: Remove duplicate events.

        Deduplication strategy:
        - Group events by (coin, chain, source, data_type)
        - Within each group, if multiple events have identical data within
          dedup_window_sec, keep only the most recent one
        - Track deduplication count for transparency
        """
        dedup_window = timedelta(seconds=self.quality_config["dedup_window_sec"])
        current_time = datetime.utcnow()

        # Clean up old seen events
        cutoff_time = current_time - dedup_window
        self.seen_events = {
            sig: ts for sig, ts in self.seen_events.items()
            if ts > cutoff_time
        }

        unique_events = []
        duplicate_count = 0

        for event in events:
            # Generate event signature
            signature = self._event_signature(event)

            # Check if we've seen this event recently
            if signature in self.seen_events:
                last_seen = self.seen_events[signature]
                if event.timestamp - last_seen < dedup_window:
                    duplicate_count += 1
                    logger.debug(f"Duplicate event detected: {signature}")
                    continue

            # Not a duplicate - keep it
            self.seen_events[signature] = event.timestamp
            unique_events.append(event)

        if duplicate_count > 0:
            logger.info(f"Filtered {duplicate_count} duplicate events")

        return unique_events

    def _detect_outliers(self, events: List[RiskEvent]) -> List[RiskEvent]:
        """
        Stage 3: Detect statistical outliers using z-score method.

        For each metric (price, liquidity, volume, etc.), calculate z-score.
        If |z-score| > threshold, flag as outlier but don't remove.
        """
        if len(events) < 3:
            # Not enough data for meaningful outlier detection
            return events

        # Group events by (coin, chain) for per-market outlier detection
        markets: Dict[tuple, List[RiskEvent]] = defaultdict(list)
        for event in events:
            markets[(event.coin, event.chain)].append(event)

        # Detect outliers within each market
        for market_key, market_events in markets.items():
            self._detect_outliers_in_market(market_events)

        return events

    def _detect_outliers_in_market(self, events: List[RiskEvent]):
        """Detect outliers within a single market (coin + chain)."""
        if len(events) < 3:
            return

        # Price outliers
        prices = [e.price for e in events if e.price is not None]
        if len(prices) >= 3:
            mean_price = statistics.mean(prices)
            stdev_price = statistics.stdev(prices)

            if stdev_price > 0:
                for event in events:
                    if event.price is not None:
                        z_score = abs(event.price - mean_price) / stdev_price
                        if z_score > self.outlier_threshold:
                            event.is_outlier = True
                            event.quality_score *= 0.5  # Penalize outliers
                            logger.warning(
                                f"Price outlier detected: {event.coin} on {event.chain} "
                                f"price={event.price:.4f} (z={z_score:.2f})"
                            )

        # Liquidity outliers
        liquidities = [e.liquidity_depth for e in events if e.liquidity_depth is not None]
        if len(liquidities) >= 3:
            mean_liq = statistics.mean(liquidities)
            stdev_liq = statistics.stdev(liquidities)

            if stdev_liq > 0:
                for event in events:
                    if event.liquidity_depth is not None:
                        z_score = abs(event.liquidity_depth - mean_liq) / stdev_liq
                        if z_score > self.outlier_threshold:
                            event.is_outlier = True
                            event.quality_score *= 0.5

    def _event_signature(self, event: RiskEvent) -> str:
        """
        Generate a unique signature for deduplication.

        Signature includes coin, chain, source, and key data values.
        """
        parts = [
            event.coin,
            event.chain,
            event.source,
            f"{event.price:.6f}" if event.price is not None else "none",
            f"{event.liquidity_depth:.2f}" if event.liquidity_depth is not None else "none",
            f"{event.volume:.2f}" if event.volume is not None else "none"
        ]
        return "|".join(parts)


class BackpressureHandler:
    """
    Handles API rate limits and failures with exponential backoff.

    Implements circuit breaker pattern to prevent cascading failures.
    """

    def __init__(self):
        self.config = config.QUALITY_CONFIG

        # Track failures per source
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.circuit_open: Dict[str, datetime] = {}  # source -> circuit_open_time

        # Backoff parameters
        self.max_retries = self.config["max_retry_attempts"]
        self.backoff_base = self.config["retry_backoff_base"]
        self.circuit_breaker_threshold = self.config["circuit_breaker_threshold"]

    async def execute_with_backoff(
        self,
        source_id: str,
        coro_func,
        *args,
        **kwargs
    ):
        """
        Execute an async function with exponential backoff on failure.

        Args:
            source_id: Identifier for the data source (for tracking failures)
            coro_func: Async function to execute
            *args, **kwargs: Arguments for coro_func

        Returns:
            Result of coro_func or None if all retries failed

        Raises:
            CircuitBreakerOpen: If circuit breaker is open for this source
        """
        # Check circuit breaker
        if self._is_circuit_open(source_id):
            logger.warning(f"Circuit breaker OPEN for {source_id}, skipping request")
            raise CircuitBreakerOpen(f"Circuit breaker open for {source_id}")

        for attempt in range(self.max_retries):
            try:
                result = await coro_func(*args, **kwargs)

                # Success - reset failure count
                if self.failure_counts[source_id] > 0:
                    logger.info(f"Source {source_id} recovered after {self.failure_counts[source_id]} failures")
                self.failure_counts[source_id] = 0

                return result

            except Exception as e:
                self.failure_counts[source_id] += 1

                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for {source_id}: {e}"
                )

                # Check if we should open circuit breaker
                if self.failure_counts[source_id] >= self.circuit_breaker_threshold:
                    self._open_circuit(source_id)
                    raise CircuitBreakerOpen(f"Circuit breaker opened for {source_id}")

                # Last attempt - don't wait
                if attempt == self.max_retries - 1:
                    logger.error(f"All retries exhausted for {source_id}")
                    return None

                # Exponential backoff
                backoff_sec = self.backoff_base ** attempt
                logger.info(f"Backing off {backoff_sec}s before retry...")
                await asyncio.sleep(backoff_sec)

        return None

    def _is_circuit_open(self, source_id: str) -> bool:
        """Check if circuit breaker is currently open for a source."""
        if source_id not in self.circuit_open:
            return False

        # Circuit stays open for 5 minutes
        circuit_duration = timedelta(minutes=5)
        if datetime.utcnow() - self.circuit_open[source_id] > circuit_duration:
            # Close circuit after timeout
            logger.info(f"Closing circuit breaker for {source_id}")
            del self.circuit_open[source_id]
            self.failure_counts[source_id] = 0
            return False

        return True

    def _open_circuit(self, source_id: str):
        """Open circuit breaker for a source."""
        logger.error(
            f"Opening circuit breaker for {source_id} "
            f"after {self.failure_counts[source_id]} consecutive failures"
        )
        self.circuit_open[source_id] = datetime.utcnow()


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open for a data source."""
    pass


# Singleton instances
quality_pipeline = DataQualityPipeline()
backpressure_handler = BackpressureHandler()
