"""
Temporal Confidence Score (TCS) Calculator.

TCS quantifies epistemic uncertainty in risk assessments by combining:
1. Finality weight - weighted average of event finality across sources
2. Chain confidence - minimum finality across all contributing chains
3. Completeness - fraction of expected data sources present
4. Staleness penalty - penalty for data age

Formula: TCS = (finality_weight * chain_confidence * completeness) / staleness_penalty
"""

from datetime import datetime
from typing import List, Dict, Optional
import logging

from src.common.schema import RiskEvent, ConfidenceBreakdown, FinalityTier
from src.common.config import config

logger = logging.getLogger(__name__)


class TCSCalculator:
    """
    Calculates Temporal Confidence Scores for risk events.

    The TCS is a meta-awareness metric that tells us how confident
    we should be in our risk assessment given the current state of
    blockchain finality and data availability.
    """

    def __init__(self):
        self.tcs_config = config.TCS_CONFIG
        self.expected_sources = set(self.tcs_config["expected_sources"])
        self.source_importance = self.tcs_config["source_importance"]
        self.staleness_thresholds = self.tcs_config["staleness_thresholds"]

    def calculate_tcs(
        self,
        events: List[RiskEvent],
        timestamp: Optional[datetime] = None
    ) -> ConfidenceBreakdown:
        """
        Calculate TCS for a collection of events (typically within a window).

        Args:
            events: List of RiskEvent objects to aggregate
            timestamp: Reference timestamp for staleness calculation (default: now)

        Returns:
            ConfidenceBreakdown with all TCS components
        """
        if not events:
            return ConfidenceBreakdown(
                finality_weight=0.0,
                chain_confidence=0.0,
                completeness=0.0,
                staleness_penalty=1.0,
                temporal_confidence=0.0
            )

        timestamp = timestamp or datetime.utcnow()

        # Component 1: Finality Weight
        finality_weight = self._calculate_finality_weight(events)

        # Component 2: Chain Confidence
        chain_confidence = self._calculate_chain_confidence(events)

        # Component 3: Completeness
        completeness = self._calculate_completeness(events)

        # Component 4: Staleness Penalty
        staleness_penalty = self._calculate_staleness_penalty(events, timestamp)

        # Final TCS calculation
        temporal_confidence = (
            (finality_weight * chain_confidence * completeness) / staleness_penalty
        )

        # Clamp to [0, 1]
        temporal_confidence = max(0.0, min(1.0, temporal_confidence))

        return ConfidenceBreakdown(
            finality_weight=finality_weight,
            chain_confidence=chain_confidence,
            completeness=completeness,
            staleness_penalty=staleness_penalty,
            temporal_confidence=temporal_confidence
        )

    def _calculate_finality_weight(self, events: List[RiskEvent]) -> float:
        """
        Component 1: Finality Weight

        Weighted average of finality confidences across all events,
        weighted by source importance.

        Formula: sum(event.finality_conf * event.importance) / total_importance
        """
        if not events:
            return 0.0

        weighted_sum = 0.0
        total_importance = 0.0

        for event in events:
            # Get finality confidence for this event
            finality_conf = event.get_confidence_tier_value()

            # Get importance weight for this source
            source_type = self._infer_source_type(event)
            importance = self.source_importance.get(source_type, 1.0)

            weighted_sum += finality_conf * importance
            total_importance += importance

        if total_importance == 0:
            return 0.0

        return weighted_sum / total_importance

    def _calculate_chain_confidence(self, events: List[RiskEvent]) -> float:
        """
        Component 2: Chain Confidence

        Minimum finality confidence across all contributing chains.
        The chain with the weakest finality becomes the bottleneck.

        Formula: min(finality_per_chain.values())
        """
        if not events:
            return 0.0

        # Group events by chain and find min finality per chain
        chain_finalities: Dict[str, float] = {}

        for event in events:
            finality_conf = event.get_confidence_tier_value()

            if event.chain not in chain_finalities:
                chain_finalities[event.chain] = finality_conf
            else:
                # Take minimum finality for this chain
                chain_finalities[event.chain] = min(
                    chain_finalities[event.chain],
                    finality_conf
                )

        if not chain_finalities:
            return 0.0

        # Overall chain confidence is minimum across all chains
        return min(chain_finalities.values())

    def _calculate_completeness(self, events: List[RiskEvent]) -> float:
        """
        Component 3: Completeness

        Fraction of expected data sources that are actually present.

        Formula: len(present_sources) / len(expected_sources)
        """
        if not events:
            return 0.0

        # Identify which source types are present
        present_sources = set()
        for event in events:
            source_type = self._infer_source_type(event)
            if source_type:
                present_sources.add(source_type)

        # Calculate completeness
        completeness = len(present_sources) / len(self.expected_sources)

        return completeness

    def _calculate_staleness_penalty(
        self,
        events: List[RiskEvent],
        reference_time: datetime
    ) -> float:
        """
        Component 4: Staleness Penalty

        Penalty factor based on the age of the oldest event.
        Stale data reduces confidence even if finality is high.

        Thresholds (from config):
        - < 5 min: penalty = 1.0 (no penalty)
        - < 10 min: penalty = 0.9 (slight penalty)
        - >= 10 min: penalty = 0.7 (significant penalty)
        """
        if not events:
            return 1.0

        # Find oldest event
        oldest_event = min(events, key=lambda e: e.timestamp)
        age_sec = (reference_time - oldest_event.timestamp).total_seconds()

        # Apply tiered penalties
        thresholds = self.staleness_thresholds
        if age_sec < thresholds["fresh"]:
            return 1.0
        elif age_sec < thresholds["acceptable"]:
            return 0.9
        else:
            return 0.7

    def _infer_source_type(self, event: RiskEvent) -> Optional[str]:
        """
        Infer the source type (price, liquidity, supply, etc.) from event data.

        This is a heuristic based on which fields are populated.
        """
        if event.price is not None:
            return "price"
        elif event.liquidity_depth is not None:
            return "liquidity"
        elif event.net_supply_change is not None:
            return "supply"
        elif event.market_volatility is not None:
            return "volatility"
        elif event.sentiment_score is not None:
            return "sentiment"
        else:
            # Fallback to source field if available
            return event.source or None

    def update_event_tcs(self, event: RiskEvent) -> RiskEvent:
        """
        Calculate and update TCS for a single event.

        For single events, TCS simplifies to:
        - finality_weight = event's own finality
        - chain_confidence = event's own finality
        - completeness = 1/5 (only 1 source present)
        - staleness_penalty = based on event age
        """
        breakdown = self.calculate_tcs([event])

        event.temporal_confidence = breakdown.temporal_confidence
        event.confidence_breakdown = {
            "finality_weight": breakdown.finality_weight,
            "chain_confidence": breakdown.chain_confidence,
            "completeness": breakdown.completeness,
            "staleness_penalty": breakdown.staleness_penalty
        }

        return event

    def should_attest(self, tcs: float) -> bool:
        """
        Determine if an event with given TCS should be attested to blockchain.

        Only high-confidence (tier2+) events are attested to save gas.
        """
        return tcs >= self.tcs_config["attestation_threshold"]

    def get_tcs_status(self, tcs: float) -> str:
        """Get human-readable status for TCS value."""
        if tcs >= 0.9:
            return "EXCELLENT"
        elif tcs >= 0.8:
            return "GOOD"
        elif tcs >= 0.6:
            return "MODERATE"
        elif tcs >= 0.4:
            return "LOW"
        else:
            return "POOR"


# Singleton calculator
tcs_calculator = TCSCalculator()
