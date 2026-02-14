# 🚀 API QUICK REFERENCE - CURL EXAMPLES

**Base URL:** `https://api.atlas.example.com/v1`  
**Replace with your actual backend URL**

---

## 📋 QUICK TEST COMMANDS

### 1. Get Current Risk State
```bash
curl -X GET "https://api.atlas.example.com/v1/risk/current?coin=USDC&chain=ethereum" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "riskScore": 45,
    "riskLevel": "ELEVATED",
    "tcs": 0.92,
    "windowState": "FINAL",
    "finalityWeight": 0.95,
    "crossChainConfidence": 0.88,
    "completeness": 0.97,
    "stalenessPenalty": 0.02,
    "stressBreakdown": {
      "Peg Stress": {
        "value": 35.2,
        "rollingMean": 32.8,
        "contributionPercent": 0.28,
        "trend": "rising",
        "history": [30.1, 31.5, 32.8, 34.2, 35.2],
        "description": "Measures deviation from $1.00 peg"
      },
      "Liquidity Stress": {
        "value": 42.1,
        "rollingMean": 40.5,
        "contributionPercent": 0.32,
        "trend": "stable",
        "history": [38.5, 39.2, 40.5, 41.8, 42.1],
        "description": "Tracks liquidity depth"
      },
      "Supply Stress": {
        "value": 28.5,
        "rollingMean": 29.1,
        "contributionPercent": 0.22,
        "trend": "falling",
        "history": [32.1, 30.8, 29.1, 28.9, 28.5],
        "description": "Monitors supply changes"
      },
      "Market Stress": {
        "value": 38.7,
        "rollingMean": 37.2,
        "contributionPercent": 0.18,
        "trend": "rising",
        "history": [35.2, 36.1, 37.2, 38.1, 38.7],
        "description": "Market conditions"
      }
    },
    "chainFinalityList": [
      {
        "chain": "Ethereum",
        "confirmations": 64,
        "tier": "Tier 1",
        "finalized": true,
        "lastReorg": "2026-02-14T10:30:00Z",
        "confidence": 0.98
      }
    ]
  }
}
```

---

### 2. Get Risk History
```bash
curl -X GET "https://api.atlas.example.com/v1/risk/history?coin=USDC&chain=ethereum&from=2026-02-14T00:00:00Z&to=2026-02-14T12:00:00Z&interval=5m" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "snapshots": [
      {
        "timestamp": "2026-02-14T00:00:00Z",
        "riskScore": 38,
        "confidence": 0.89,
        "event": null
      },
      {
        "timestamp": "2026-02-14T00:05:00Z",
        "riskScore": 39,
        "confidence": 0.90,
        "event": null
      },
      {
        "timestamp": "2026-02-14T00:10:00Z",
        "riskScore": 42,
        "confidence": 0.91,
        "event": "Large transfer detected"
      }
    ],
    "totalCount": 144
  }
}
```

---

### 3. Get On-Chain Alerts
```bash
curl -X GET "https://api.atlas.example.com/v1/alerts?coin=USDC&minRisk=80&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "alert_abc123",
        "coin": "USDC",
        "chain": "ethereum",
        "risk": 85,
        "confidence": 0.95,
        "timestamp": "2026-02-14T10:30:00Z",
        "txHash": "0x7a3f...9e2d",
        "tier": "T3",
        "blockNumber": 19234567,
        "stressSnapshot": {
          "pegStress": 78.5,
          "liquidityStress": 65.2,
          "supplyStress": 42.1,
          "marketStress": 55.8
        }
      }
    ],
    "totalCount": 5,
    "hasMore": false
  }
}
```

---

### 4. Get Alert Detail
```bash
curl -X GET "https://api.atlas.example.com/v1/alerts/alert_abc123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "id": "alert_abc123",
    "coin": "USDC",
    "risk": 85,
    "confidence": 0.95,
    "timestamp": "2026-02-14T10:30:00Z",
    "txHash": "0x7a3f...9e2d",
    "explorerUrl": "https://etherscan.io/tx/0x7a3f...9e2d",
    "stressSnapshot": {
      "pegStress": 78.5,
      "liquidityStress": 65.2,
      "supplyStress": 42.1,
      "marketStress": 55.8
    }
  }
}
```

---

### 5. Get Available Coins
```bash
curl -X GET "https://api.atlas.example.com/v1/config/coins" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "coins": [
      {
        "symbol": "USDC",
        "name": "USD Coin",
        "icon": "https://cdn.atlas.example.com/icons/usdc.png",
        "chains": ["ethereum", "polygon", "arbitrum"]
      },
      {
        "symbol": "USDT",
        "name": "Tether",
        "icon": "https://cdn.atlas.example.com/icons/usdt.png",
        "chains": ["ethereum", "polygon"]
      },
      {
        "symbol": "DAI",
        "name": "Dai",
        "icon": "https://cdn.atlas.example.com/icons/dai.png",
        "chains": ["ethereum"]
      }
    ]
  }
}
```

