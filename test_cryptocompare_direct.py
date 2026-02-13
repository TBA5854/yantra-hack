import asyncio
import aiohttp
import os
from datetime import datetime, timezone

async def test_cryptocompare():
    # USDD crash: June 12-18, 2022
    start = datetime(2022, 6, 12, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2022, 6, 18, 23, 59, 59, tzinfo=timezone.utc)
    
    end_ts = int(end.timestamp())
    
    api_key = "bd25d756776bfbf97826408037aac385d673c03b5ca954be21565565e4b8d05f"
    
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": "USDD",
        "tsym": "USD",
        "limit": 168,  # 7 days * 24 hours
        "toTs": end_ts
    }
    
    headers = {"authorization": f"Apikey {api_key}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            
            print(f"\nResponse keys: {data.keys()}")
            print(f"\nResponse: {data.get('Response')}")
            print(f"Message: {data.get('Message')}")
            
            if data.get("Data"):
                candles = data["Data"].get("Data", [])
                print(f"\nTotal candles: {len(candles)}")
                
                if candles:
                    print(f"\nFirst candle: {candles[0]}")
                    print(f"Last candle: {candles[-1]}")
                    
                    # Count non-zero prices
                    non_zero = sum(1 for c in candles if c['close'] > 0)
                    print(f"\nNon-zero prices: {non_zero}/{len(candles)}")
                    
                    # Show some with prices
                    with_prices = [c for c in candles if c['close'] > 0]
                    if with_prices:
                        print(f"\nSample with prices:")
                        for c in with_prices[:3]:
                            ts = datetime.fromtimestamp(c['time'], tz=timezone.utc)
                            print(f"  {ts}: ${c['close']} (vol: {c['volumefrom']})")

asyncio.run(test_cryptocompare())
