# Free Alternative Data Sources for Crashed Stablecoins

## Problem
CoinGecko Demo/Free API blocks historical data from 2021-2022:
- "Your request exceeds the allowed time range"
- Only allows last ~90 days

## Free Alternatives

### 1. **CryptoCompare API** (Free Tier)
- **URL**: https://min-api.cryptocompare.com
- **Historical Data**: ✅ YES - up to 2000 days
- **Free Tier**: 100,000 calls/month
- **Endpoints**:
  - `/data/v2/histohour` - Hourly OHLCV
  - `/data/v2/histoday` - Daily OHLCV
- **No API key required** for basic usage
- **Example**:
  ```bash
  curl "https://min-api.cryptocompare.com/data/v2/histohour?fsym=USDD&tsym=USD&limit=168&toTs=1655596800"
  # 168 hours = 7 days, toTs = June 18, 2022 (USDD crash end)
  ```

### 2. **Binance Public API** (No Auth Required)
- **URL**: https://api.binance.com/api/v3/klines
- **Historical Data**: ✅ YES - back to listing date
- **Free Tier**: Unlimited (with rate limits)
- **Issues for our coins**:
  - USDD: Not currently listed (was USDDUSDT)
  - USDN: Never listed
  - BAC: Never listed
  - SETD: Never listed
- **Only useful if coins were historically listed**

### 3. **Messari API** (Free Tier)
- **URL**: https://data.messari.io/api
- **Historical Data**: ✅ YES - full history
- **Free Tier**: 20 calls/minute, 1000/month
- **Endpoints**:
  - `/v1/assets/{asset}/metrics/price/time-series`
- **Requires free API key**
- **Coverage**: Most major assets including failed stablecoins

### 4. **The Graph (Uniswap V2/V3 Subgraphs)**
- **URL**: https://thegraph.com/explorer
- **Historical Data**: ✅ YES - from pool creation
- **Free Tier**: Unlimited queries
- **Data**: DEX trades, liquidity, volume
- **Example** for USDD:
  ```graphql
  query {
    pairDayDatas(
      where: {
        token0: "0x0c10bf8fcb7bf5412187a595ab97a3609160b5c6" # USDD
        date_gte: 1654992000  # June 12, 2022
        date_lte: 1655596800  # June 18, 2022
      }
    ) {
      date
      reserve0
      reserve1
      volumeUSD
    }
  }
  ```

### 5. **CoinMarketCap API** (Free Tier)
- **URL**: https://coinmarketcap.com/api
- **Historical Data**: ❌ NO for free tier
- **Free Tier**: Only latest data
- **Not useful for crash periods**

## Recommended Approach

### **Option 1: CryptoCompare (Easiest)**
```python
import aiohttp

async def fetch_cryptocompare_historical(coin_symbol, start_ts, end_ts):
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": coin_symbol,  # e.g., "USDD"
        "tsym": "USD",
        "limit": 2000,
        "toTs": end_ts  # Unix timestamp
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            return data["Data"]["Data"]  # List of OHLCV candles
```

**Pros**:
- ✅ No API key required
- ✅ Simple REST API
- ✅ Hourly granularity
- ✅ Covers all our coins

**Cons**:
- ⚠️ Rate limited (free tier)
- ⚠️ May not have SETD/BAC data

### **Option 2: The Graph (Most Complete)**
```python
async def fetch_uniswap_historical(token_address, start_date, end_date):
    query = """
    query($token: String!, $start: Int!, $end: Int!) {
      pairDayDatas(
        where: {
          token0: $token
          date_gte: $start
          date_lte: $end
        }
      ) {
        date
        reserve0
        reserve1
        volumeUSD
      }
    }
    """
    # Execute GraphQL query against Uniswap V2/V3 subgraph
```

**Pros**:
- ✅ Free, unlimited queries
- ✅ On-chain DEX data (most reliable)
- ✅ Liquidity depth included

**Cons**:
- ⚠️ Requires token contract addresses
- ⚠️ Only covers DEX activity (not CEX)
- ⚠️ GraphQL more complex

### **Option 3: Messari API (Professional Grade)**
```python
async def fetch_messari_historical(asset_slug, start, end):
    url = f"https://data.messari.io/api/v1/assets/{asset_slug}/metrics/price/time-series"
    params = {
        "start": start,  # ISO format: "2022-06-12"
        "end": end,
        "interval": "1h"
    }
    headers = {"x-messari-api-key": "YOUR_FREE_KEY"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            return data["data"]["values"]
```

**Pros**:
- ✅ Professional-grade data
- ✅ Full historical coverage
- ✅ 1-hour granularity

**Cons**:
- ⚠️ Requires free API key signup
- ⚠️ 1000 calls/month limit

## Implementation Plan

1. **Add CryptoCompare collector** (quickest win)
2. **Fallback to The Graph** if CryptoCompare missing data
3. **Messari as backup** for obscure coins

Next step: Which source would you like me to implement first?
