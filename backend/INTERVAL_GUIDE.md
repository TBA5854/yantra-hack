# Interval Parameter Guide

## What `--interval` Does

**Controls**: How often data is collected (polling frequency)

**Units**: Seconds

**Default**: 60 seconds (1 minute)

---

## Quick Examples

```bash
# Every 10 seconds (testing)
uv run python stream_to_csv.py --interval 10

# Every 1 minute (default, real-time)
uv run python stream_to_csv.py --interval 60

# Every 5 minutes (standard)
uv run python stream_to_csv.py --interval 300

# Every 1 hour (historical)
uv run python stream_to_csv.py --interval 3600
```

---

## Timeline Visualization

### Example: `--interval 60` (1 minute)

```
Time     | Action
---------|------------------------------------------
13:00:00 | Cycle 1: Collect data → CSV (price: $0.999919)
13:00:05 | ... waiting ...
13:01:00 | Cycle 2: Collect data → CSV (price: $0.999920)
13:01:05 | ... waiting ...
13:02:00 | Cycle 3: Collect data → CSV (price: $0.999918)
```

### Example: `--interval 300` (5 minutes)

```
Time     | Action
---------|------------------------------------------
13:00:00 | Cycle 1: Collect data → CSV
13:05:00 | Cycle 2: Collect data → CSV
13:10:00 | Cycle 3: Collect data → CSV
```

---

## Choosing the Right Interval

### Factors to Consider:

1. **API Rate Limits**
   - CoinGecko Demo: 50 requests/minute
   - With 3 chains: Each cycle = 3 requests
   - Max frequency: ~20 seconds between cycles

2. **Data Requirements**
   - Real-time monitoring: 30-60 seconds
   - Trend analysis: 300 seconds (5 min)
   - Historical records: 3600 seconds (1 hour)

3. **Storage Costs**
   - 10s interval: 8,640 events/day/coin
   - 60s interval: 1,440 events/day/coin
   - 300s interval: 288 events/day/coin

4. **Data Freshness**
   - Stablecoin depegs happen in minutes
   - 60s provides good balance
   - 10s for critical monitoring

---

## Recommendations by Use Case

### 🔴 High-Frequency Trading / Alerts
```bash
--interval 10   # Every 10 seconds
```
- **Pros**: Catch depegs immediately
- **Cons**: High API usage, large CSV files
- **Cost**: ~8,640 events/day per coin

### 🟡 Real-Time Monitoring (RECOMMENDED)
```bash
--interval 60   # Every 1 minute (default)
```
- **Pros**: Good balance of freshness and efficiency
- **Pros**: Catches most events quickly
- **Cons**: Minimal
- **Cost**: ~1,440 events/day per coin

### 🟢 Standard Monitoring
```bash
--interval 300  # Every 5 minutes
```
- **Pros**: Lower API usage, smaller files
- **Cons**: May miss brief depegs
- **Cost**: ~288 events/day per coin

### 🔵 Historical Data Collection
```bash
--interval 3600  # Every 1 hour
```
- **Pros**: Minimal API usage, tiny files
- **Cons**: Not suitable for real-time monitoring
- **Cost**: ~24 events/day per coin

---

## Data Volume Examples

### Scenario: Monitor USDC on 3 chains for 24 hours

| Interval | Events/Day | CSV Size (est.) | API Calls/Day |
|----------|------------|-----------------|---------------|
| 10s | 25,920 | ~3.2 MB | 25,920 |
| 30s | 8,640 | ~1.1 MB | 8,640 |
| 60s | 4,320 | ~540 KB | 4,320 |
| 300s | 864 | ~108 KB | 864 |
| 3600s | 72 | ~9 KB | 72 |

*Assumes 125 bytes per event*

---

## Combined with Other Parameters

### Example 1: Quick Test
```bash
uv run python stream_to_csv.py \
  --coins USDC \
  --chains ethereum \
  --interval 5 \
  --cycles 3 \
  --output test.csv
```
**Result**: Collect 3 times, every 5 seconds (~15 seconds total)

### Example 2: 24-Hour Monitoring
```bash
uv run python stream_to_csv.py \
  --coins USDC USDT \
  --chains ethereum arbitrum solana \
  --interval 60 \
  --output monitoring_24h.csv
```
**Result**: Collect every minute, continuously until stopped

### Example 3: Low-Frequency Historical
```bash
uv run python stream_to_csv.py \
  --coins USDC \
  --chains ethereum \
  --interval 3600 \
  --cycles 24 \
  --output historical_24h.csv
```
**Result**: Collect 24 times (24 hours), once per hour

---

## Deduplication Impact

**Important**: The quality pipeline deduplicates events within **60 seconds**

**Scenario**:
- Interval: 10 seconds
- CoinGecko updates: Every 60 seconds
- Result: Most events deduplicated!

```
Time     | Action              | Deduplicated?
---------|---------------------|---------------
13:00:00 | Price: $0.999919   | ✅ Kept
13:00:10 | Price: $0.999919   | ❌ Duplicate (same price within 60s)
13:00:20 | Price: $0.999919   | ❌ Duplicate
13:00:30 | Price: $0.999919   | ❌ Duplicate
13:01:00 | Price: $0.999920   | ✅ Kept (new price)
```

**Recommendation**: Match interval to data update frequency
- CoinGecko: Updates ~60 seconds → Use 60s interval
- On-chain data: Updates per block → Use block time

---

## API Rate Limit Considerations

### CoinGecko Demo API
- **Limit**: 50 requests/minute
- **Your setup**: 3 chains = 3 requests per cycle
- **Max safe frequency**: 60s / 3 = ~20 seconds minimum

**Safe intervals**:
- ✅ 60s (1 req/min per chain → 3 req/min total)
- ✅ 30s (2 req/min per chain → 6 req/min total)
- ⚠️ 10s (6 req/min per chain → 18 req/min total)
- ❌ 5s (12 req/min per chain → 36 req/min total) - Too close to limit

---

## Current Configuration

**Your running command** (if still running):
```bash
stream_to_csv.py --coins USDC UST DAI --chains ethereum arbitrum...
```

**Default interval**: 60 seconds (since not specified)

**Calculation**:
- 3 coins × 3 chains = 9 requests per cycle
- Every 60 seconds
- = 9 requests/minute
- ✅ Well within 50 req/min limit

---

## Summary

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| `--interval` | 60 | 1-∞ | Seconds between collection cycles |
| `--cycles` | ∞ | 1-∞ | Number of cycles before stopping |

**Formula**:
```
Total runtime = interval × cycles

Example: --interval 60 --cycles 10
= 60 seconds × 10 cycles
= 600 seconds = 10 minutes
```

**Best practice**: Start with default (60s), adjust based on needs! 🎯

---

**Generated**: February 14, 2026  
**Default Interval**: 60 seconds  
**Recommended**: 60-300 seconds for most use cases
