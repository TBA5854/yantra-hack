"""
Window State Machine for time-windowed aggregation.

State transitions: OPEN → PROVISIONAL → FINAL

- OPEN: Accepting new events
- PROVISIONAL: Window closed, waiting for finality
- FINAL: All events finalized, window is immutable
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import asyncio
import logging

from src.common.schema import RiskEvent, WindowState, AggregatedRiskSnapshot
from src.common.config import config
from src.layer1_core.tcs.calculator import tcs_calculator
from src.layer1_core.finality.tracker import finality_registry

logger = logging.getLogger(__name__)


class TimeWindow:
    """
    Represents a single time window for event aggregation.

    Each window has:
    - A unique ID (ISO timestamp of window start)
    - A state (OPEN, PROVISIONAL, FINAL)
    - A collection of events
    - Transition timestamps
    """

    def __init__(
        self,
        window_id: str,
        window_start: datetime,
        window_end: datetime
    ):
        self.window_id = window_id
        self.window_start = window_start
        self.window_end = window_end
        self.state = WindowState.OPEN

        # Events in this window
        self.events: List[RiskEvent] = []

        # State transition timestamps
        self.opened_at = datetime.utcnow()
        self.closed_at: Optional[datetime] = None
        self.provisional_at: Optional[datetime] = None
        self.finalized_at: Optional[datetime] = None

        # Aggregated snapshot (produced when window transitions to FINAL)
        self.snapshot: Optional[AggregatedRiskSnapshot] = None

    def add_event(self, event: RiskEvent):
        """Add an event to this window (only if OPEN)."""
        if self.state != WindowState.OPEN:
            logger.warning(
                f"Cannot add event to window {self.window_id} - "
                f"window is {self.state.value}"
            )
            return

        event.window_id = self.window_id
        event.window_state = self.state.value
        event.window_start = self.window_start
        event.window_end = self.window_end
        self.events.append(event)

    def is_expired(self, current_time: datetime) -> bool:
        """Check if window should be closed."""
        return current_time >= self.window_end

    def can_transition_to_provisional(self, current_time: datetime) -> bool:
        """Check if window can transition to PROVISIONAL."""
        if self.state != WindowState.OPEN:
            return False

        # Window must be expired
        if not self.is_expired(current_time):
            return False

        # Must wait for provisional delay after window close
        delay = timedelta(seconds=config.WINDOW_CONFIG["provisional_delay_sec"])
        return current_time >= self.window_end + delay

    def can_transition_to_final(self, current_time: datetime) -> bool:
        """Check if window can transition to FINAL."""
        if self.state != WindowState.PROVISIONAL:
            return False

        # Must wait for finalization delay
        delay = timedelta(seconds=config.WINDOW_CONFIG["finalization_delay_sec"])
        return current_time >= self.window_end + delay

    def all_events_finalized(self) -> bool:
        """Check if all events in window have reached tier3 finality."""
        if not self.events:
            return True

        return all(e.is_finalized or e.invalidated for e in self.events)

    def transition_to_provisional(self):
        """Transition window from OPEN to PROVISIONAL."""
        logger.info(f"Window {self.window_id} transitioning to PROVISIONAL")
        self.state = WindowState.PROVISIONAL
        self.closed_at = datetime.utcnow()
        self.provisional_at = datetime.utcnow()

        # Update all events' window state
        for event in self.events:
            event.window_state = WindowState.PROVISIONAL.value

    def transition_to_final(self):
        """Transition window from PROVISIONAL to FINAL."""
        logger.info(f"Window {self.window_id} transitioning to FINAL")
        self.state = WindowState.FINAL
        self.finalized_at = datetime.utcnow()

        # Update all events' window state
        for event in self.events:
            event.window_state = WindowState.FINAL.value

        # Generate aggregated snapshot
        self.snapshot = self._generate_snapshot()

    def _generate_snapshot(self) -> AggregatedRiskSnapshot:
        """Generate aggregated risk snapshot from window events."""
        # Filter out invalidated events
        valid_events = [e for e in self.events if not e.invalidated]

        if not valid_events:
            logger.warning(f"No valid events in window {self.window_id}")
            return AggregatedRiskSnapshot(
                window_id=self.window_id,
                window_state=WindowState.FINAL.value,
                timestamp=datetime.utcnow()
            )

        # Extract coin and chains
        coin = valid_events[0].coin if valid_events else ""
        chains = list(set(e.chain for e in valid_events))
        sources = list(set(e.source for e in valid_events))

        # Aggregate price data
        prices = [e.price for e in valid_events if e.price is not None]
        avg_price = sum(prices) / len(prices) if prices else None
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None

        # Aggregate liquidity
        liquidities = [e.liquidity_depth for e in valid_events if e.liquidity_depth is not None]
        total_liquidity = sum(liquidities) if liquidities else None

        # Aggregate volume
        volumes = [e.volume for e in valid_events if e.volume is not None]
        total_volume = sum(volumes) if volumes else None

        # Supply changes
        supply_changes = [e.net_supply_change for e in valid_events if e.net_supply_change is not None]
        net_supply_change = sum(supply_changes) if supply_changes else None

        # Volatility (max across sources)
        volatilities = [e.market_volatility for e in valid_events if e.market_volatility is not None]
        market_volatility = max(volatilities) if volatilities else None

        # Sentiment (average)
        sentiments = [e.sentiment_score for e in valid_events if e.sentiment_score is not None]
        sentiment_score = sum(sentiments) / len(sentiments) if sentiments else None

        # Calculate TCS for the aggregated snapshot
        tcs_breakdown = tcs_calculator.calculate_tcs(valid_events)

        # Depeg detection
        is_depegged = False
        depeg_severity = None
        if avg_price is not None:
            depeg_distance = abs(avg_price - 1.0)
            depeg_threshold = config.COINS.get(coin, None)
            if depeg_threshold:
                is_depegged = depeg_distance >= depeg_threshold.depeg_threshold
                depeg_severity = depeg_distance

        snapshot = AggregatedRiskSnapshot(
            timestamp=datetime.utcnow(),
            coin=coin,
            chains=chains,
            window_id=self.window_id,
            window_state=WindowState.FINAL.value,
            avg_price=avg_price,
            min_price=min_price,
            max_price=max_price,
            total_liquidity=total_liquidity,
            total_volume=total_volume,
            net_supply_change=net_supply_change,
            market_volatility=market_volatility,
            sentiment_score=sentiment_score,
            temporal_confidence=tcs_breakdown.temporal_confidence,
            confidence_breakdown={
                "finality_weight": tcs_breakdown.finality_weight,
                "chain_confidence": tcs_breakdown.chain_confidence,
                "completeness": tcs_breakdown.completeness,
                "staleness_penalty": tcs_breakdown.staleness_penalty
            },
            num_events_aggregated=len(valid_events),
            sources_included=sources,
            event_ids=[e.event_id for e in valid_events],
            is_depegged=is_depegged,
            depeg_severity=depeg_severity
        )

        logger.info(
            f"Generated snapshot for window {self.window_id}: "
            f"coin={coin}, tcs={snapshot.temporal_confidence:.3f}, "
            f"events={len(valid_events)}, depegged={is_depegged}"
        )

        return snapshot


class WindowManager:
    """
    Manages time windows and state transitions.

    Responsibilities:
    1. Create new windows at regular intervals
    2. Route events to appropriate windows
    3. Transition windows through states (OPEN → PROVISIONAL → FINAL)
    4. Monitor finality and trigger transitions
    5. Generate aggregated snapshots
    """

    def __init__(self, window_size_sec: int = 300):
        self.window_size_sec = window_size_sec
        self.windows: Dict[str, TimeWindow] = {}
        self.current_window: Optional[TimeWindow] = None

    def get_window_id(self, timestamp: datetime) -> str:
        """
        Generate window ID from timestamp.

        Windows are aligned to fixed intervals (e.g., :00, :05, :10, etc.)
        """
        # Align timestamp to window boundary
        epoch = int(timestamp.timestamp())
        window_start_epoch = (epoch // self.window_size_sec) * self.window_size_sec
        window_start = datetime.utcfromtimestamp(window_start_epoch)
        return window_start.isoformat()

    def get_or_create_window(self, timestamp: datetime) -> TimeWindow:
        """Get existing window or create new one for timestamp."""
        window_id = self.get_window_id(timestamp)

        if window_id not in self.windows:
            # Create new window
            epoch = int(timestamp.timestamp())
            window_start_epoch = (epoch // self.window_size_sec) * self.window_size_sec
            window_start = datetime.utcfromtimestamp(window_start_epoch)
            window_end = window_start + timedelta(seconds=self.window_size_sec)

            window = TimeWindow(window_id, window_start, window_end)
            self.windows[window_id] = window
            self.current_window = window

            logger.info(
                f"Created new window {window_id} "
                f"[{window_start.isoformat()} - {window_end.isoformat()}]"
            )

        return self.windows[window_id]

    def add_event(self, event: RiskEvent):
        """Add event to appropriate window based on timestamp."""
        window = self.get_or_create_window(event.timestamp)
        window.add_event(event)

    async def run_state_machine(self, check_interval_sec: int = 10):
        """
        Main state machine loop.

        Continuously checks windows and transitions them through states.
        """
        logger.info("Starting window state machine")

        while True:
            current_time = datetime.utcnow()

            # Check all windows for state transitions
            for window_id, window in list(self.windows.items()):
                await self._process_window(window, current_time)

            await asyncio.sleep(check_interval_sec)

    async def _process_window(self, window: TimeWindow, current_time: datetime):
        """Process a single window and transition if necessary."""

        # OPEN → PROVISIONAL transition
        if window.can_transition_to_provisional(current_time):
            window.transition_to_provisional()

        # PROVISIONAL state: update event finality
        if window.state == WindowState.PROVISIONAL:
            await self._update_window_finality(window)

        # PROVISIONAL → FINAL transition
        if window.can_transition_to_final(current_time):
            # Check if all events are finalized
            if window.all_events_finalized():
                window.transition_to_final()
                logger.info(
                    f"Window {window.window_id} finalized with "
                    f"{len(window.events)} events, "
                    f"TCS={window.snapshot.temporal_confidence:.3f}"
                )
            else:
                # Grace period expired but not all events finalized
                # This can happen with slow chains or reorgs
                unfinalized = sum(1 for e in window.events if not e.is_finalized)
                logger.warning(
                    f"Window {window.window_id} grace period expired but "
                    f"{unfinalized} events not finalized. Extending grace period."
                )

    async def _update_window_finality(self, window: TimeWindow):
        """Update finality for all events in a window."""
        tasks = []
        for event in window.events:
            if not event.is_finalized and not event.invalidated:
                tasks.append(finality_registry.update_event_finality(event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_finalized_snapshots(self) -> List[AggregatedRiskSnapshot]:
        """Get all finalized snapshots."""
        snapshots = []
        for window in self.windows.values():
            if window.state == WindowState.FINAL and window.snapshot:
                snapshots.append(window.snapshot)
        return snapshots

    def cleanup_old_windows(self, max_age_hours: int = 24):
        """Remove old finalized windows to free memory."""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        to_remove = []

        for window_id, window in self.windows.items():
            if window.state == WindowState.FINAL and window.finalized_at < cutoff:
                to_remove.append(window_id)

        for window_id in to_remove:
            del self.windows[window_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old windows")
