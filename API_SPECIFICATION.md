# 🔌 API SPECIFICATION - ATLAS RISK INTELLIGENCE

**Version:** 1.0  
**Date:** 2026-02-14  
**Base URL:** `https://api.atlas.example.com/v1`

---

## 📋 OVERVIEW

This document specifies the backend APIs required to support the ATLAS Flutter web frontend. The frontend currently uses **mock data** and needs these endpoints to be implemented for production.

### Authentication
All API requests should include:
```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

### Response Format
All responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-02-14T12:50:53Z",
  "meta": {
    "version": "1.0",
    "requestId": "uuid"
  }
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

---

## 🎯 CORE ENDPOINTS

### 1. Get Current Risk State
**Purpose:** Fetch the complete current risk state for a stablecoin

**Endpoint:** `GET /risk/current`

**Query Parameters:**
```
coin: string (required) - Stablecoin symbol (e.g., "USDC", "USDT", "DAI")
chain: string (optional) - Blockchain (default: "ethereum")
```

**Response:**
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
    "lastUpdated": "2026-02-14T12:50:00Z",
    "stressBreakdown": {
      "Peg Stress": {
        "value": 35.2,
        "rollingMean": 32.8,
        "contributionPercent": 0.28,
        "trend": "rising",
        "history": [30.1, 31.5, 32.8, 34.2, 35.2],
        "description": "Measures deviation from $1.00 peg across major DEXs and CEXs"
      },
      "Liquidity Stress": {
        "value": 42.1,
        "rollingMean": 40.5,
        "contributionPercent": 0.32,
        "trend": "stable",
        "history": [38.5, 39.2, 40.5, 41.8, 42.1],
        "description": "Tracks available liquidity depth and slippage on major trading venues"
      },
      "Supply Stress": {
        "value": 28.5,
        "rollingMean": 29.1,
        "contributionPercent": 0.22,
        "trend": "falling",
        "history": [32.1, 30.8, 29.1, 28.9, 28.5],
        "description": "Monitors supply expansion/contraction rates and reserve ratios"
      },
      "Market Stress": {
        "value": 38.7,
        "rollingMean": 37.2,
        "contributionPercent": 0.18,
        "trend": "rising",
        "history": [35.2, 36.1, 37.2, 38.1, 38.7],
        "description": "Aggregates broader market conditions affecting stablecoin stability"
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
      },
      {
        "chain": "Polygon",
        "confirmations": 128,
        "tier": "Tier 2",
        "finalized": true,
        "lastReorg": "2026-02-14T11:15:00Z",
        "confidence": 0.95
      },
      {
        "chain": "Arbitrum",
        "confirmations": 32,
        "tier": "Tier 3",
        "finalized": false,
        "lastReorg": "2026-02-14T12:00:00Z",
        "confidence": 0.85
      }
    ]
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

**Used By:**
- Command Center page
- Stress Analysis page
- Confidence & Finality page

**Update Frequency:** Real-time (WebSocket) or polling every 5 seconds

---

### 2. Get Risk History
**Purpose:** Fetch historical risk snapshots for timeline visualization

**Endpoint:** `GET /risk/history`

**Query Parameters:**
```
coin: string (required)
chain: string (optional)
from: ISO8601 timestamp (required)
to: ISO8601 timestamp (required)
interval: string (optional) - "1m", "5m", "15m", "1h" (default: "5m")
```

**Response:**
```json
{
  "success": true,
  "data": {
    "snapshots": [
      {
        "timestamp": "2026-02-14T12:00:00Z",
        "riskScore": 42,
        "confidence": 0.91,
        "event": null
      },
      {
        "timestamp": "2026-02-14T12:05:00Z",
        "riskScore": 43,
        "confidence": 0.92,
        "event": "Large transfer detected"
      },
      {
        "timestamp": "2026-02-14T12:10:00Z",
        "riskScore": 45,
        "confidence": 0.92,
        "event": null
      }
    ],
    "totalCount": 144,
    "interval": "5m"
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

**Used By:**
- Command Center page (Risk Timeline chart)

**Update Frequency:** Fetch on page load, then real-time updates

---

### 3. Get On-Chain Alerts
**Purpose:** Fetch logged risk alerts that were attested on-chain

**Endpoint:** `GET /alerts`

**Query Parameters:**
```
coin: string (optional) - Filter by stablecoin
chain: string (optional) - Filter by blockchain
tier: string (optional) - "T1", "T2", "T3"
minRisk: number (optional) - Minimum risk score (0-100)
from: ISO8601 timestamp (optional)
to: ISO8601 timestamp (optional)
limit: number (optional, default: 50)
offset: number (optional, default: 0)
```

**Response:**
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
        },
        "windowState": "FINAL",
        "tcs": 0.95
      },
      {
        "id": "alert_def456",
        "coin": "USDT",
        "chain": "ethereum",
        "risk": 45,
        "confidence": 0.88,
        "timestamp": "2026-02-14T07:15:00Z",
        "txHash": "0x2b1c...4f7a",
        "tier": "T2",
        "blockNumber": 19234123,
        "stressSnapshot": {
          "pegStress": 35.2,
          "liquidityStress": 48.9,
          "supplyStress": 52.3,
          "marketStress": 41.7
        },
        "windowState": "PROVISIONAL",
        "tcs": 0.88
      }
    ],
    "totalCount": 247,
    "hasMore": true
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

