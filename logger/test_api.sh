#!/bin/bash

# Solana Logger API Test Script

API_URL="http://localhost:8080"

echo "🧪 Testing Solana Logger API"
echo "================================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check"
curl -s "$API_URL/health" | jq .
echo ""
echo ""

# 2. Get Stats
echo "2️⃣ Statistics"
curl -s "$API_URL/api/v1/stats" | jq .
echo ""
echo ""

# 3. Create Log Entry - User Login
echo "3️⃣ Creating Log Entry: User Login"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/logs" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_login",
    "severity": "info",
    "data": {
      "user_id": "user_12345",
      "ip_address": "192.168.1.100",
      "timestamp": "2026-02-14T14:20:00Z",
      "browser": "Chrome/120.0",
      "success": true
    }
  }')
echo $LOGIN_RESPONSE | jq .
LOG_ID_1=$(echo $LOGIN_RESPONSE | jq -r '.id')
echo ""
echo ""

# 4. Create Log Entry - System Error
echo "4️⃣ Creating Log Entry: System Error"
ERROR_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/logs" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "system_error",
    "severity": "error",
    "data": {
      "error_code": "DB_CONNECTION_FAILED",
      "error_message": "Failed to connect to database",
      "stack_trace": "at main.rs:42",
      "timestamp": "2026-02-14T14:21:00Z"
    }
  }')
echo $ERROR_RESPONSE | jq .
LOG_ID_2=$(echo $ERROR_RESPONSE | jq -r '.id')
echo ""
echo ""

# 5. Create Log Entry - Payment Transaction
echo "5️⃣ Creating Log Entry: Payment Transaction"
PAYMENT_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/logs" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "payment_transaction",
    "severity": "critical",
    "data": {
      "transaction_id": "tx_987654321",
      "amount": 150.50,
      "currency": "USD",
      "from_account": "acc_123",
      "to_account": "acc_456",
      "status": "completed",
      "timestamp": "2026-02-14T14:22:00Z"
    }
  }')
echo $PAYMENT_RESPONSE | jq .
LOG_ID_3=$(echo $PAYMENT_RESPONSE | jq -r '.id')
echo ""
echo ""

# Wait for blockchain submission
echo "⏳ Waiting 3 seconds for blockchain submission..."
sleep 3
echo ""

# 6. Get Specific Log
echo "6️⃣ Retrieving Log Entry by ID"
curl -s "$API_URL/api/v1/logs/$LOG_ID_1" | jq .
echo ""
echo ""

# 7. Query Logs by Event Type
echo "7️⃣ Querying Logs by Event Type (user_login)"
curl -s "$API_URL/api/v1/logs?event_type=user_login&limit=10" | jq .
echo ""
echo ""

# 8. Query Logs by Severity
echo "8️⃣ Querying Logs by Severity (error)"
curl -s "$API_URL/api/v1/logs?severity=error&limit=10" | jq .
echo ""
echo ""

# 9. Query All Recent Logs
echo "9️⃣ Querying Recent Logs (limit 5)"
curl -s "$API_URL/api/v1/logs?limit=5" | jq .
echo ""
echo ""

# 10. Verify Log Entry
echo "🔐 Verifying Log Entry Against Blockchain"
curl -s "$API_URL/api/v1/logs/$LOG_ID_1/verify" | jq .
echo ""
echo ""

# 11. Final Stats
echo "📊 Final Statistics"
curl -s "$API_URL/api/v1/stats" | jq .
echo ""
echo ""

echo "✅ All tests completed!"
