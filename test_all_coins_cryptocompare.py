import asyncio
import aiohttp

async def test_coin(coin_symbol, start_ts, end_ts, period_name):
    api_key = "bd25d756776bfbf97826408037aac385d673c03b5ca954be21565565e4b8d05f"
    
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        "fsym": coin_symbol,
        "tsym": "USD",
        "limit": 168,
        "toTs": end_ts
    }
    
    headers = {"authorization": f"Apikey {api_key}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            data = await response.json()
            
            if data.get("Response") == "Error":
                print(f"❌ {coin_symbol} ({period_name}): {data.get('Message')}")
                return
            
            candles = data.get("Data", {}).get("Data", [])
            non_zero = sum(1 for c in candles if c['close'] > 0)
            
            if non_zero > 0:
                print(f"✅ {coin_symbol} ({period_name}): {non_zero}/{len(candles)} data points")
            else:
                print(f"⚠️  {coin_symbol} ({period_name}): {len(candles)} candles but all zeros")

async def main():
    print("Testing CryptoCompare data availability:\n")
    
    # USDD crash: June 12-18, 2022
    await test_coin("USDD", 1654992000, 1655596800, "crash Jun 2022")
    
    # USDN crash: April 3-9, 2022  
    await test_coin("USDN", 1648944000, 1649548800, "crash Apr 2022")
    
    # BAC crash: Jan 10-16, 2021
    await test_coin("BAC", 1610236800, 1610841600, "crash Jan 2021")
    
    # Try recent for comparison
    await test_coin("USDD", 1707264000, 1707868800, "recent Feb 2026")
    await test_coin("LUNA", 1651881600, 1652486400, "crash May 2022")
    await test_coin("BTC", 1654992000, 1655596800, "test Jun 2022")

asyncio.run(main())
