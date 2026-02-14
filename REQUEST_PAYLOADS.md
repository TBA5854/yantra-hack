# 📤 REQUEST PAYLOADS - What Frontend Sends

This document shows the **exact JSON the frontend will send** for each API request.

---

## 🔍 GET REQUESTS (Query Parameters Only)

### 1. GET /risk/current
**No request body** - All data in URL query parameters

**URL:**
```
GET /risk/current?coin=USDC&chain=ethereum
```

**Query Parameters:**
```json
{
  "coin": "USDC",
  "chain": "ethereum"
}
```

---

### 2. GET /risk/history
**No request body** - All data in URL query parameters

**URL:**
```
GET /risk/history?coin=USDC&chain=ethereum&from=2026-02-14T00:00:00Z&to=2026-02-14T12:00:00Z&interval=5m
```

**Query Parameters:**
```json
{
  "coin": "USDC",
  "chain": "ethereum",
  "from": "2026-02-14T00:00:00Z",
  "to": "2026-02-14T12:00:00Z",
  "interval": "5m"
}
```

---

### 3. GET /alerts
**No request body** - All data in URL query parameters

**URL:**
```
GET /alerts?coin=USDC&tier=T3&minRisk=80&limit=50&offset=0
```

**Query Parameters:**
```json
{
  "coin": "USDC",
  "tier": "T3",
  "minRisk": 80,
  "limit": 50,
  "offset": 0
}
```

---

### 4. GET /alerts/{alertId}
**No request body** - Alert ID in URL path

**URL:**
```
GET /alerts/alert_abc123
```

---

### 5. GET /config/coins
**No request body** - No parameters needed

**URL:**
```
GET /config/coins
```

---

### 6. GET /config/chains
**No request body** - No parameters needed

**URL:**
```
GET /config/chains
```

---

## 📨 POST REQUESTS (If Needed in Future)

Currently, the frontend is **read-only** and doesn't send POST requests. But if you add features like:

### 7. POST /alerts/acknowledge (Future Feature)
**Request Body:**
```json
{
  "alertId": "alert_abc123",
  "acknowledgedBy": "user@example.com",
  "timestamp": "2026-02-14T12:55:00Z",
  "notes": "Investigated - false positive"
}
```

---

### 8. POST /risk/subscribe (Future Feature)
**Request Body:**
```json
{
  "coin": "USDC",
  "chain": "ethereum",
  "webhookUrl": "https://your-server.com/webhook",
  "thresholds": {
    "riskScore": 80,
    "tcsBelow": 0.6
  }
}
```

---

## 🔌 WEBSOCKET MESSAGES

### Client → Server (Subscribe to Updates)
```json
{
  "type": "subscribe",
  "data": {
    "coin": "USDC",
    "chain": "ethereum"
  }
}
```

### Client → Server (Unsubscribe)
```json
{
  "type": "unsubscribe",
  "data": {
    "coin": "USDC",
    "chain": "ethereum"
  }
}
```

### Client → Server (Ping)
```json
{
  "type": "ping",
  "timestamp": "2026-02-14T12:55:00Z"
}
```

---

## 📋 SUMMARY: What Frontend Sends

### Current Implementation (Read-Only)
**All requests are GET** - No JSON bodies sent, only URL query parameters:

| Endpoint | Method | Body | Query Params |
|----------|--------|------|--------------|
| /risk/current | GET | ❌ None | ✅ coin, chain |
| /risk/history | GET | ❌ None | ✅ coin, chain, from, to, interval |
| /alerts | GET | ❌ None | ✅ coin, tier, minRisk, limit, offset |
| /alerts/{id} | GET | ❌ None | ❌ None (ID in URL) |
| /config/coins | GET | ❌ None | ❌ None |
| /config/chains | GET | ❌ None | ❌ None |

### WebSocket
**Sends JSON messages** for subscribe/unsubscribe/ping

---

## 🔧 BACKEND EXPECTATIONS

### What Backend Should Expect:

1. **GET requests only** (no POST/PUT/DELETE currently)
2. **Query parameters** in URL (not request body)
3. **Headers:**
   ```
   Authorization: Bearer <jwt_token>
   X-API-Key: <api_key>
   Content-Type: application/json
   ```

### Example Request Headers:
```http
GET /risk/current?coin=USDC&chain=ethereum HTTP/1.1
Host: api.atlas.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-API-Key: atlas_api_key_123456789
Content-Type: application/json
Accept: application/json
User-Agent: Atlas-Flutter-Web/1.0
```

---

## ✅ VALIDATION RULES

Backend should validate:

### Query Parameters
```typescript
// coin
- Required: Yes
- Type: string
- Allowed: "USDC", "USDT", "DAI"
- Case: Uppercase

// chain
- Required: No (default: "ethereum")
- Type: string
- Allowed: "ethereum", "polygon", "arbitrum"
- Case: Lowercase

// from/to (timestamps)
- Required: Yes (for /risk/history)
- Type: ISO8601 string
- Format: "2026-02-14T12:55:00Z"
- Validation: from < to

// interval
- Required: No (default: "5m")
- Type: string
- Allowed: "1m", "5m", "15m", "1h"

// minRisk
- Required: No
- Type: number
- Range: 0-100

// tier
- Required: No
- Type: string
- Allowed: "T1", "T2", "T3"

// limit
- Required: No (default: 50)
- Type: number
- Range: 1-100

// offset
- Required: No (default: 0)
- Type: number
- Range: 0+
```

---

## 🚨 ERROR CASES

Frontend expects these error responses:

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid coin symbol",
    "details": {
      "parameter": "coin",
      "value": "INVALID",
      "allowed": ["USDC", "USDT", "DAI"]
    }
  },
  "timestamp": "2026-02-14T12:55:00Z"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  },
  "timestamp": "2026-02-14T12:55:00Z"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Alert not found",
    "details": {
      "alertId": "alert_invalid"
    }
  },
  "timestamp": "2026-02-14T12:55:00Z"
}
```

### 429 Rate Limit
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retryAfter": 45
    }
  },
  "timestamp": "2026-02-14T12:55:00Z"
}
```

### 500 Internal Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "requestId": "req_abc123"
    }
  },
  "timestamp": "2026-02-14T12:55:00Z"
}
```

---

## 📝 COMPLETE REQUEST EXAMPLES

### Example 1: Get Current Risk
```http
GET /risk/current?coin=USDC&chain=ethereum HTTP/1.1
Host: api.atlas.example.com
Authorization: Bearer eyJhbGc...
X-API-Key: atlas_key_123
```

**Frontend sends:** Nothing in body, only URL params

---

### Example 2: Get Alerts with Filters
```http
GET /alerts?coin=USDC&minRisk=80&tier=T3&limit=10&offset=0 HTTP/1.1
Host: api.atlas.example.com
Authorization: Bearer eyJhbGc...
X-API-Key: atlas_key_123
```

**Frontend sends:** Nothing in body, only URL params

---

### Example 3: WebSocket Subscribe
```javascript
// After WebSocket connection established
ws.send(JSON.stringify({
  "type": "subscribe",
  "data": {
    "coin": "USDC",
    "chain": "ethereum"
  }
}));
```

**Frontend sends:** JSON message over WebSocket

---

## 🎯 KEY TAKEAWAY

**The frontend currently sends NO request bodies** - everything is:
- ✅ URL query parameters (for GET requests)
- ✅ WebSocket JSON messages (for real-time)
- ❌ No POST/PUT/DELETE requests
- ❌ No JSON request bodies

Your backend should expect **query parameters only** for all current endpoints!
