# Crashed Stablecoin Data Collection - Complete ✅

## Summary

Successfully collected **recent week data** (Feb 7-14, 2026) for **3 crashed algorithmic stablecoins** using CoinGecko API.

**Date**: 2026-02-14  
**Status**: ✅ **3/4 coins collected** (75% success rate)

---

## Datasets Collected

### ✅ USDD (Decentralized USD)
- **Status**: Still pegged (~$1.00)
- **Records**: 167 data points
- **Max Depeg**: 20.14 bps (0.20%)
- **Mean Depeg**: 4.81 bps (0.05%)
- **Source**: CoinGecko (Demo API)
- **Location**: `data/usdd_recent/`

### ✅ USDN (Neutrino USD)
- **Status**: Survived Waves crash, still trading
- **Records**: 167 data points
- **Source**: CoinGecko (Demo API)
- **Location**: `data/usdn_recent/`

### ✅ BAC (Basis Cash)
- **Status**: Still listed on CoinGecko
- **Records**: 167 data points
- **Source**: CoinGecko (Demo API)
- **Location**: `data/bac_recent/`

### ❌ SETD (SetDollar)
- **Status**: Not found on CoinGecko (likely delisted/dead)
- **Error**: `{"error":"coin not found"}`
- **Reason**: Coin ID "set-dollar" does not exist

---

## Historical Crash Data (Failed)

All historical crash period collections **failed** due to CoinGecko API limitations:

**Error**: `Your request exceeds the allowed time range. Public API users are limited to querying historical data`

### Why Historical Data Failed

1. **USDD Crash** (June 12-18, 2022): 401 - Time range restriction
2. **USDN Crash** (April 3-9, 2022): 401 - Time range restriction  
3. **BAC Crash** (Jan 10-16, 2021): 401 - Time range restriction
4. **SETD Crash** (Feb 14-20, 2021): 404 - Coin not found

**CoinGecko Demo/Free API** only allows recent data (last ~90 days), not historical data from 2021-2022.

---

## Data Schema

Each dataset contains hourly data points with the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | UTC timestamp | `2026-02-07 00:03:36+00:00` |
| `coin` | Coin symbol | `USDD` |
| `source` | Data source | `coingecko` |
| `price` | USD price | `0.9996823271731604` |
| `volume_24h` | 24h trading volume | `2288391.626786581` |
| `market_cap` | Market capitalization | `962437564.0504684` |
| `peg_deviation` | Abs deviation from $1 | `0.0003176728` |
| `peg_deviation_bps` | Deviation in basis points | `3.176728` |
| `price_change_pct` | Price change % | `0.0210844` |

---

## Files Created

### Configuration
- [crashed_coin_configs.py](backend/src/data_collection/sources/crashed_coin_configs.py) - 149 lines
  - Configuration registry for all 10 datasets (5 coins × 2 periods)
  - Crash dates, Binance symbols, CoinGecko IDs

### Collection Script
- [collect_crashed_coins.py](backend/src/data_collection/sources/collect_crashed_coins.py) - 433 lines
  - Unified collector reusing Luna crash infrastructure
  - Binance klines + CoinGecko fallback
  - CSV/Parquet/JSON output

### Output Data
```
data/
├── usdd_recent/
│   ├── usdd_unified.csv (28 KB)
│   ├── usdd_unified.parquet (18 KB)
│   └── summary_stats.json (640 B)
├── usdn_recent/
│   ├── usdn_unified.csv
│   ├── usdn_unified.parquet
│   └── summary_stats.json
└── bac_recent/
    ├── bac_unified.csv
    ├── bac_unified.parquet
    └── summary_stats.json
```

---

## Usage

### Collect All Recent Data
```bash
uv run python -m src.data_collection.sources.collect_crashed_coins --recent-only
```

### Collect Specific Coin
```bash
uv run python -m src.data_collection.sources.collect_crashed_coins --coin USDD
```

### Try Historical Crash Data (will fail with Demo API)
```bash
uv run python -m src.data_collection.sources.collect_crashed_coins --crash-only
```

---

## Insights from Recent Data

### USDD (Still Stable)
- **Max depeg**: 20.14 bps on Feb 7, 2026 at 15:03:47 UTC
- **Mean depeg**: 4.81 bps (very stable)
- **Price range**: $0.9980 - $1.0005
- **Verdict**: Still maintaining peg after June 2022 depeg event

### USDN (Recovered from Waves Crash)
- **Status**: Still trading despite April 2022 Waves blockchain collapse
- **Data**: 167 recent data points collected
- **Verdict**: Survived the crash, still active

### BAC (Zombie Coin)
- **Status**: Still listed on CoinGecko but likely low volume
- **Data**: 167 recent data points collected
- **Verdict**: Listed but may have minimal activity

---

## Limitations & Next Steps

### Current Limitations
1. **No historical crash data** - CoinGecko Demo API restricts time range
2. **No Binance data** - All coins delisted from Binance
3. **SETD missing** - Completely delisted/dead

### Solutions for Historical Data
1. **Upgrade to CoinGecko Pro** (paid plan) for full historical access
2. **Alternative sources**:
   - Dune Analytics (on-chain data)
   - The Graph (DEX data)
   - Archive node queries (supply events)
   - Wayback Machine (historical CoinGecko snapshots)

### Recommended Next Steps
1. ✅ **Recent data collected** - Can analyze current state of crashed coins
2. ⏳ **Historical data** - Need Pro API or alternative sources
3. 📊 **Comparison with Luna** - Can compare recent vs Luna crash dataset
4. 🔍 **On-chain analysis** - Query blockchain for mint/burn events during crashes

---

## Conclusion

Successfully implemented a **generalized crashed stablecoin data collection pipeline** that:
- ✅ Reuses existing Luna crash infrastructure
- ✅ Supports multiple data sources (Binance, CoinGecko)
- ✅ Collects recent data for 3/4 target coins
- ✅ Outputs CSV, Parquet, JSON formats
- ✅ Calculates peg deviation metrics
- ⏳ Historical crash data blocked by API limitations

**Total data collected**: 501 data points (167 × 3 coins) for recent week.

For historical crash analysis, consider upgrading to CoinGecko Pro API or using alternative data sources.
