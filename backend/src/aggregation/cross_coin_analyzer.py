"""
Cross-coin analysis and comparison.

Analyzes relationships between multiple stablecoins to detect:
- Correlated depeg events (contagion risk)
- Divergence patterns
- Market-wide stress signals
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import statistics
import logging

from src.common.schema import AggregatedRiskSnapshot
from src.registry.coin_registry import coin_registry, CoinStatus

logger = logging.getLogger(__name__)


@dataclass
class CoinComparison:
    """Comparison between two stablecoins."""
    coin1: str
    coin2: str
    timestamp: datetime

    # Price comparison
    price_diff: float  # Absolute difference
    price_correlation: Optional[float] = None  # Historical correlation

    # Risk comparison
    health_score_diff: float = 0.0
    tcs_diff: float = 0.0

    # Divergence flags
    is_diverging: bool = False  # Prices moving apart
    divergence_severity: float = 0.0


@dataclass
class MarketStressSignal:
    """Market-wide stress signal across all stablecoins."""
    timestamp: datetime
    severity: str  # "low", "moderate", "high", "critical"
    severity_score: float  # 0.0 to 1.0

    # Contributing factors
    depegged_count: int
    avg_depeg_severity: float
    avg_health_score: float
    avg_tcs: float

    # Sentiment
    avg_sentiment: Optional[float] = None

    # Liquidity
    total_liquidity: Optional[float] = None
    liquidity_crisis: bool = False

    # Affected coins
    affected_coins: List[str] = None


class CrossCoinAnalyzer:
    """
    Analyzes relationships and patterns across multiple stablecoins.

    Detects:
    - Contagion risk (correlated depegs)
    - Market stress signals
    - Divergence anomalies
    """

    def __init__(self):
        self.registry = coin_registry

        # Thresholds
        self.divergence_threshold = 0.01  # 1% price difference triggers flag
        self.contagion_threshold = 2  # ≥2 depegged coins = contagion risk

    def compare_coins(
        self,
        coin1: str,
        coin2: str
    ) -> Optional[CoinComparison]:
        """
        Compare two stablecoins.

        Returns:
            CoinComparison with metrics, or None if data unavailable
        """
        status1 = self.registry.get_coin_status(coin1)
        status2 = self.registry.get_coin_status(coin2)

        if not status1 or not status2:
            logger.warning(f"Cannot compare {coin1} and {coin2} - missing status")
            return None

        if status1.current_price is None or status2.current_price is None:
            logger.warning(f"Cannot compare {coin1} and {coin2} - missing prices")
            return None

        # Calculate price difference
        price_diff = abs(status1.current_price - status2.current_price)

        # Check for divergence
        is_diverging = price_diff > self.divergence_threshold
        divergence_severity = price_diff if is_diverging else 0.0

        # Health score difference
        health_diff = abs(status1.health_score - status2.health_score)

        # TCS difference
        tcs_diff = abs(status1.temporal_confidence - status2.temporal_confidence)

        comparison = CoinComparison(
            coin1=coin1,
            coin2=coin2,
            timestamp=datetime.utcnow(),
            price_diff=price_diff,
            health_score_diff=health_diff,
            tcs_diff=tcs_diff,
            is_diverging=is_diverging,
            divergence_severity=divergence_severity
        )

        if is_diverging:
            logger.warning(
                f"Price divergence detected: {coin1} vs {coin2} "
                f"(Δ=${price_diff:.4f}, {divergence_severity*100:.2f}%)"
            )

        return comparison

    def compare_all_pairs(self) -> List[CoinComparison]:
        """Compare all pairs of active coins."""
        active_coins = self.registry.get_active_coins()
        comparisons = []

        for i, coin1 in enumerate(active_coins):
            for coin2 in active_coins[i+1:]:
                comparison = self.compare_coins(coin1, coin2)
                if comparison:
                    comparisons.append(comparison)

        return comparisons

    def detect_contagion_risk(self) -> Tuple[bool, List[str]]:
        """
        Detect contagion risk from correlated depeg events.

        Returns:
            (is_contagion, affected_coins)
        """
        depegged_coins = self.registry.get_depegged_coins()

        is_contagion = len(depegged_coins) >= self.contagion_threshold

        if is_contagion:
            logger.error(
                f"🚨 CONTAGION RISK DETECTED: {len(depegged_coins)} coins depegged: "
                f"{', '.join(depegged_coins)}"
            )

        return is_contagion, depegged_coins

    def assess_market_stress(self) -> MarketStressSignal:
        """
        Assess overall market stress across all stablecoins.

        Returns:
            MarketStressSignal with severity and metrics
        """
        active_coins = self.registry.get_active_coins()

        if not active_coins:
            logger.warning("No active coins to assess market stress")
            return MarketStressSignal(
                timestamp=datetime.utcnow(),
                severity="unknown",
                severity_score=0.0,
                depegged_count=0,
                avg_depeg_severity=0.0,
                avg_health_score=0.0,
                avg_tcs=0.0,
                affected_coins=[]
            )

        # Collect metrics
        depegged_coins = []
        depeg_severities = []
        health_scores = []
        tcs_scores = []
        sentiments = []
        liquidities = []

        for coin in active_coins:
            status = self.registry.get_coin_status(coin)
            if not status:
                continue

            health_scores.append(status.health_score)
            tcs_scores.append(status.temporal_confidence)

            if status.is_depegged:
                depegged_coins.append(coin)
                depeg_severities.append(status.depeg_severity)

            if status.sentiment_score is not None:
                sentiments.append(status.sentiment_score)

            if status.total_liquidity is not None:
                liquidities.append(status.total_liquidity)

        # Calculate averages
        avg_health = statistics.mean(health_scores) if health_scores else 0.0
        avg_tcs = statistics.mean(tcs_scores) if tcs_scores else 0.0
        avg_sentiment = statistics.mean(sentiments) if sentiments else None
        total_liquidity = sum(liquidities) if liquidities else None

        # Calculate depeg metrics
        depegged_count = len(depegged_coins)
        avg_depeg_severity = (
            statistics.mean(depeg_severities) if depeg_severities else 0.0
        )

        # Liquidity crisis detection
        # (if any coin has liquidity below min threshold)
        liquidity_crisis = any(
            status.has_liquidity_crisis
            for status in self.registry.coin_status.values()
        )

        # Calculate severity score (0.0 to 1.0)
        severity_score = self._calculate_stress_severity(
            depegged_count=depegged_count,
            avg_depeg_severity=avg_depeg_severity,
            avg_health=avg_health,
            avg_sentiment=avg_sentiment,
            liquidity_crisis=liquidity_crisis
        )

        # Classify severity
        if severity_score >= 0.8:
            severity = "critical"
        elif severity_score >= 0.6:
            severity = "high"
        elif severity_score >= 0.3:
            severity = "moderate"
        else:
            severity = "low"

        signal = MarketStressSignal(
            timestamp=datetime.utcnow(),
            severity=severity,
            severity_score=severity_score,
            depegged_count=depegged_count,
            avg_depeg_severity=avg_depeg_severity,
            avg_health_score=avg_health,
            avg_tcs=avg_tcs,
            avg_sentiment=avg_sentiment,
            total_liquidity=total_liquidity,
            liquidity_crisis=liquidity_crisis,
            affected_coins=depegged_coins
        )

        if severity in ["high", "critical"]:
            logger.error(
                f"🚨 {severity.upper()} MARKET STRESS DETECTED: "
                f"score={severity_score:.2f}, depegged={depegged_count}"
            )
        elif severity == "moderate":
            logger.warning(
                f"⚠️ MODERATE MARKET STRESS: "
                f"score={severity_score:.2f}"
            )

        return signal

    def _calculate_stress_severity(
        self,
        depegged_count: int,
        avg_depeg_severity: float,
        avg_health: float,
        avg_sentiment: Optional[float],
        liquidity_crisis: bool
    ) -> float:
        """Calculate market stress severity score (0.0 to 1.0)."""
        score = 0.0

        # Factor 1: Depeg events (most critical)
        if depegged_count >= 3:  # All major stablecoins depegged
            score += 0.6
        elif depegged_count >= 2:  # Contagion
            score += 0.4
        elif depegged_count >= 1:
            score += 0.2

        # Factor 2: Depeg severity
        score += min(0.3, avg_depeg_severity * 3)  # Max 0.3 contribution

        # Factor 3: Average health
        score += (1.0 - avg_health) * 0.2  # Max 0.2 contribution

        # Factor 4: Sentiment (if available)
        if avg_sentiment is not None and avg_sentiment < 0:
            score += abs(avg_sentiment) * 0.1  # Max 0.1 contribution

        # Factor 5: Liquidity crisis (binary)
        if liquidity_crisis:
            score += 0.2

        return min(1.0, score)

    def get_market_overview(self) -> Dict:
        """Get comprehensive market overview."""
        summary = self.registry.get_registry_summary()
        stress_signal = self.assess_market_stress()
        is_contagion, contagion_coins = self.detect_contagion_risk()

        # Get comparisons
        comparisons = self.compare_all_pairs()
        diverging = [c for c in comparisons if c.is_diverging]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "registry_summary": summary,
            "market_stress": {
                "severity": stress_signal.severity,
                "score": stress_signal.severity_score,
                "depegged_count": stress_signal.depegged_count,
                "avg_health": stress_signal.avg_health_score,
                "avg_tcs": stress_signal.avg_tcs,
                "liquidity_crisis": stress_signal.liquidity_crisis
            },
            "contagion_risk": {
                "detected": is_contagion,
                "affected_coins": contagion_coins
            },
            "divergences": {
                "count": len(diverging),
                "pairs": [
                    {
                        "coin1": c.coin1,
                        "coin2": c.coin2,
                        "price_diff": c.price_diff,
                        "severity": c.divergence_severity
                    }
                    for c in diverging
                ]
            }
        }


# Singleton analyzer
cross_coin_analyzer = CrossCoinAnalyzer()
