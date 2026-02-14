-- Solana Logger Database Schema

-- Logs table: Stores full JSON log entries with blockchain references
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    hash VARCHAR(64) NOT NULL UNIQUE,
    tx_signature VARCHAR(128),
    blockchain_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_logs_event_type ON logs(event_type);
CREATE INDEX IF NOT EXISTS idx_logs_severity ON logs(severity);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_hash ON logs(hash);
CREATE INDEX IF NOT EXISTS idx_logs_tx_signature ON logs(tx_signature);

-- GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_logs_data_gin ON logs USING GIN(data);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_logs_updated_at
    BEFORE UPDATE ON logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Table for tracking blockchain synchronization status
CREATE TABLE IF NOT EXISTS sync_status (
    id SERIAL PRIMARY KEY,
    last_processed_slot BIGINT NOT NULL DEFAULT 0,
    last_sync_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'idle'
);

INSERT INTO sync_status (last_processed_slot) VALUES (0) ON CONFLICT DO NOTHING;

-- Comments
COMMENT ON TABLE logs IS 'Stores log entries with full JSON data and blockchain hash references';
COMMENT ON COLUMN logs.hash IS 'SHA-256 hash of the log data stored on Solana blockchain';
COMMENT ON COLUMN logs.tx_signature IS 'Solana transaction signature containing the hash';
COMMENT ON COLUMN logs.blockchain_status IS 'Status: pending, confirmed, finalized, failed';
