#!/bin/bash

# Setup script for Solana Logger Microservice

set -e

echo "🚀 Setting up Solana Logger Microservice"
echo "========================================"
echo ""

# 1. Check prerequisites
echo "1️⃣ Checking prerequisites..."

if ! command -v cargo &> /dev/null; then
    echo "❌ Cargo not found. Please install Rust:"
    echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. You may need to install it:"
    echo "   sudo apt-get install postgresql-client"
fi

echo "✅ Prerequisites check complete"
echo ""

# 2. Setup database
echo "2️⃣ Setting up database..."
echo ""

read -p "Enter PostgreSQL database name (default: solana_logger): " DB_NAME
DB_NAME=${DB_NAME:-solana_logger}

read -p "Enter PostgreSQL user (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}

read -sp "Enter PostgreSQL password: " DB_PASS
echo ""

DB_URL="postgresql://${DB_USER}:${DB_PASS}@localhost/${DB_NAME}"

echo "Creating database..."
PGPASSWORD=$DB_PASS createdb -U $DB_USER $DB_NAME 2>/dev/null || echo "Database already exists"

echo "Running migrations..."
PGPASSWORD=$DB_PASS psql -U $DB_USER -d $DB_NAME -f api/schema.sql

echo "✅ Database setup complete"
echo ""

# 3. Setup Solana keypair
echo "3️⃣ Setting up Solana keypair..."
echo ""

SOLANA_DIR="$HOME/.config/solana"
KEYPAIR_PATH="$SOLANA_DIR/logger-keypair.json"

if [ -f "$KEYPAIR_PATH" ]; then
    echo "Keypair already exists at $KEYPAIR_PATH"
else
    echo "Creating new Solana keypair..."
    mkdir -p $SOLANA_DIR
    
    # Generate a new keypair using Rust
    cd api
    cargo run --example generate_keypair > $KEYPAIR_PATH
    cd ..
    
    echo "✅ Keypair created at $KEYPAIR_PATH"
fi

echo ""

# 4. Create .env file
echo "4️⃣ Creating environment configuration..."
echo ""

cat > api/.env << EOF
# Database Configuration
DATABASE_URL=$DB_URL

# Solana Configuration
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_KEYPAIR_PATH=$KEYPAIR_PATH

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8080
RUST_LOG=info
EOF

echo "✅ Environment file created at api/.env"
echo ""

# 5. Build project
echo "5️⃣ Building project..."
echo ""

cd api
cargo build --release

echo "✅ Build complete"
echo ""

# 6. Display next steps
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Fund your Solana wallet (devnet):"
echo "   Your wallet pubkey is in: $KEYPAIR_PATH"
echo "   Get devnet SOL: https://faucet.solana.com"
echo ""
echo "2. Start the API server:"
echo "   cd api"
echo "   cargo run --release"
echo ""
echo "3. Test the API:"
echo "   chmod +x ../test_api.sh"
echo "   ../test_api.sh"
echo ""
echo "4. View API documentation:"
echo "   cat ../API.md"
echo ""
echo "🎉 Happy logging!"