**Used By:**
- On-Chain Alerts page

**Update Frequency:** Fetch on page load, then real-time updates for new alerts

---

### 4. Get Alert Detail
**Purpose:** Fetch detailed information about a specific alert

**Endpoint:** `GET /alerts/{alertId}`

**Path Parameters:**
```
alertId: string (required)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "alert_abc123",
    "coin": "USDC",
    "chain": "ethereum",
    "risk": 85,
    "confidence": 0.95,
    "timestamp": "2026-02-14T10:30:00Z",
    "txHash": "0x7a3f...9e2d",
    "tier": "T3",
    "blockNumber": 19234567,
    "explorerUrl": "https://etherscan.io/tx/0x7a3f...9e2d",
    "windowState": "FINAL",
    "tcs": 0.95,
    "stressSnapshot": {
      "pegStress": 78.5,
      "liquidityStress": 65.2,
      "supplyStress": 42.1,
      "marketStress": 55.8
    },
    "chainFinality": [
      {
        "chain": "Ethereum",
        "confirmations": 64,
        "finalized": true,
        "confidence": 0.98
      }
    ],
    "rawData": {
      "pegDeviation": 0.0235,
      "liquidityDepth": 12500000,
      "supplyChange24h": -0.0012,
      "marketVolatility": 0.0156
    }
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

**Used By:**
- On-Chain Alerts page (detail modal)

---

## 🔄 REAL-TIME ENDPOINTS

### 5. WebSocket: Live Risk Updates
**Purpose:** Stream real-time risk updates to the frontend

**Endpoint:** `WSS /ws/risk`

**Connection:**
```javascript
const ws = new WebSocket('wss://api.atlas.example.com/v1/ws/risk?coin=USDC&chain=ethereum');
```

**Message Format (Server → Client):**
```json
{
  "type": "risk_update",
  "data": {
    "riskScore": 46,
    "riskLevel": "ELEVATED",
    "tcs": 0.91,
    "timestamp": "2026-02-14T12:51:00Z",
    "changes": {
      "riskScore": +1,
      "pegStress": +0.5
    }
  }
}
```

**Message Types:**
- `risk_update` - Risk score changed
- `alert_created` - New alert logged on-chain
- `window_state_change` - Window state machine transition
- `finality_update` - Chain finality status changed

**Used By:**
- All pages (for live updates)

---

## 🎛️ CONFIGURATION ENDPOINTS

### 6. Get Available Coins
**Purpose:** List all supported stablecoins

**Endpoint:** `GET /config/coins`

**Response:**
```json
{
  "success": true,
  "data": {
    "coins": [
      {
        "symbol": "USDC",
        "name": "USD Coin",
        "icon": "https://cdn.atlas.example.com/icons/usdc.png",
        "chains": ["ethereum", "polygon", "arbitrum", "optimism"]
      },
      {
        "symbol": "USDT",
        "name": "Tether",
        "icon": "https://cdn.atlas.example.com/icons/usdt.png",
        "chains": ["ethereum", "polygon", "tron"]
      },
      {
        "symbol": "DAI",
        "name": "Dai",
        "icon": "https://cdn.atlas.example.com/icons/dai.png",
        "chains": ["ethereum", "polygon"]
      }
    ]
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

**Used By:**
- Top bar (coin selector)

---

### 7. Get Available Chains
**Purpose:** List all supported blockchains

**Endpoint:** `GET /config/chains`

**Response:**
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
  },
  "timestamp": "2026-02-14T12:50:53Z"
}
```

**Used By:**
- Top bar (chain selector)

---

## 📊 DATA MODELS

### RiskState
```typescript
interface RiskState {
  riskScore: number;           // 0-100
  riskLevel: string;           // "SAFE" | "ELEVATED" | "CRITICAL"
  tcs: number;                 // 0-1 (Temporal Confidence Score)
  windowState: string;         // "OPEN" | "PROVISIONAL" | "FINAL"
  finalityWeight: number;      // 0-1
  crossChainConfidence: number; // 0-1
  completeness: number;        // 0-1
  stalenessPenalty: number;    // 0-1
  lastUpdated: string;         // ISO8601
  stressBreakdown: Record<string, StressFactor>;
  chainFinalityList: ChainFinality[];
}
```

### StressFactor
```typescript
interface StressFactor {
  value: number;               // 0-100
  rollingMean: number;         // 0-100
  contributionPercent: number; // 0-1
  trend: string;               // "rising" | "falling" | "stable"
  history: number[];           // Last N values
  description: string;
}
```

### RiskSnapshot
```typescript
interface RiskSnapshot {
  timestamp: string;           // ISO8601
  riskScore: number;           // 0-100
  confidence: number;          // 0-1
  event: string | null;        // Optional event description
}
```

### ChainFinality
```typescript
interface ChainFinality {
  chain: string;
  confirmations: number;
  tier: string;                // "Tier 1" | "Tier 2" | "Tier 3"
  finalized: boolean;
  lastReorg: string;           // ISO8601
  confidence: number;          // 0-1
}
```

### Alert
```typescript
interface Alert {
  id: string;
  coin: string;
  chain: string;
  risk: number;                // 0-100
  confidence: number;          // 0-1
  timestamp: string;           // ISO8601
  txHash: string;
  tier: string;                // "T1" | "T2" | "T3"
  blockNumber: number;
  stressSnapshot: {
    pegStress: number;
    liquidityStress: number;
    supplyStress: number;
    marketStress: number;
  };
  windowState: string;
  tcs: number;
}
```

---

## 🔐 SECURITY REQUIREMENTS

### Rate Limiting
```
GET endpoints: 100 requests/minute per IP
WebSocket: 1 connection per user
```

### CORS
```
Allow-Origin: https://atlas.example.com
Allow-Methods: GET, POST, OPTIONS
Allow-Headers: Authorization, Content-Type, X-API-Key
```

### Data Validation
- All timestamps must be ISO8601 format
- All numeric values must be validated (0-100 for risk, 0-1 for confidence)
- Coin symbols must be uppercase
- Chain IDs must be lowercase

---

## 📈 PERFORMANCE REQUIREMENTS

### Response Times
- GET /risk/current: < 200ms
- GET /risk/history: < 500ms
- GET /alerts: < 300ms
- WebSocket latency: < 100ms

### Caching
- Risk state: Cache for 5 seconds
- Config endpoints: Cache for 1 hour
- Alert history: Cache for 1 minute

---

## 🧪 TESTING ENDPOINTS

### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0",
  "uptime": 3600,
  "timestamp": "2026-02-14T12:50:53Z"
}
```

