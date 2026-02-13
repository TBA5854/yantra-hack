#!/bin/bash

# Test if Binance has historical klines for these coins during their crash periods

echo "Testing Binance historical klines availability..."
echo ""

# USDD crash: June 12-18, 2022
# Unix timestamp: 1655020800000 (June 12, 2022 00:00:00)
echo "1. USDD (June 12, 2022):"
curl -s "https://api.binance.com/api/v3/klines?symbol=USDDUSDT&interval=5m&startTime=1655020800000&limit=1" | jq -r 'if . | type == "array" then "✅ Has data: \(.[0][0] | tonumber / 1000 | strftime("%Y-%m-%d %H:%M")) - $\(.[0][4])" else "❌ Error: \(.msg)" end'

# Try USDDBUSD
echo "   Trying USDDBUSD:"
curl -s "https://api.binance.com/api/v3/klines?symbol=USDDBUSD&interval=5m&startTime=1655020800000&limit=1" | jq -r 'if . | type == "array" then "✅ Has data: \(.[0][0] | tonumber / 1000 | strftime("%Y-%m-%d %H:%M")) - $\(.[0][4])" else "❌ Error: \(.msg)" end'

echo ""

# USDN crash: April 3-9, 2022
# Unix timestamp: 1648944000000 (April 3, 2022 00:00:00)
echo "2. USDN (April 3, 2022):"
curl -s "https://api.binance.com/api/v3/klines?symbol=USDNUSDT&interval=5m&startTime=1648944000000&limit=1" | jq -r 'if . | type == "array" then "✅ Has data: \(.[0][0] | tonumber / 1000 | strftime("%Y-%m-%d %H:%M")) - $\(.[0][4])" else "❌ Error: \(.msg)" end'

echo ""

# BAC crash: January 10-16, 2021
# Unix timestamp: 1610236800000 (January 10, 2021 00:00:00)
echo "3. BAC (January 10, 2021):"
curl -s "https://api.binance.com/api/v3/klines?symbol=BACUSDT&interval=5m&startTime=1610236800000&limit=1" | jq -r 'if . | type == "array" then "✅ Has data: \(.[0][0] | tonumber / 1000 | strftime("%Y-%m-%d %H:%M")) - $\(.[0][4])" else "❌ Error: \(.msg)" end'

echo ""

# Check what USDD pairs exist
echo "4. Available USDD pairs on Binance:"
curl -s "https://api.binance.com/api/v3/exchangeInfo" | jq -r '.symbols[] | select(.symbol | contains("USDD")) | .symbol' | head -10

