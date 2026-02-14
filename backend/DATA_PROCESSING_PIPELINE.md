# CSV Data Processing Pipeline - Raw vs Normalized

**Question**: Is the CSV data raw or modified/normalized?

**Answer**: The data goes through a **Quality Pipeline** with normalization, but it's **minimal and transparent**. Here's exactly what happens:

---

## 📊 Data Processing Stages

The data flows through 3 quality stages before being written to CSV:

```
API Source → Quality Pipeline → CSV File
             ├─ 1. Normalization
             ├─ 2. Deduplication  
             └─ 3. Outlier Detection
```

---

## Stage 1: Normalization ✏️

**Purpose**: Standardize formats and apply safety bounds

### What Gets Modified:

1. **Coin Symbols** → Uppercase
   - Example: `usdc` → `USDC`

2. **Chain Names** → Lowercase
   - Example: `Ethereum` → `ethereum`

3. **Timestamps** → UTC (timezone removed)
   - Example: `2026-02-14T13:17:12+05:30` → `2026-02-14T07:47:12`

4. **Price Clamping** (for stablecoins)
   - **Min**: $0.95
   - **Max**: $1.05
   - If price < $0.95 → clamped to $0.95 ⚠️
   - If price > $1.05 → clamped to $1.05 ⚠️
   - **Warning logged** when clamping occurs

### What Stays Raw:

- ✅ **Price values** (within $0.95-$1.05 range)
- ✅ **Volume data**
- ✅ **Market cap**
- ✅ **Liquidity depth**
- ✅ **Supply changes**
- ✅ **All numerical metrics** (no rounding or averaging)

**Configuration**:
```python
# From config.py
QUALITY_CONFIG = {
    "price_bounds": (0.95, 1.05),  # Min/max for stablecoins
}
```

---

## Stage 2: Deduplication 🔍

**Purpose**: Remove duplicate events within a time window

### How It Works:

1. **Event Signature** created from:
   - Coin + Chain + Source
   - Price (6 decimals)
   - Liquidity (2 decimals)
   - Volume (2 decimals)

2. **Dedup Window**: 60 seconds
   - If identical event seen within 60s → **filtered out**
   - Prevents double-counting same data

3. **Example**:
   ```
   Event 1: USDC/ethereum/coingecko/$0.999919 at 07:43:32
   Event 2: USDC/ethereum/coingecko/$0.999919 at 07:43:35
   → Event 2 FILTERED (duplicate within 60s)
   ```

### What Gets Removed:

- ❌ Exact duplicates within 60 seconds
- ❌ Events with identical coin, chain, source, and values

### What Stays:

- ✅ Same coin on different chains (ethereum vs arbitrum)
- ✅ Same coin from different sources (coingecko vs chainlink)
- ✅ Different prices for same coin
- ✅ Events more than 60 seconds apart

**Configuration**:
```python
QUALITY_CONFIG = {
    "dedup_window_sec": 60,  # 1 minute deduplication window
}
```

---

## Stage 3: Outlier Detection 📈