### Mock Data Toggle
```
GET /debug/mock?enabled=true

Response:
{
  "success": true,
  "message": "Mock data enabled"
}
```

---

## 📝 IMPLEMENTATION PRIORITY

### Phase 1 (Critical - Week 1)
1. ✅ GET /risk/current
2. ✅ GET /risk/history
3. ✅ GET /config/coins
4. ✅ GET /config/chains

### Phase 2 (Important - Week 2)
5. ✅ GET /alerts
6. ✅ GET /alerts/{alertId}
7. ✅ WebSocket /ws/risk

### Phase 3 (Nice-to-have - Week 3)
8. ⏳ Advanced filtering
9. ⏳ Historical replay endpoints
10. ⏳ System status endpoints

---

## 🔗 INTEGRATION EXAMPLE

```dart
// Example: Fetching current risk state
class RiskApiClient {
  final String baseUrl = 'https://api.atlas.example.com/v1';
  
  Future<RiskState> getCurrentRisk(String coin, String chain) async {
    final response = await http.get(
      Uri.parse('$baseUrl/risk/current?coin=$coin&chain=$chain'),
      headers: {
        'Authorization': 'Bearer $token',
        'X-API-Key': apiKey,
      },
    );
    
    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return RiskState.fromJson(json['data']);
    } else {
      throw ApiException('Failed to fetch risk state');
    }
  }
}
```

---

**Status:** 📋 SPECIFICATION COMPLETE  
**Next Step:** Backend implementation  
**Contact:** API team for questions
