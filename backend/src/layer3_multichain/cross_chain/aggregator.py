"""
Cross-chain event aggregator.

Handles temporal synchronization across chains with heterogeneous finality:
- Ethereum: ~12.8 min finality
- Arbitrum: ~15 min total (L2 + L1 finality)
- Solana: ~2 min finality

Key challenge: Cross-chain temporal ordering with different finality times.
Solution: Use TCS to quantify confidence in cross-chain aggregations.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from src.common.schema import RiskEvent, AggregatedRiskSnapshot, WindowState
from src.common.config import config
from src.layer1_core.tcs.calculator import tcs_calculator

logger = logging.getLogger(__name__)


@dataclass
class ChainEventBatch:
    """Batch of events from a single chain."""
    chain: str
    events: List[RiskEvent]
    min_finality_tier: str  # Minimum finality tier across all events
    chain_confidence: float  # Min confidence for this chain
    latest_timestamp: datetime


class CrossChainAggregator:
    """
    Aggregates events across multiple chains.

    Handles:
    - Temporal alignment (events from different chains at similar times)
    - Heterogeneous finality (different finality times per chain)
    - Cross-chain TCS calculation (min confidence across chains)
    - Grace periods for slow chains
    """

    def __init__(self):
        self.grace_period_sec = config.TCS_CONFIG["cross_chain_grace_period"]

        # Chain-specific finality times (for grace period calculation)
        self.chain_finality_times = {
            "ethereum": config.CHAINS["ethereum"].tier3_time_sec,
            "arbitrum": config.CHAINS["arbitrum"].tier3_time_sec,
            "solana": config.CHAINS["solana"].tier3_time_sec
        }

    def aggregate_cross_chain(
        self,
        events_by_chain: Dict[str, List[RiskEvent]],
        window_id: str,
        coin: str
    ) -> Optional[AggregatedRiskSnapshot]:
        """
        Aggregate events across multiple chains for a coin.

        Args:
            events_by_chain: Dict mapping chain -> list of events
            window_id: Time window identifier
            coin: Stablecoin symbol

        Returns:
            Cross-chain aggregated snapshot with multi-chain TCS
        """
        if not events_by_chain:
            logger.warning("No events to aggregate across chains")
            return None

        # Flatten all events
        all_events = []
        for chain_events in events_by_chain.values():
            all_events.extend(chain_events)

        if not all_events:
            return None

        # Calculate cross-chain TCS
        tcs_breakdown = tcs_calculator.calculate_tcs(all_events)

        # Additionally calculate chain-specific confidence
        chain_confidence = self._calculate_chain_confidence(events_by_chain)

        # Adjust TCS with chain confidence (weakest link)
        adjusted_tcs = tcs_breakdown.temporal_confidence * chain_confidence

        # Aggregate metrics across chains
        prices = [e.price for e in all_events if e.price is not None]
        liquidities = [e.liquidity_depth for e in all_events if e.liquidity_depth is not None]
        volumes = [e.volume for e in all_events if e.volume is not None]
        supply_changes = [e.net_supply_change for e in all_events if e.net_supply_change is not None]
        volatilities = [e.market_volatility for e in all_events if e.market_volatility is not None]
        sentiments = [e.sentiment_score for e in all_events if e.sentiment_score is not None]

        # Create cross-chain snapshot
        snapshot = AggregatedRiskSnapshot(
            timestamp=datetime.utcnow(),
            coin=coin,
            chains=list(events_by_chain.keys()),
            window_id=window_id,
            window_state=WindowState.PROVISIONAL.value,  # Wait for all chains to finalize
            avg_price=sum(prices) / len(prices) if prices else None,
            min_price=min(prices) if prices else None,
            max_price=max(prices) if prices else None,
            total_liquidity=sum(liquidities) if liquidities else None,
            total_volume=sum(volumes) if volumes else None,
            net_supply_change=sum(supply_changes) if supply_changes else None,
            market_volatility=max(volatilities) if volatilities else None,
            sentiment_score=sum(sentiments) / len(sentiments) if sentiments else None,
            temporal_confidence=adjusted_tcs,
            confidence_breakdown={
                "finality_weight": tcs_breakdown.finality_weight,
                "chain_confidence": chain_confidence,  # Cross-chain bottleneck
                "completeness": tcs_breakdown.completeness,
                "staleness_penalty": tcs_breakdown.staleness_penalty,
                "adjusted_tcs": adjusted_tcs
            },
            num_events_aggregated=len(all_events),
            sources_included=list(set(e.source for e in all_events)),
            event_ids=[e.event_id for e in all_events]
        )

        # Check depeg (price should be same across chains)
        if snapshot.avg_price:
            depeg_distance = abs(snapshot.avg_price - 1.0)
            coin_config = config.COINS.get(coin)
            if coin_config:
                snapshot.is_depegged = depeg_distance >= coin_config.depeg_threshold
                snapshot.depeg_severity = depeg_distance

        logger.info(
            f"Cross-chain aggregation: {coin} across {len(events_by_chain)} chains, "
            f"TCS={adjusted_tcs:.3f} (chain_conf={chain_confidence:.3f}), "
            f"events={len(all_events)}"
        )

        return snapshot

    def _calculate_chain_confidence(
        self,
        events_by_chain: Dict[str, List[RiskEvent]]
    ) -> float:
        """
        Calculate cross-chain confidence as minimum finality across chains.

        This is the "weakest link" principle: the overall confidence
        is limited by the chain with the lowest finality.
        """
        chain_confidences = []

        for chain, events in events_by_chain.items():
            if not events:
                continue

            # Get minimum finality confidence for this chain
            min_confidence = min(
                e.get_confidence_tier_value() for e in events
            )
            chain_confidences.append(min_confidence)

            logger.debug(
                f"Chain {chain}: min_confidence={min_confidence:.3f} "
                f"from {len(events)} events"
            )

        # Cross-chain confidence = minimum across all chains
        if not chain_confidences:
            return 0.0

        overall_confidence = min(chain_confidences)

        logger.info(
            f"Cross-chain confidence: {overall_confidence:.3f} "
            f"(weakest of {len(chain_confidences)} chains)"
        )

        return overall_confidence

    def check_cross_chain_readiness(
        self,
        events_by_chain: Dict[str, List[RiskEvent]],
        window_end: datetime
    ) -> bool:
        """
        Check if cross-chain aggregation is ready.

        Returns True if:
        1. Grace period has passed for all chains
        2. All chains have reached minimum finality threshold
        """
        current_time = datetime.utcnow()

        # Check if grace period has passed
        grace_period_elapsed = current_time >= window_end + timedelta(
            seconds=self.grace_period_sec
        )

        if not grace_period_elapsed:
            logger.debug("Grace period not yet elapsed for cross-chain aggregation")
            return False

        # Check minimum finality per chain
        for chain, events in events_by_chain.items():
            if not events:
                continue

            # Get minimum finality tier for this chain
            min_tier = min(e.finality_tier for e in events)

            # Require at least tier2 (0.8 confidence) for cross-chain aggregation
            if min_tier == "tier1":
                logger.debug(
                    f"Chain {chain} not ready: still has tier1 events"
                )
                return False

        logger.info("Cross-chain aggregation ready: all chains ≥tier2")
        return True

    def detect_cross_chain_divergence(
        self,
        events_by_chain: Dict[str, List[RiskEvent]],
        threshold: float = 0.01
    ) -> Dict:
        """
        Detect price divergence across chains.

        If the same coin has different prices on different chains,
        this could indicate:
        - Arbitrage opportunities
        - Liquidity issues on one chain
        - Oracle failures
        - Chain-specific risk

        Args:
            events_by_chain: Events grouped by chain
            threshold: Max acceptable price difference (default 1%)

        Returns:
            Divergence report with details
        """
        # Get average price per chain
        chain_prices = {}
        for chain, events in events_by_chain.items():
            prices = [e.price for e in events if e.price is not None]
            if prices:
                chain_prices[chain] = sum(prices) / len(prices)

        if len(chain_prices) < 2:
            return {"divergence_detected": False}

        # Check all pairs for divergence
        chains = list(chain_prices.keys())
        divergences = []

        for i, chain1 in enumerate(chains):
            for chain2 in chains[i+1:]:
                price1 = chain_prices[chain1]
                price2 = chain_prices[chain2]
                diff = abs(price1 - price2)

                if diff > threshold:
                    divergences.append({
                        "chain1": chain1,
                        "chain2": chain2,
                        "price1": price1,
                        "price2": price2,
                        "difference": diff,
                        "percentage": (diff / ((price1 + price2) / 2)) * 100
                    })

                    logger.warning(
                        f"Cross-chain divergence detected: "
                        f"{chain1} ${price1:.6f} vs {chain2} ${price2:.6f} "
                        f"(Δ=${diff:.6f}, {(diff/price1)*100:.2f}%)"
                    )

        return {
            "divergence_detected": len(divergences) > 0,
            "divergence_count": len(divergences),
            "divergences": divergences,
            "chain_prices": chain_prices
        }

    def get_slowest_chain(
        self,
        chains: List[str]
    ) -> str:
        """Get the chain with the slowest finality time."""
        slowest_chain = max(
            chains,
            key=lambda c: self.chain_finality_times.get(c, 0)
        )
        return slowest_chain

    def calculate_cross_chain_grace_period(
        self,
        chains: List[str]
    ) -> int:
        """
        Calculate grace period based on slowest chain.

        Grace period = finality time of slowest chain
        """
        max_finality = max(
            self.chain_finality_times.get(c, 0) for c in chains
        )
        return max_finality


# Singleton aggregator
cross_chain_aggregator = CrossChainAggregator()