**Purpose**: Flag statistical anomalies (doesn't remove data)

### How It Works:

1. **Z-Score Calculation**:
   ```
   z-score = |value - mean| / standard_deviation
   ```

2. **Threshold**: z-score > 3.0 → flagged as outlier

3. **Per-Market Detection**:
   - Groups by (coin, chain)
   - Each market analyzed separately
   - Requires minimum 3 events

4. **Metrics Analyzed**:
   - Price outliers
   - Liquidity outliers

### What Happens to Outliers:

- ⚠️ **Flagged** with `is_outlier = True`
- ⚠️ **Quality score** reduced by 50% (1.0 → 0.5)
- ⚠️ **Warning logged**
- ✅ **Still included** in CSV (not removed!)

**Configuration**:
```python
QUALITY_CONFIG = {
    "outlier_z_threshold": 3.0,  # 3 standard deviations
}
```

---

## What's Written to CSV?

### Raw Data (Unmodified):
- ✅ **Price values** (exact from API, unless clamped)
- ✅ **Volume** (exact)
- ✅ **Market cap** (exact)
- ✅ **Liquidity** (exact)
- ✅ **All metrics** (no averaging, no rounding)

### Normalized Data (Standardized):
- 📝 **Timestamps** (UTC format, timezone removed)
- 📝 **Coin symbols** (UPPERCASE)
- 📝 **Chain names** (lowercase)

### Filtered Data (May Be Missing):
- ❌ **Duplicates** (identical events within 60s)
- ⚠️ **Extreme outliers** (flagged but still included)

---

## Example: Full Pipeline Trace

### Input (from CoinGecko API):
```json
{
  "usd-coin": {
    "usd": 0.999919,
    "last_updated_at": 1708003412
  }
}
```

### After Stage 1 (Normalization):
```python
RiskEvent(
  coin="USDC",              # ← Uppercase
  chain="ethereum",         # ← Lowercase
  source="coingecko",
  price=0.999919,           # ← RAW (within bounds)
  timestamp=datetime(2026, 2, 14, 7, 43, 32),  # ← UTC
  quality_score=1.0
)
```

### After Stage 2 (Deduplication):
```python
# Check signature: "USDC|ethereum|coingecko|0.999919|none|none"
# Not seen in last 60s → KEEP ✅
```

### After Stage 3 (Outlier Detection):
```python
# z-score = |0.999919 - 0.999920| / 0.000001 = 1.0
# z-score < 3.0 → NOT an outlier ✅
```

### Final CSV Output:
```csv
2026-02-14T07:43:32,USDC,ethereum,coingecko,0.999919,,,,,,,0.300,tier1,,
```

**Result**: Price is **RAW** (0.999919 exactly as received from API) ✅

---

## Summary: Raw vs Normalized

| Aspect | Raw? | Modified? | How? |
|--------|------|-----------|------|
| **Price values** | ✅ Yes | ⚠️ Clamped | Only if < $0.95 or > $1.05 |
| **Volume** | ✅ Yes | ❌ No | Exact from API |
| **Market cap** | ✅ Yes | ❌ No | Exact from API |
| **Liquidity** | ✅ Yes | ❌ No | Exact from API |
| **Timestamps** | ❌ No | ✅ Yes | Converted to UTC |
| **Coin symbols** | ❌ No | ✅ Yes | UPPERCASE |
| **Chain names** | ❌ No | ✅ Yes | lowercase |
| **Duplicates** | - | ✅ Removed | Within 60s window |
| **Outliers** | ✅ Yes | ⚠️ Flagged | Included but marked |

---

## Disable Normalization (Get Truly Raw Data)

If you want **100% raw data** with NO processing:

### Option 1: Bypass Quality Pipeline

```python
# In stream_to_csv.py or orchestrator
orchestrator = DataCollectionOrchestrator(
    coins=["USDC"],
    chains=["ethereum"],
    enable_quality_pipeline=False  # ← DISABLE
)
```

**Result**: No normalization, no deduplication, no outlier detection

### Option 2: Modify Price Bounds

```python
# In config.py
QUALITY_CONFIG = {
    "price_bounds": (0.0, 999.0),  # Allow any price (no clamping)
    "dedup_window_sec": 0,          # Disable deduplication
    "outlier_z_threshold": 999.0,   # Disable outlier flagging
}
```

### Option 3: Direct API-to-CSV

Write a simple script that bypasses the orchestrator entirely:

```python
import csv
from src.data_collection.sources.price_source import price_source

# Fetch raw price
event = await price_source.fetch_price("USDC", "ethereum")

# Write directly to CSV (no processing)
with open('raw_data.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow([event.timestamp, event.coin, event.price])
```

---

## Current Configuration Summary

**As of February 14, 2026:**

### Processing Enabled:
- ✅ Normalization (timestamps, case standardization)
- ✅ Deduplication (60s window)
- ✅ Outlier detection (z-score > 3.0)
- ✅ Price bounds ($0.95 - $1.05)

### Data Integrity:
- ✅ **Price values are RAW** (within safety bounds)
- ✅ **No averaging** or aggregation
- ✅ **No rounding** beyond API precision
- ✅ **Transparent processing** (all modifications logged)

### Files:
- **Quality Pipeline**: `/home/tba/projects/web3/backend/src/data_collection/quality/pipeline.py`
- **Configuration**: `/home/tba/projects/web3/backend/src/common/config.py`
- **CSV Writer**: `/home/tba/projects/web3/backend/stream_to_csv.py`

---

## Verdict: Mostly Raw with Safety Guardrails ✅

The CSV data is **mostly raw** with these exceptions:

1. **Format standardization** (timestamps, case)
2. **Duplicate removal** (prevents double-counting)
3. **Safety bounds** ($0.95-$1.05 for stablecoins)
4. **Outlier flagging** (for transparency)

**All modifications are:**
- ✅ Logged
- ✅ Transparent
- ✅ Reversible (via config)
- ✅ Minimal (preserves original values)

**Bottom line**: You're getting **real API data with quality assurance**, not synthetic or heavily transformed data. 🎯

---

**Generated**: February 14, 2026  
**Pipeline Version**: 1.0  
**Quality Stages**: 3 (Normalization, Deduplication, Outlier Detection)
