"""
RPC Connection Manager with failover, rate limiting, and error recovery.

Provides robust RPC connectivity for blockchain monitoring with:
- Automatic failover to backup RPC endpoints
- Rate limiting to prevent hitting API limits
- Exponential backoff on failures
- Connection health monitoring
- Circuit breaker pattern
"""

from typing import Callable, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures detected, using fallback
    HALF_OPEN = "half_open"  # Testing if primary recovered


class RPCClient:
    """
    RPC client with automatic failover and error recovery.

    Features:
    - Multiple RPC endpoints with priority ordering
    - Automatic failover when primary fails
    - Circuit breaker to prevent hammering failed endpoints
    - Exponential backoff on retries
    - Rate limiting (simple token bucket)
    """

    def __init__(
        self,
        chain: str,
        primary_rpc: str,
        fallback_rpcs: List[str],
        max_retries: int = 3,
        timeout_sec: int = 30
    ):
        """
        Initialize RPC client.

        Args:
            chain: Chain name
            primary_rpc: Primary RPC URL
            fallback_rpcs: List of fallback RPC URLs
            max_retries: Max retry attempts per request
            timeout_sec: Request timeout in seconds
        """
        self.chain = chain
        self.primary_rpc = primary_rpc
        self.fallback_rpcs = fallback_rpcs
        self.max_retries = max_retries
        self.timeout_sec = timeout_sec

        # Current RPC endpoint
        self.all_rpcs = [primary_rpc] + fallback_rpcs
        self.current_rpc_index = 0

        # Circuit breaker state
        self.circuit_state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = 5  # Open circuit after 5 failures
        self.circuit_open_time: Optional[datetime] = None
        self.circuit_timeout_sec = 60  # Try primary again after 60s

        # Rate limiting (simple token bucket)
        self.rate_limit_tokens = 10
        self.max_tokens = 10
        self.token_refill_rate = 2.0  # tokens per second
        self.last_refill_time = datetime.utcnow()

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.failovers = 0

        logger.info(
            f"Initialized RPC client for {chain} with {len(self.all_rpcs)} endpoints"
        )

    @property
    def current_rpc(self) -> str:
        """Get current RPC URL."""
        return self.all_rpcs[self.current_rpc_index]

    async def call_with_failover(
        self,
        method: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Call RPC method with automatic failover.

        Args:
            method: Async callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from method call

        Raises:
            Exception: If all retries and failovers exhausted
        """
        self.total_requests += 1

        # Check circuit breaker
        if self.circuit_state == CircuitState.OPEN:
            if self._should_try_primary():
                self.circuit_state = CircuitState.HALF_OPEN
                logger.info(f"Circuit half-open for {self.chain}, testing primary")
            else:
                # Circuit still open, use fallback
                if self.current_rpc_index == 0:
                    self._switch_to_fallback()

        # Rate limiting
        await self._wait_for_rate_limit()

        # Try with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                # Execute method with timeout
                result = await asyncio.wait_for(
                    method(*args, **kwargs),
                    timeout=self.timeout_sec
                )

                # Success!
                self.successful_requests += 1
                self._record_success()
                return result

            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(
                    f"RPC timeout on {self.chain} (attempt {attempt + 1}/{self.max_retries})"
                )
                await self._handle_failure(attempt)

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"RPC error on {self.chain}: {str(e)[:100]} "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                await self._handle_failure(attempt)

        # All retries failed
        self.failed_requests += 1
        logger.error(
            f"All retries exhausted for {self.chain} after {self.max_retries} attempts"
        )
        raise last_exception

    async def _handle_failure(self, attempt: int):
        """Handle RPC failure."""
        self.failure_count += 1

        # Open circuit if too many failures
        if self.failure_count >= self.failure_threshold:
            if self.circuit_state == CircuitState.CLOSED:
                logger.error(
                    f"Opening circuit for {self.chain} after {self.failure_count} failures"
                )
                self.circuit_state = CircuitState.OPEN
                self.circuit_open_time = datetime.utcnow()
                self._switch_to_fallback()

        # Exponential backoff
        if attempt < self.max_retries - 1:
            backoff_sec = 2 ** attempt  # 1s, 2s, 4s
            logger.debug(f"Backing off for {backoff_sec}s")
            await asyncio.sleep(backoff_sec)

    def _record_success(self):
        """Record successful request."""
        # Reset failure count on success
        if self.failure_count > 0:
            logger.info(
                f"RPC recovered for {self.chain} after {self.failure_count} failures"
            )
            self.failure_count = 0

        # Close circuit if we're in half-open state
        if self.circuit_state == CircuitState.HALF_OPEN:
            logger.info(f"Closing circuit for {self.chain} - primary recovered")
            self.circuit_state = CircuitState.CLOSED
            self.current_rpc_index = 0  # Back to primary

    def _should_try_primary(self) -> bool:
        """Check if we should try primary RPC again."""
        if self.circuit_open_time is None:
            return False

        elapsed = (datetime.utcnow() - self.circuit_open_time).total_seconds()
        return elapsed >= self.circuit_timeout_sec

    def _switch_to_fallback(self):
        """Switch to next fallback RPC."""
        old_rpc = self.current_rpc
        self.current_rpc_index = (self.current_rpc_index + 1) % len(self.all_rpcs)
        self.failovers += 1

        logger.warning(
            f"Switching {self.chain} RPC: {old_rpc} -> {self.current_rpc}"
        )

    async def _wait_for_rate_limit(self):
        """Wait if rate limit exceeded (token bucket algorithm)."""
        # Refill tokens based on time elapsed
        now = datetime.utcnow()
        elapsed = (now - self.last_refill_time).total_seconds()
        tokens_to_add = elapsed * self.token_refill_rate
        self.rate_limit_tokens = min(self.max_tokens, self.rate_limit_tokens + tokens_to_add)
        self.last_refill_time = now

        # Wait if no tokens available
        if self.rate_limit_tokens < 1:
            wait_time = 1 / self.token_refill_rate
            logger.debug(f"Rate limit reached for {self.chain}, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
            self.rate_limit_tokens = 1

        # Consume token
        self.rate_limit_tokens -= 1

    def get_stats(self) -> dict:
        """Get client statistics."""
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 0
        )

        return {
            "chain": self.chain,
            "current_rpc": self.current_rpc,
            "circuit_state": self.circuit_state.value,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{success_rate:.1%}",
            "failovers": self.failovers,
            "failure_count": self.failure_count
        }


class RPCClientRegistry:
    """Registry for managing RPC clients across multiple chains."""

    def __init__(self):
        self.clients: dict[str, RPCClient] = {}

    def get_or_create(
        self,
        chain: str,
        primary_rpc: str,
        fallback_rpcs: List[str]
    ) -> RPCClient:
        """Get existing client or create new one."""
        if chain not in self.clients:
            self.clients[chain] = RPCClient(
                chain=chain,
                primary_rpc=primary_rpc,
                fallback_rpcs=fallback_rpcs
            )
        return self.clients[chain]

    def get_all_stats(self) -> dict:
        """Get stats for all clients."""
        return {
            chain: client.get_stats()
            for chain, client in self.clients.items()
        }


# Singleton registry
rpc_registry = RPCClientRegistry()
