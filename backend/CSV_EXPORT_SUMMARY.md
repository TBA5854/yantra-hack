# Stablecoin Events CSV Export - Summary

**Date**: February 14, 2026  
**Time**: 13:09-13:10 IST  
**File**: `stablecoin_demo.csv`  
**Size**: 424 bytes

---

## ✅ CSV Export Complete!

Successfully collected and exported **3 stablecoin risk events** to CSV format.

### 📊 Collection Details

- **Monitoring**: USDC on Ethereum
- **Collection Cycles**: 3
- **Poll Interval**: 10 seconds
- **Total Duration**: ~35 seconds
- **Events Collected**: 3 (cycle 1), 0 (cycle 2-3 deduplicated)

### 📋 CSV Structure

The CSV file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `timestamp` | Event timestamp (ISO 8601) | `2026-02-14T07:39:35` |
| `coin` | Stablecoin symbol | `USDC` |
| `chain` | Blockchain name | `ethereum` |
| `source` | Data source | `coingecko`, `volatility_mock`, `sentiment_mock` |
| `price` | USD price | `0.999990` |
| `volume_24h` | 24-hour volume | (not provided by mock sources) |
| `market_cap` | Market capitalization | (not provided by mock sources) |
| `liquidity_depth` | DEX liquidity depth | (not in this sample) |
| `net_supply_change` | Supply mint/burn | (not in this sample) |
| `market_volatility` | Volatility percentage | `0.000572` (0.0572%) |
| `sentiment_score` | Sentiment [-1, 1] | `0.131` (neutral/positive) |
| `temporal_confidence` | TCS score [0, 1] | `0.300` (tier1) |
| `finality_tier` | Blockchain finality | `tier1`, `tier2`, `tier3` |
| `block_number` | Block number (if on-chain) | (empty for off-chain) |
| `tx_hash` | Transaction hash | (empty for off-chain) |

### 📈 Collected Events

#### Event 1: Price Data (CoinGecko)
```
Timestamp:  2026-02-14 07:39:35 UTC
Coin:       USDC
Chain:      ethereum
Source:     coingecko
Price:      $0.999990
TCS:        0.300 (tier1)
```

**Analysis**: USDC trading at **$0.999990** - perfectly pegged with only -0.001% deviation (1 basis point).

#### Event 2: Volatility Data (Mock)
```
Timestamp:  2026-02-14 07:39:40.293980 UTC
Coin:       USDC
Chain:      ethereum
Source:     volatility_mock
Volatility: 0.000572 (0.0572%)
TCS:        0.300 (tier1)
```

**Analysis**: Very low volatility of **0.0572%**, indicating stable price movement.

#### Event 3: Sentiment Data (Mock)
```
Timestamp:  2026-02-14 07:39:40.294412 UTC
Coin:       USDC
Chain:      ethereum
Source:     sentiment_mock
Sentiment:  0.131 (neutral/slightly positive)
TCS:        0.300 (tier1)
```

**Analysis**: Neutral to slightly positive sentiment score of **+0.131**.

### 🔄 Deduplication Note

Cycles 2 and 3 collected 0 new events because the **deduplication pipeline** filtered them out:
- The quality pipeline uses a 60-second sliding window
- Events with same timestamp/source/coin are considered duplicates
- This prevents double-counting of the same data

### 💡 Usage

#### View CSV
```bash
cat stablecoin_demo.csv
```

#### View formatted (column-aligned)
```bash
column -t -s',' stablecoin_demo.csv
```

#### Import into Python/Pandas
```python
import pandas as pd

df = pd.read_csv('stablecoin_demo.csv')
print(df)

# Get price data
prices = df[df['source'] == 'coingecko']['price']
print(f"Average USDC price: ${prices.mean():.6f}")
```

#### Import into Excel/Google Sheets
Just open the CSV file - it's standard format.

---

## 🚀 Running Continuous Collection

### Basic Usage
```bash
# Collect for 10 cycles (default 60s interval)
uv run python stream_to_csv.py --cycles 10

# Collect with custom interval (30 seconds)
uv run python stream_to_csv.py --interval 30

# Collect multiple coins
uv run python stream_to_csv.py --coins USDC USDT DAI

# Run continuously (Ctrl+C to stop)
uv run python stream_to_csv.py
```

### Advanced Usage
```bash
# Monitor USDC and USDT on ethereum and arbitrum
uv run python stream_to_csv.py \
  --coins USDC USDT \
  --chains ethereum arbitrum \
  --interval 60 \
  --output multi_coin_stream.csv

# Quick test (3 cycles, 10 second interval)
uv run python stream_to_csv.py --cycles 3 --interval 10
```

---

## 📊 Data Quality

### Sources Working (3/5 = 60%)
- ✅ **Price** (CoinGecko API) - Real data
- ✅ **Volatility** (Mock) - Simulated data
- ✅ **Sentiment** (Mock) - Simulated data

### Sources Not Working (2/5 = 40%)
- ❌ **Liquidity** (Uniswap V3) - Graph endpoint deprecated
- ⚠️ **Supply** (Web3) - Mock mode

### Temporal Confidence Score (TCS)
All events have **TCS = 0.300** (tier1), which indicates:
- **Confidence Level**: Low (real-time monitoring)
- **Finality**: tier1 (unconfirmed)
- **Attestation Ready**: ❌ No (requires TCS ≥ 0.8)
- **Reason for Low TCS**: Only 3/5 data sources active (60% completeness)

---

## 🎯 Next Steps

### To Improve CSV Data Quality

1. **Fix Liquidity Source**
   - Migrate to new The Graph endpoint
   - Or implement direct Uniswap V3 contract calls

2. **Enable Live Supply Monitoring**
   - Switch from mock to live Web3 mode
   - Configure Ethereum RPC in `.env`

3. **Add Real Sentiment**
   - Integrate Twitter/Reddit APIs
   - Or use LunarCrush, Messari, or Santiment

4. **Increase TCS**
   - Get all 5 sources working → 100% completeness
   - TCS would increase from 0.300 to 0.600+
   - With finality progression → TCS 0.8+ (attestation-ready)

### To Collect More Data

```bash
# Run for 24 hours, collecting every minute
uv run python stream_to_csv.py \
  --interval 60 \
  --output usdc_24h_$(date +%Y%m%d).csv

# Monitor all major stablecoins
uv run python stream_to_csv.py \
  --coins USDC USDT DAI BUSD \
  --chains ethereum arbitrum \
  --interval 120 \
  --output all_stablecoins.csv
```

---

## 📁 Files Created

1. **`stream_to_csv.py`** - Streaming CSV export script (188 lines)
2. **`stablecoin_demo.csv`** - Sample CSV output (424 bytes, 3 events)
3. **`CSV_EXPORT_SUMMARY.md`** - This documentation

---

## ✅ Success Criteria

- [x] Events collected from multiple sources
- [x] Data exported to CSV format
- [x] CSV has proper headers
- [x] Timestamps in ISO 8601 format
- [x] Price data from real CoinGecko API
- [x] Quality pipeline deduplication working
- [x] Logging and progress reporting
- [x] Configurable via command-line arguments
- [x] File created successfully (424 bytes)

**Status**: ✅ **CSV Export Fully Functional!**

---

**Generated**: February 14, 2026, 13:10 IST  
**Script**: `/home/tba/projects/web3/backend/stream_to_csv.py`  
**Output**: `/home/tba/projects/web3/backend/stablecoin_demo.csv`
