# Quick Start Guide

## 🚀 5-Minute Quick Start

### Option 1: Local Development

1. **Prerequisites:**
   ```bash
   # Rust (if not installed)
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # PostgreSQL
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Run automated setup:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start the server:**
   ```bash
   cd api
   cargo run --release
   ```

4. **Test it:**
   ```bash
   chmod +x test_api.sh
   ./test_api.sh
   ```

### Option 2: Docker (Easiest)

1. **Generate keypair first:**
   ```bash
   cd api
   cargo run --example generate_keypair > ../keypair.json
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Check logs:**
   ```bash
   docker-compose logs -f api
   ```

4. **Test API:**
   ```bash
   curl http://localhost:8080/health
   ```

---

## 📚 Usage Examples

### Creating a Log

```bash
curl -X POST http://localhost:8080/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_action",
    "severity": "info",
    "data": {
      "action": "file_upload",
      "user_id": "user_123",
      "file_size": 1024000
    }
  }'
```

### Querying Logs

```bash
# Get all logs
curl http://localhost:8080/api/v1/logs

# Filter by event type
curl "http://localhost:8080/api/v1/logs?event_type=user_action&limit=10"

# Filter by severity
curl "http://localhost:8080/api/v1/logs?severity=error"
```

### Verifying a Log

```bash
# Replace {id} with actual log UUID
curl http://localhost:8080/api/v1/logs/{id}/verify
```

---

## 🔐 How the Hybrid System Works

1. **Create Log:**
   - Client sends JSON log data
   - API computes SHA-256 hash
   - Full log stored in PostgreSQL
   - Hash submitted to Solana blockchain (async)

2. **Storage:**
   - **Off-chain (PostgreSQL)**: Full JSON data, queryable
   - **On-chain (Solana)**: Only the hash (immutable proof)

3. **Verification:**
   - Fetch log from database
   - Recompute hash from data
   - Query blockchain for stored hash
   - Compare: if they match ✅, data is verified!

**Benefits:**
- ✅ Data integrity guaranteed by blockchain
- ✅ Cost-effective (only hashes on-chain)
- ✅ Fast queries (PostgreSQL)
- ✅ Immutable audit trail

---

## 🔧 Configuration

Edit `api/.env`:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/solana_logger

# Solana (use devnet for testing, mainnet for production)
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_KEYPAIR_PATH=~/.config/solana/id.json

# API
API_HOST=0.0.0.0
API_PORT=8080
RUST_LOG=info
```

---

## 💰 Funding Your Wallet

Your Solana wallet needs SOL to pay for transaction fees.

**For Devnet (Testing):**
1. Get your wallet address:
   ```bash
   # It's printed when you run the API
   # Or check the keypair:
   cat ~/.config/solana/logger-keypair.json
   ```

2. Get free devnet SOL:
   - Visit: https://faucet.solana.com
   - Enter your public key
   - Request airdrop

**For Mainnet (Production):**
- Transfer real SOL to your wallet address
- Each log submission costs ~0.000005 SOL (~$0.0001)

---

## 📊 Monitoring

### Check System Health
```bash
curl http://localhost:8080/health
```

### Get Statistics
```bash
curl http://localhost:8080/api/v1/stats
```

Response:
```json
{
  "total_logs": 1500,
  "pending_logs": 5,
  "confirmed_logs": 1490,
  "failed_logs": 5,
  "wallet_pubkey": "...",
  "wallet_balance_lamports": 100000000
}
```

---

## 🐛 Troubleshooting

### "Failed to connect to database"
- Check PostgreSQL is running: `systemctl status postgresql`
- Verify DATABASE_URL in `.env`
- Test connection: `psql $DATABASE_URL`

### "Failed to load keypair"
- Ensure keypair file exists
- Check SOLANA_KEYPAIR_PATH in `.env`
- Generate new keypair: `cargo run --example generate_keypair`

### "Insufficient funds"
- Check wallet balance: see `/api/v1/stats`
- Fund wallet on devnet: https://faucet.solana.com
- Each transaction costs ~5000 lamports

### Logs not confirming on blockchain
- Check Solana RPC URL is correct
- Verify wallet has sufficient SOL
- Check API logs: `RUST_LOG=debug cargo run`
- Network might be congested (wait a bit)

---

## 🚢 Production Deployment

1. **Use mainnet RPC:**
   ```env
   SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
   ```

2. **Secure your keypair:**
   ```bash
   chmod 600 /path/to/keypair.json
   chown app-user:app-user /path/to/keypair.json
   ```

3. **Enable authentication:**
   ```env
   API_KEY=your-secret-key-here
   ```

4. **Use production database:**
   - Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
   - Enable SSL connections
   - Regular backups

5. **Scale:**
   - Run multiple API instances behind load balancer
   - Use connection pooling (already configured)
   - Monitor with Prometheus/Grafana

---

## 📖 Further Reading

- [Full API Documentation](API.md)
- [Architecture Overview](README.md)
- [Solana Documentation](https://docs.solana.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## 💡 Use Cases

**Audit Logging:**
- Track all administrative actions
- Immutable proof for compliance (SOC2, GDPR)

**Financial Transactions:**
- Log all payment events
- Cryptographic proof of transaction history

**System Monitoring:**
- Tamper-proof log of system events
- Verify logs haven't been modified

**IoT Data:**
- Log sensor readings
- Prove data authenticity

**Supply Chain:**
- Track item movements
- Verifiable chain of custody

---

Need help? Check the API documentation or open an issue!
