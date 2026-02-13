"""
Test script for blockchain RPC connections.

Tests that all 3 finality trackers can connect to their respective chains
and fetch current block numbers.
"""

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_ethereum_rpc():
    """Test Ethereum RPC connection."""
    from src.layer1_core.finality.tracker import EthereumFinalityTracker

    logger.info("=" * 70)
    logger.info("Testing Ethereum RPC Connection")
    logger.info("=" * 70)

    tracker = EthereumFinalityTracker()

    try:
        block_num = await tracker.get_current_block_number()
        logger.info(f"✓ Current Ethereum block: {block_num:,}")

        # Test block existence check
        exists = await tracker.check_block_exists(block_num)
        logger.info(f"✓ Block {block_num} exists: {exists}")

        # Test a few blocks back
        old_block = block_num - 10
        exists_old = await tracker.check_block_exists(old_block)
        logger.info(f"✓ Block {old_block} exists: {exists_old}")

        return True
    except Exception as e:
        logger.error(f"✗ Ethereum RPC test failed: {e}")
        return False


async def test_arbitrum_rpc():
    """Test Arbitrum RPC connection."""
    from src.layer1_core.finality.tracker import ArbitrumFinalityTracker

    logger.info("\n" + "=" * 70)
    logger.info("Testing Arbitrum RPC Connection")
    logger.info("=" * 70)

    tracker = ArbitrumFinalityTracker()

    try:
        block_num = await tracker.get_current_block_number()
        logger.info(f"✓ Current Arbitrum block: {block_num:,}")

        # Test block existence check
        exists = await tracker.check_block_exists(block_num)
        logger.info(f"✓ Block {block_num} exists: {exists}")

        # Test a few blocks back
        old_block = block_num - 10
        exists_old = await tracker.check_block_exists(old_block)
        logger.info(f"✓ Block {old_block} exists: {exists_old}")

        return True
    except Exception as e:
        logger.error(f"✗ Arbitrum RPC test failed: {e}")
        return False


async def test_solana_rpc():
    """Test Solana RPC connection."""
    from src.layer1_core.finality.tracker import SolanaFinalityTracker

    logger.info("\n" + "=" * 70)
    logger.info("Testing Solana RPC Connection")
    logger.info("=" * 70)

    tracker = SolanaFinalityTracker()

    try:
        slot = await tracker.get_current_block_number()
        logger.info(f"✓ Current Solana slot: {slot:,}")

        # Test slot existence check
        exists = await tracker.check_block_exists(slot)
        logger.info(f"✓ Slot {slot} exists: {exists}")

        # Test a few slots back (note: some may be skipped on Solana)
        old_slot = slot - 100
        exists_old = await tracker.check_block_exists(old_slot)
        logger.info(f"✓ Slot {old_slot} exists: {exists_old}")

        return True
    except Exception as e:
        logger.error(f"✗ Solana RPC test failed: {e}")
        return False


async def test_all_rpcs():
    """Test all RPC connections."""
    logger.info("=" * 70)
    logger.info("RPC CONNECTION TESTS")
    logger.info("=" * 70)

    results = {
        "ethereum": await test_ethereum_rpc(),
        "arbitrum": await test_arbitrum_rpc(),
        "solana": await test_solana_rpc()
    }

    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    for chain, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{chain.capitalize():<12} {status}")

    all_passed = all(results.values())
    if all_passed:
        logger.info("\n🎉 All RPC connections working!")
    else:
        logger.warning("\n⚠️ Some RPC connections failed")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(test_all_rpcs())
    exit(0 if success else 1)
