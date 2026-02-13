"""
Web3 Supply Event Listener

Monitors on-chain mint/burn events for stablecoins across multiple chains:
- Ethereum: USDC, USDT, DAI mint/burn events
- Arbitrum: Bridged USDC, USDT events
- Solana: SPL token mint/burn

Uses Web3.py for EVM chains and Solana.py for Solana.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, AsyncIterator
from web3 import Web3
from web3.contract import Contract
from eth_typing import HexStr
import json

from src.common.config import Config
from src.common.schema import RiskEvent

logger = logging.getLogger(__name__)


# ERC20 Transfer event signature (for detecting mints/burns)
TRANSFER_EVENT_SIGNATURE = Web3.keccak(text="Transfer(address,address,uint256)").hex()

# Zero address (used for mints and burns)
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class Web3SupplyMonitor:
    """
    Monitors on-chain supply changes (mints/burns) for stablecoins.

    Detects:
    - Mint events: Transfer from 0x0 address
    - Burn events: Transfer to 0x0 address
    """

    def __init__(self, chain: str = "ethereum", coin: str = "USDC", mode: str = "mock"):
        """
        Initialize supply monitor.

        Args:
            chain: Chain to monitor (ethereum, arbitrum, solana)
            coin: Coin to monitor (USDC, USDT, DAI)
            mode: "mock" or "live"
        """
        self.chain = chain
        self.coin = coin
        self.mode = mode

        # Get chain config
        self.chain_config = Config.CHAINS.get(chain)
        self.rpc_url = self.chain_config.rpc_url if self.chain_config else ""

        # Get coin config
        self.coin_config = Config.COINS.get(coin)
        self.contract_address = self.coin_config.contract_addresses.get(chain) if self.coin_config else None
        self.decimals = self.coin_config.decimals if self.coin_config else 6

        # Web3 connection
        if mode == "live" and self.rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            logger.info(f"Connected to {chain} RPC: {self.w3.is_connected()}")
        else:
            self.w3 = None
            logger.info(f"Running in mock mode for {coin} on {chain}")

    def decode_transfer_event(self, log: Dict) -> Optional[Dict]:
        """
        Decode Transfer event from log.

        Args:
            log: Raw event log from blockchain

        Returns:
            Dict with from, to, amount or None if not a Transfer event
        """
        # Check if this is a Transfer event
        if len(log.get('topics', [])) < 3:
            return None

        if log['topics'][0].hex() != TRANSFER_EVENT_SIGNATURE:
            return None

        # Decode topics
        from_address = "0x" + log['topics'][1].hex()[-40:]
        to_address = "0x" + log['topics'][2].hex()[-40:]

        # Decode data (amount)
        amount_hex = log['data'].hex() if hasattr(log['data'], 'hex') else log['data']
        amount = int(amount_hex, 16)

        return {
            "from": from_address.lower(),
            "to": to_address.lower(),
            "amount": amount,
            "amount_decimal": amount / (10 ** self.decimals)
        }

    def is_mint_event(self, from_address: str) -> bool:
        """Check if event is a mint (from zero address)."""
        return from_address.lower() == ZERO_ADDRESS.lower()

    def is_burn_event(self, to_address: str) -> bool:
        """Check if event is a burn (to zero address)."""
        return to_address.lower() == ZERO_ADDRESS.lower()

    async def fetch_recent_supply_events(
        self,
        from_block: int,
        to_block: int = None
    ) -> List[RiskEvent]:
        """
        Fetch supply events (mints/burns) for a block range.

        Args:
            from_block: Start block number
            to_block: End block number (latest if None)

        Returns:
            List of RiskEvent objects for mint/burn events
        """
        if self.mode == "mock":
            return await self._fetch_mock_supply_events()

        if not self.w3 or not self.w3.is_connected():
            logger.error(f"Web3 not connected for {self.chain}")
            return []

        if not self.contract_address:
            logger.error(f"No contract address for {self.coin} on {self.chain}")
            return []

        try:
            # Get current block if to_block not specified
            if to_block is None:
                to_block = self.w3.eth.block_number

            logger.info(
                f"Fetching {self.coin} supply events on {self.chain} "
                f"from block {from_block} to {to_block}"
            )

            # Fetch Transfer events for this contract
            filter_params = {
                "fromBlock": from_block,
                "toBlock": to_block,
                "address": self.contract_address,
                "topics": [TRANSFER_EVENT_SIGNATURE]
            }

            logs = self.w3.eth.get_logs(filter_params)

            # Process logs into RiskEvents
            events = []
            for log in logs:
                transfer = self.decode_transfer_event(log)
                if not transfer:
                    continue

                # Determine if mint or burn
                is_mint = self.is_mint_event(transfer['from'])
                is_burn = self.is_burn_event(transfer['to'])

                if not (is_mint or is_burn):
                    # Regular transfer, not mint/burn
                    continue

                # Get block timestamp
                block = self.w3.eth.get_block(log['blockNumber'])
                timestamp = datetime.fromtimestamp(block['timestamp'], tz=timezone.utc)

                # Calculate net supply change (positive for mint, negative for burn)
                net_change = transfer['amount_decimal'] if is_mint else -transfer['amount_decimal']

                event = RiskEvent(
                    timestamp=timestamp,
                    coin=self.coin,
                    chain=self.chain,
                    source="web3_events",
                    net_supply_change=net_change,
                    block_number=log['blockNumber'],
                    tx_hash=log['transactionHash'].hex(),
                    confirmation_count=to_block - log['blockNumber'],
                    finality_tier="tier1",  # Will upgrade as confirmations increase
                    event_version=1,
                    invalidated=False,
                    metadata={
                        "event_type": "mint" if is_mint else "burn",
                        "from": transfer['from'],
                        "to": transfer['to'],
                        "amount": transfer['amount_decimal'],
                        "contract_address": self.contract_address
                    }
                )

                events.append(event)

            logger.info(
                f"✓ Found {len(events)} supply events "
                f"({sum(1 for e in events if e.metadata['event_type'] == 'mint')} mints, "
                f"{sum(1 for e in events if e.metadata['event_type'] == 'burn')} burns)"
            )

            return events

        except Exception as e:
            logger.error(f"Error fetching supply events: {e}")
            return []

    async def _fetch_mock_supply_events(self) -> List[RiskEvent]:
        """Generate mock supply events for testing."""
        now = datetime.now(timezone.utc)

        # Generate a few mock mint/burn events
        events = [
            RiskEvent(
                timestamp=now,
                coin=self.coin,
                chain=self.chain,
                source="web3_events_mock",
                net_supply_change=1_000_000.0,  # 1M mint
                block_number=20_000_000,
                tx_hash="0xmock_mint_1",
                confirmation_count=10,
                finality_tier="tier2",
                event_version=1,
                invalidated=False,
                metadata={
                    "event_type": "mint",
                    "from": ZERO_ADDRESS,
                    "to": "0xmock_treasury",
                    "amount": 1_000_000.0
                }
            ),
            RiskEvent(
                timestamp=now,
                coin=self.coin,
                chain=self.chain,
                source="web3_events_mock",
                net_supply_change=-500_000.0,  # 500K burn
                block_number=20_000_010,
                tx_hash="0xmock_burn_1",
                confirmation_count=5,
                finality_tier="tier1",
                event_version=1,
                invalidated=False,
                metadata={
                    "event_type": "burn",
                    "from": "0xmock_burner",
                    "to": ZERO_ADDRESS,
                    "amount": 500_000.0
                }
            )
        ]

        logger.info(f"✓ Generated {len(events)} mock supply events for {self.coin} on {self.chain}")
        return events

    async def stream_supply_events(
        self,
        poll_interval: int = 60
    ) -> AsyncIterator[RiskEvent]:
        """
        Stream supply events continuously.

        Args:
            poll_interval: Seconds between polls

        Yields:
            RiskEvent objects as they occur
        """
        last_block = None

        if self.mode == "live" and self.w3:
            last_block = self.w3.eth.block_number - 100  # Start from 100 blocks ago

        while True:
            try:
                if self.mode == "mock":
                    # In mock mode, yield events periodically
                    events = await self._fetch_mock_supply_events()
                    for event in events:
                        yield event
                    await asyncio.sleep(poll_interval)
                    continue

                # Live mode
                if not self.w3 or not self.w3.is_connected():
                    logger.warning(f"Web3 not connected, sleeping...")
                    await asyncio.sleep(poll_interval)
                    continue

                current_block = self.w3.eth.block_number

                if last_block is None:
                    last_block = current_block - 10  # Start from 10 blocks ago

                # Fetch events from last_block to current
                if current_block > last_block:
                    events = await self.fetch_recent_supply_events(
                        from_block=last_block + 1,
                        to_block=current_block
                    )

                    for event in events:
                        yield event

                    last_block = current_block

                # Wait before next poll
                await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(f"Error in supply event stream: {e}")
                await asyncio.sleep(poll_interval)


class MultiChainSupplyMonitor:
    """Monitors supply events across multiple chains and coins."""

    def __init__(self, coins: List[str] = None, chains: List[str] = None, mode: str = "mock"):
        """
        Initialize multi-chain supply monitor.

        Args:
            coins: List of coins to monitor (defaults to all)
            chains: List of chains to monitor (defaults to all)
            mode: "mock" or "live"
        """
        self.coins = coins or list(Config.COINS.keys())
        self.chains = chains or ["ethereum", "arbitrum"]  # Exclude Solana for now
        self.mode = mode

        # Create monitors for each coin/chain pair
        self.monitors: List[Web3SupplyMonitor] = []
        for coin in self.coins:
            for chain in self.chains:
                monitor = Web3SupplyMonitor(chain=chain, coin=coin, mode=mode)
                self.monitors.append(monitor)

        logger.info(f"Initialized {len(self.monitors)} supply monitors")

    async def fetch_all_supply_events(
        self,
        from_block: int,
        to_block: int = None
    ) -> List[RiskEvent]:
        """
        Fetch supply events from all monitors.

        Args:
            from_block: Start block number (per chain)
            to_block: End block number (per chain)

        Returns:
            Combined list of RiskEvents from all chains
        """
        tasks = [
            monitor.fetch_recent_supply_events(from_block, to_block)
            for monitor in self.monitors
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results
        all_events = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Monitor failed: {result}")
                continue
            all_events.extend(result)

        return all_events

    async def stream_all_supply_events(
        self,
        poll_interval: int = 60
    ) -> AsyncIterator[RiskEvent]:
        """
        Stream supply events from all chains simultaneously.

        Args:
            poll_interval: Seconds between polls per monitor

        Yields:
            RiskEvent objects as they occur on any chain
        """
        # Create async generators for each monitor
        streams = [
            monitor.stream_supply_events(poll_interval)
            for monitor in self.monitors
        ]

        # Merge streams
        while True:
            for stream in streams:
                try:
                    event = await asyncio.wait_for(
                        stream.__anext__(),
                        timeout=poll_interval
                    )
                    yield event
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    break
                except Exception as e:
                    logger.error(f"Stream error: {e}")


async def demo_supply_monitoring():
    """Demo: Monitor supply events."""
    logger.info("=" * 70)
    logger.info("SUPPLY EVENT MONITORING DEMO")
    logger.info("=" * 70)

    # Create multi-chain monitor in mock mode
    monitor = MultiChainSupplyMonitor(
        coins=["USDC", "USDT"],
        chains=["ethereum", "arbitrum"],
        mode="mock"
    )

    # Fetch recent events
    logger.info("\n📊 Fetching recent supply events...")
    events = await monitor.fetch_all_supply_events(from_block=20_000_000)

    logger.info(f"\n✓ Found {len(events)} total supply events:")
    for event in events:
        logger.info(
            f"  {event.coin} on {event.chain}: "
            f"{event.metadata['event_type'].upper()} "
            f"{event.net_supply_change:+,.0f} "
            f"(block {event.block_number})"
        )

    # Demo streaming (just a few iterations)
    logger.info("\n📡 Starting supply event stream (3 iterations)...")
    iteration = 0
    async for event in monitor.stream_all_supply_events(poll_interval=2):
        logger.info(
            f"  [{iteration}] {event.coin} on {event.chain}: "
            f"{event.metadata['event_type'].upper()} "
            f"{event.net_supply_change:+,.0f}"
        )
        iteration += 1
        if iteration >= 6:  # 3 iterations * 2 monitors = 6 events
            break

    logger.info("\n" + "=" * 70)
    logger.info("✅ DEMO COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(demo_supply_monitoring())
