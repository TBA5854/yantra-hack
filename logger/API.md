# API Documentation

## Base URL
```
http://localhost:8080
```

## Endpoints

### 1. Health Check
Check API and dependencies health status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "database": true,
  "solana_rpc": true,
  "version": "0.1.0"
}
```

---

### 2. Create Log Entry
Submit a new log entry to the system.

**Endpoint:** `POST /api/v1/logs`

**Request Body:**
```json
{
  "event_type": "user_login",
  "severity": "info",
  "data": {
    "user_id": "12345",
    "ip": "192.168.1.1",
    "timestamp": "2026-02-14T14:20:00Z",
    "any_custom_field": "value"
  }
}
```

**Parameters:**
- `event_type` (string, required): Type of event (e.g., "user_login", "system_error", "payment")
- `severity` (string, required): Severity level ("info", "warning", "error", "critical")
- `data` (object, required): Arbitrary JSON object with log details

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
  "tx_signature": "5J8g...",
  "blockchain_status": "pending",
  "created_at": "2026-02-14T14:20:00Z"
}
```

**Status Codes:**
- `201 Created`: Log entry created successfully
- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Database or system error

---

### 3. Get Log by ID
Retrieve a specific log entry by its UUID.

**Endpoint:** `GET /api/v1/logs/{id}`

**Parameters:**
- `id` (path, UUID): Log entry ID

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "user_login",
  "severity": "info",
  "data": {
    "user_id": "12345",
    "ip": "192.168.1.1"
  },
  "hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
  "tx_signature": "5J8g...",
  "blockchain_status": "confirmed",
  "created_at": "2026-02-14T14:20:00Z",
  "updated_at": "2026-02-14T14:20:05Z"
}
```

**Status Codes:**
- `200 OK`: Log entry found
- `404 Not Found`: Log entry not found
- `400 Bad Request`: Invalid ID format

---

### 4. Query Logs
Search and filter log entries with pagination.

**Endpoint:** `GET /api/v1/logs`

**Query Parameters:**
- `event_type` (string, optional): Filter by event type
- `severity` (string, optional): Filter by severity
- `limit` (integer, optional): Number of results (default: 100, max: 1000)
- `offset` (integer, optional): Pagination offset (default: 0)
- `from_date` (ISO 8601, optional): Filter logs from this date
- `to_date` (ISO 8601, optional): Filter logs until this date

**Example:**
```bash
GET /api/v1/logs?event_type=user_login&severity=info&limit=50&offset=0
```

**Response:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "event_type": "user_login",
      "severity": "info",
      "data": { "user_id": "12345" },
      "hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
      "tx_signature": "5J8g...",
      "blockchain_status": "confirmed",
      "created_at": "2026-02-14T14:20:00Z",
      "updated_at": "2026-02-14T14:20:05Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

### 5. Verify Log Entry
Verify log integrity against blockchain.

**Endpoint:** `GET /api/v1/logs/{id}/verify`

**Parameters:**
- `id` (path, UUID): Log entry ID

**Response:**
```json
{
  "log_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_valid": true,
  "local_hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
  "blockchain_hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
  "tx_signature": "5J8g...",
  "blockchain_status": "confirmed",
  "message": "Log verified successfully"
}
```

**Verification Results:**
- `is_valid: true`: Hash matches blockchain
- `is_valid: false`: Hash mismatch or not yet on blockchain

**Status Codes:**
- `200 OK`: Verification completed
- `404 Not Found`: Log entry not found

---

### 6. Get Statistics
Get system statistics and blockchain info.

**Endpoint:** `GET /api/v1/stats`

**Response:**
```json
{
  "total_logs": 1500,
  "pending_logs": 5,
  "confirmed_logs": 1490,
  "failed_logs": 5,
  "wallet_pubkey": "5J8g2wKXQBbFnB...",
  "wallet_balance_lamports": 100000000
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message"
}
```

**Common Error Codes:**
- `validation_error`: Request validation failed
- `database_error`: Database operation failed
- `blockchain_error`: Blockchain operation failed
- `not_found`: Resource not found
- `invalid_id`: Invalid UUID format

---

## Rate Limiting

- Default: 100 requests per minute per IP
- Configurable via environment variables

---

## Authentication

Optional API key authentication can be enabled:

```bash
Authorization: Bearer <api_key>
```

Configure in `.env`:
```
API_KEY=your-secret-key
```

---

## Examples

### cURL Examples

**Create log:**
```bash
curl -X POST http://localhost:8080/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_registration",
    "severity": "info",
    "data": {
      "user_id": "new_user_123",
      "email": "user@example.com",
      "source": "web_app"
    }
  }'
```

**Query logs:**
```bash
curl "http://localhost:8080/api/v1/logs?event_type=user_login&limit=10"
```

**Verify log:**
```bash
curl "http://localhost:8080/api/v1/logs/550e8400-e29b-41d4-a716-446655440000/verify"
```

### JavaScript Example

```javascript
// Create log
const response = await fetch('http://localhost:8080/api/v1/logs', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_type: 'api_call',
    severity: 'info',
    data: {
      endpoint: '/api/users',
      method: 'GET',
      response_time_ms: 45
    }
  })
});

const log = await response.json();
console.log('Log created:', log);

// Verify log
const verifyResponse = await fetch(
  `http://localhost:8080/api/v1/logs/${log.id}/verify`
);
const verification = await verifyResponse.json();
console.log('Verification:', verification);
```

### Python Example

```python
import requests

# Create log
response = requests.post(
    'http://localhost:8080/api/v1/logs',
    json={
        'event_type': 'data_processing',
        'severity': 'info',
        'data': {
            'records_processed': 1000,
            'duration_seconds': 12.5,
            'status': 'success'
        }
    }
)

log = response.json()
print(f"Log created: {log['id']}")

# Query logs
response = requests.get(
    'http://localhost:8080/api/v1/logs',
    params={
        'event_type': 'data_processing',
        'limit': 10
    }
)

logs = response.json()
print(f"Found {logs['total']} logs")
```