---

### 6. Get Available Chains
```bash
curl -X GET "https://api.atlas.example.com/v1/config/chains" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "chains": [
      {
        "id": "ethereum",
        "name": "Ethereum",
        "icon": "https://cdn.atlas.example.com/icons/ethereum.png",
        "explorerUrl": "https://etherscan.io"
      },
      {
        "id": "polygon",
        "name": "Polygon",
        "icon": "https://cdn.atlas.example.com/icons/polygon.png",
        "explorerUrl": "https://polygonscan.com"
      }
    ]
  }
}
```

---

## 🔌 POSTMAN COLLECTION

### Import this JSON into Postman:

```json
{
  "info": {
    "name": "ATLAS Risk Intelligence API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Current Risk",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          },
          {
            "key": "X-API-Key",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/risk/current?coin=USDC&chain=ethereum",
          "host": ["{{baseUrl}}"],
          "path": ["risk", "current"],
          "query": [
            {"key": "coin", "value": "USDC"},
            {"key": "chain", "value": "ethereum"}
          ]
        }
      }
    },
    {
      "name": "Get Risk History",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          },
          {
            "key": "X-API-Key",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/risk/history?coin=USDC&from=2026-02-14T00:00:00Z&to=2026-02-14T12:00:00Z&interval=5m",
          "host": ["{{baseUrl}}"],
          "path": ["risk", "history"],
          "query": [
            {"key": "coin", "value": "USDC"},
            {"key": "from", "value": "2026-02-14T00:00:00Z"},
            {"key": "to", "value": "2026-02-14T12:00:00Z"},
            {"key": "interval", "value": "5m"}
          ]
        }
      }
    },
    {
      "name": "Get Alerts",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          },
          {
            "key": "X-API-Key",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/alerts?coin=USDC&minRisk=80&limit=10",
          "host": ["{{baseUrl}}"],
          "path": ["alerts"],
          "query": [
            {"key": "coin", "value": "USDC"},
            {"key": "minRisk", "value": "80"},
            {"key": "limit", "value": "10"}
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://api.atlas.example.com/v1"
    },
    {
      "key": "token",
      "value": "YOUR_JWT_TOKEN"
    },
    {
      "key": "apiKey",
      "value": "YOUR_API_KEY"
    }
  ]
}
```

---

## 🧪 MOCK SERVER URLs (For Testing)

If you want to test the frontend before backend is ready, use these mock endpoints:

### Option 1: JSON Placeholder (Free)
```bash
# Mock current risk
curl https://jsonplaceholder.typicode.com/posts/1

# Mock alerts
curl https://jsonplaceholder.typicode.com/posts
```

### Option 2: Mocky.io (Custom Responses)
Create custom mock responses at: https://designer.mocky.io/

Example mock URL:
```
https://run.mocky.io/v3/YOUR_MOCK_ID
```

---

## 📝 ENVIRONMENT VARIABLES

Create a `.env` file:
```bash
API_BASE_URL=https://api.atlas.example.com/v1
API_KEY=your_api_key_here
JWT_TOKEN=your_jwt_token_here
WS_URL=wss://api.atlas.example.com/v1/ws
```

---

## 🔗 INTEGRATION IN FLUTTER

Update your API client:

```dart
// lib/data/api/api_client.dart
class ApiClient {
  static const String baseUrl = 'https://api.atlas.example.com/v1';
  static const String apiKey = 'YOUR_API_KEY';
  
  Future<RiskState> getCurrentRisk(String coin, String chain) async {
    final url = '$baseUrl/risk/current?coin=$coin&chain=$chain';
    
    final response = await http.get(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'X-API-Key': apiKey,
      },
    );
    
    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return RiskState.fromJson(json['data']);
    } else {
      throw Exception('Failed to load risk data');
    }
  }
}
```

---

## ✅ CHECKLIST FOR BACKEND TEAM

- [ ] Deploy API to production URL
- [ ] Provide API key and JWT token
- [ ] Enable CORS for frontend domain
- [ ] Set up rate limiting (100 req/min)
- [ ] Configure WebSocket endpoint
- [ ] Test all endpoints with sample data
- [ ] Provide Postman collection
- [ ] Document authentication flow

---

**Quick Start:** Replace `https://api.atlas.example.com/v1` with your actual backend URL and test with curl!
