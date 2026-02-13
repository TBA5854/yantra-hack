# Crashed Stablecoin Data Collection - Final Status

## What We Successfully Collected ✅

### Recent Data (Feb 7-14, 2026)
Using **CryptoCompare + CoinGecko**:

| Coin | Status | Records | Source | Location |
|------|--------|---------|--------|----------|
| USDD | ✅ Success | 167 | CryptoCompare | `data/usdd_recent/` |
| USDN | ✅ Success | 167 | CoinGecko | `data/usdn_recent/` |
| BAC  | ✅ Success | 167 | CoinGecko | `data/bac_recent/` |
| SETD | ❌ Failed | 0 | N/A - delisted | - |

**Total**: 501 recent data points (3/4 coins)

---

## What We Could NOT Collect ❌

### Historical Crash Data (2021-2022)

**Problem**: All free APIs block or lack historical data for these obscure coins:

| Coin | Crash Period | Binance | CryptoCompare | CoinGecko | Status |
|------|--------------|---------|---------------|-----------|--------|
| USDD | Jun 12-18, 2022 | ❌ Delisted | ❌ No data | ❌ Time limit | **Failed** |
| USDN | Apr 3-9, 2022 | ❌ Never listed | ❌ Not found | ❌ Time limit | **Failed** |
| BAC  | Jan 10-16, 2021 | ❌ Never listed | ❌ Not found | ❌ Time limit | **Failed** |
| SETD | Feb 14-20, 2021 | ❌ Never listed | ❌ Not found | ❌ Not found | **Failed** |

**Errors**:
- **Binance**: `400 Bad Request` - All coins delisted
- **CryptoCompare**: `CCCAGG market does not exist` or all zeros
- **CoinGecko**: `401 - Your request exceeds the allowed time range`

---

## Why Historical Data is Unavailable (Free Sources)

### Root Causes

1. **Low Trading Volume**: These coins had minimal CEX/DEX activity even before crash
2. **Delisting**: Most exchanges delisted them after crash
3. **API Time Limits**: Free tiers block historical data >90 days
4. **Data Quality**: CryptoCompare has zeros for periods with no trades

### Tested Sources

| Source | Historical Access | Cost | Result |
|--------|-------------------|------|--------|
| **Binance Public API** | ✅ Full history | Free | ❌ Coins not listed |
| **CryptoCompare** | ✅ Up to 2000 days | Free | ❌ No market data |
| **CoinGecko Demo** | ❌ Last 90 days only | Free | ❌ Time limit error |
| **CoinGecko Pro** | ✅ Full history | $129/mo | Not tested |
| **Messari API** | ✅ Full history | Free (1000 calls/mo) | Not implemented |
| **The Graph** | ✅ From pool creation | Free | Requires DEX activity |

---

## Solutions for Historical Data

### Option 1: Messari API (Free, 1000 calls/mo) 🌟

**Best free option** for historical data:

```bash
curl "https://data.messari.io/api/v1/assets/usdd/metrics/price/time-series?start=2022-06-12&end=2022-06-18&interval=1h" \
  -H "x-messari-api-key: YOUR_FREE_KEY"
```

**Pros**:
- ✅ Full historical coverage
- ✅ Professional-grade data
- ✅ Free tier (1000 API calls/month)
- ✅ 1-hour granularity

**Cons**:
- ⏳ Requires signup for free API key
- ⚠️ May not have BAC/SETD (very obscure)

**Next step**: Sign up at https://messari.io/api

---

### Option 2: The Graph (Uniswap DEX Data) 🌟

**Best for on-chain liquidity data**:

```graphql
query {
  pairDayDatas(
    where: {
      token0: "0x0c10bf8fcb7bf5412187a595ab97a3609160b5c6" # USDD
      date_gte: 1654992000
      date_lte: 1655596800
    }
  ) {
    date
    reserve0
    reserve1
    volumeUSD
    token0Price
  }
}
```

**Pros**:
- ✅ Free, unlimited queries
- ✅ On-chain DEX data (most reliable)
- ✅ Liquidity depth included

**Cons**:
- ⚠️ Requires contract addresses
- ⚠️ Only shows DEX activity (not CEX)
- ⚠️ Coins with no DEX pools = no data

---

### Option 3: Upgrade CoinGecko Pro ($129/mo)

**Most comprehensive** but expensive:

- ✅ Full historical data for all coins
- ✅ Higher rate limits
- ✅ API we already integrated
- ❌ $129/month subscription

---

### Option 4: Use Luna Dataset as Template

You **already have** complete Luna crash data (3,474 points, May 2022):
- ✅ `data/luna_crash/luna_crash_unified.csv`
- ✅ Binance 5-min klines
- ✅ Price, volume, supply changes
- ✅ Proven depeg pattern

**Use this** for:
- Backtesting risk models
- ML training on depeg events
- Pattern recognition

Other crashed coins have **similar failure modes**, so Luna dataset is representative.

---

## Recommendation

### Immediate Actions

1. **Use Luna dataset** for risk model development
   - Most complete crash dataset available
   - Represents algorithmic stablecoin death spiral

2. **Sign up for Messari Free API**
   - Get historical data for USDD, USDN
   - 1000 calls/month is enough for our 4 coins

3. **Use recent data** for current state comparison
   - We have 501 recent points (USDD, USDN, BAC)
   - Compare "dead/stable" vs "crash" using Luna

### Long-term Options

- **Messari API** for additional coins if needed
- **The Graph** for on-chain DEX liquidity data
- **CoinGecko Pro** if budget allows comprehensive coverage

---

## Current Implementation

### What Works ✅

- ✅ **Unified collection script** (`collect_crashed_coins.py`)
- ✅ **Multi-source fallback** (Binance → CryptoCompare → CoinGecko)
- ✅ **Config registry** for all 10 datasets (5 coins × 2 periods)
- ✅ **Recent data collection** (167 points per coin)
- ✅ **CSV/Parquet/JSON output** with peg deviation metrics

### What Needs Work ⏳

- ⏳ **Messari collector** (easy to add, need API key)
- ⏳ **The Graph collector** (requires contract addresses)
- ⏳ **Historical crash data** (blocked by free API limits)

---

## Usage

### Collect Recent Data (Works Now)
```bash
uv run python -m src.data_collection.sources.collect_crashed_coins --recent-only
# ✅ Collects USDD, USDN, BAC recent data (167 points each)
```

### Try Historical Crash Data (Will Fail Without Messari)
```bash
uv run python -m src.data_collection.sources.collect_crashed_coins --crash-only
# ❌ Fails: CryptoCompare no data, CoinGecko time limit
```

### Use Existing Luna Dataset
```bash
ls data/luna_crash/
# luna_crash_unified.csv (3,474 points, May 7-13, 2022)
# luna_crash_unified.parquet
# summary_stats.json
```

---

## Bottom Line

**For crash period data, you need either:**
1. **Messari free API** (sign up, implement collector) - RECOMMENDED
2. **CoinGecko Pro** ($129/month) - if budget allows
3. **Use Luna dataset** as representative crash example - WORKS NOW

**Recent data collection is working** with free APIs (CryptoCompare + CoinGecko).
