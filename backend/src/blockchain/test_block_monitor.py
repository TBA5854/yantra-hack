"""
Test script for block monitoring service.

Tests that block monitors can:
1. Start monitoring loops
2. Cache block headers
3. Poll continuously
4. Track statistics
"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ethereum_monitor():
    """Test Ethereum block monitoring for 30 seconds."""
    from src.confidence.finality_tracker import EthereumFinalityTracker
    from src.blockchain.block_monitor import EthereumBlockMonitor

    logger.info("=" * 70)
    logger.info("Testing Ethereum Block Monitor")
    logger.info("=" * 70)

    tracker = EthereumFinalityTracker()
    monitor = EthereumBlockMonitor("ethereum", tracker)

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor.start_monitoring())

    # Let it run for 30 seconds
    await asyncio.sleep(30)

    # Stop monitoring
    await monitor.stop_monitoring()

    # Wait for task to complete
    try:
        await asyncio.wait_for(monitor_task, timeout=5)
    except asyncio.TimeoutError:
        monitor_task.cancel()

    # Get stats
    stats = monitor.get_stats()
    logger.info("\n📊 Ethereum Monitor Stats:")
    logger.info(f"  Polls completed:     {stats['poll_count']}")
    logger.info(f"  Cache size:          {stats['cache_size']}/{stats['max_cache_size']}")
    logger.info(f"  Reorgs detected:     {stats['reorgs_detected']}")
    logger.info(f"  Last poll:           {stats['last_poll_time']}")

    return stats['poll_count'] > 0  # Success if at least 1 poll completed


async def test_arbitrum_monitor():
    """Test Arbitrum block monitoring for 10 seconds."""
    from src.confidence.finality_tracker import ArbitrumFinalityTracker
    from src.blockchain.block_monitor import ArbitrumBlockMonitor

    logger.info("\n" + "=" * 70)
    logger.info("Testing Arbitrum Block Monitor")
    logger.info("=" * 70)

    tracker = ArbitrumFinalityTracker()
    monitor = ArbitrumBlockMonitor("arbitrum", tracker)

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor.start_monitoring())

    # Let it run for 10 seconds
    await asyncio.sleep(10)

    # Stop monitoring
    await monitor.stop_monitoring()

    # Wait for task to complete
    try:
        await asyncio.wait_for(monitor_task, timeout=5)
    except asyncio.TimeoutError:
        monitor_task.cancel()

    # Get stats
    stats = monitor.get_stats()
    logger.info("\n📊 Arbitrum Monitor Stats:")
    logger.info(f"  Polls completed:     {stats['poll_count']}")
    logger.info(f"  Cache size:          {stats['cache_size']}/{stats['max_cache_size']}")
    logger.info(f"  Reorgs detected:     {stats['reorgs_detected']}")
    logger.info(f"  Last poll:           {stats['last_poll_time']}")

    return stats['poll_count'] > 0


async def test_solana_monitor():
    """Test Solana block monitoring for 5 seconds."""
    from src.confidence.finality_tracker import SolanaFinalityTracker
    from src.blockchain.block_monitor import SolanaBlockMonitor

    logger.info("\n" + "=" * 70)
    logger.info("Testing Solana Block Monitor")
    logger.info("=" * 70)

    tracker = SolanaFinalityTracker()
    monitor = SolanaBlockMonitor("solana", tracker)

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor.start_monitoring())

    # Let it run for 5 seconds
    await asyncio.sleep(5)

    # Stop monitoring
    await monitor.stop_monitoring()

    # Wait for task to complete
    try:
        await asyncio.wait_for(monitor_task, timeout=5)
    except asyncio.TimeoutError:
        monitor_task.cancel()

    # Get stats
    stats = monitor.get_stats()
    logger.info("\n📊 Solana Monitor Stats:")
    logger.info(f"  Polls completed:     {stats['poll_count']}")
    logger.info(f"  Cache size:          {stats['cache_size']}/{stats['max_cache_size']}")
    logger.info(f"  Reorgs detected:     {stats['reorgs_detected']}")
    logger.info(f"  Last poll:           {stats['last_poll_time']}")

    return stats['poll_count'] > 0


async def test_all_monitors():
    """Test all block monitors."""
    logger.info("=" * 70)
    logger.info("BLOCK MONITOR TESTS")
    logger.info("=" * 70)

    results = {
        "ethereum": await test_ethereum_monitor(),
        "arbitrum": await test_arbitrum_monitor(),
        "solana": await test_solana_monitor()
    }

    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    for chain, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{chain.capitalize():<12} {status}")

    all_passed = all(results.values())
    if all_passed:
        logger.info("\n🎉 All block monitors working!")
    else:
        logger.warning("\n⚠️ Some monitors failed")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_all_monitors())
    exit(0 if success else 1)
