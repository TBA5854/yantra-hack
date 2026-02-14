use anyhow::{Context, Result, anyhow};
use solana_client::rpc_client::RpcClient;
use solana_sdk::{
    commitment_config::CommitmentConfig,
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    signature::{Keypair, Signature},
    signer::Signer,
    system_program,
    transaction::Transaction,
};
use std::str::FromStr;

/// Solana blockchain client for log hash storage
pub struct SolanaClient {
    rpc_client: RpcClient,
    keypair: Keypair,
    program_id: Pubkey,
}

impl SolanaClient {
    /// Create a new Solana client
    pub fn new(rpc_url: &str, keypair_path: &str) -> Result<Self> {
        let rpc_client = RpcClient::new_with_commitment(
            rpc_url.to_string(),
            CommitmentConfig::confirmed(),
        );

        // Load keypair from file
        let keypair = Self::load_keypair(keypair_path)
            .context("Failed to load keypair")?;

        // For simplicity, we'll use a memo program approach
        // The actual program ID would be deployed separately
        // Using system program as placeholder - in production, deploy a custom program
        let program_id = system_program::id();

        Ok(Self {
            rpc_client,
            keypair,
            program_id,
        })
    }

    /// Load keypair from JSON file
    fn load_keypair(path: &str) -> Result<Keypair> {
        let expanded_path = shellexpand::tilde(path);
        let keypair_bytes = std::fs::read(expanded_path.as_ref())
            .context("Failed to read keypair file")?;
        
        let keypair_data: Vec<u8> = serde_json::from_slice(&keypair_bytes)
            .context("Failed to parse keypair JSON")?;
        
        Keypair::from_bytes(&keypair_data)
            .context("Invalid keypair data")
    }

    /// Health check - verify RPC connectivity
    pub async fn health_check(&self) -> bool {
        self.rpc_client.get_version().is_ok()
    }

    /// Submit log hash to blockchain using memo instruction
    /// In production, this would interact with a custom Solana program
    pub async fn submit_log_hash(&self, hash: &str) -> Result<String> {
        // Get recent blockhash
        let recent_blockhash = self.rpc_client
            .get_latest_blockhash()
            .context("Failed to get recent blockhash")?;

        // Create memo instruction with the hash
        // Format: "LOG:<hash>"
        let memo_data = format!("LOG:{}", hash);
        
        // Use spl-memo program
        let memo_program_id = Pubkey::from_str("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")
            .unwrap();

        let instruction = Instruction {
            program_id: memo_program_id,
            accounts: vec![],
            data: memo_data.into_bytes(),
        };

        // Create and sign transaction
        let transaction = Transaction::new_signed_with_payer(
            &[instruction],
            Some(&self.keypair.pubkey()),
            &[&self.keypair],
            recent_blockhash,
        );

        // Send transaction
        let signature = self.rpc_client
            .send_and_confirm_transaction(&transaction)
            .context("Failed to send transaction")?;

        Ok(signature.to_string())
    }

    /// Verify log hash exists on blockchain
    pub async fn verify_log_hash(&self, tx_signature: &str) -> Result<Option<String>> {
        let signature = Signature::from_str(tx_signature)
            .context("Invalid transaction signature")?;

        // Get transaction details
        let tx = self.rpc_client
            .get_transaction(&signature, solana_client::rpc_config::RpcTransactionConfig {
                encoding: Some(solana_transaction_status::UiTransactionEncoding::Json),
                commitment: Some(CommitmentConfig::confirmed()),
                max_supported_transaction_version: Some(0),
            })
            .context("Failed to fetch transaction")?;

        // Extract memo data from transaction
        if let Some(meta) = tx.transaction.meta {
            if let Some(log_messages) = meta.log_messages {
                for log in log_messages {
                    if log.contains("LOG:") {
                        // Extract hash from memo
                        if let Some(hash_start) = log.find("LOG:") {
                            let hash = &log[hash_start + 4..];
                            if let Some(end) = hash.find('"').or(hash.find(' ')) {
                                return Ok(Some(hash[..end].to_string()));
                            }
                            return Ok(Some(hash.to_string()));
                        }
                    }
                }
            }
        }

        Ok(None)
    }

    /// Get account balance
    pub fn get_balance(&self) -> Result<u64> {
        let balance = self.rpc_client
            .get_balance(&self.keypair.pubkey())
            .context("Failed to get balance")?;
        Ok(balance)
    }

    /// Get public key
    pub fn pubkey(&self) -> Pubkey {
        self.keypair.pubkey()
    }
}

// For testing without actual blockchain
#[cfg(test)]
pub struct MockSolanaClient;

#[cfg(test)]
impl MockSolanaClient {
    pub fn new() -> Self {
        Self
    }

    pub async fn submit_log_hash(&self, _hash: &str) -> Result<String> {
        Ok("mock_signature_12345".to_string())
    }

    pub async fn verify_log_hash(&self, _tx_signature: &str) -> Result<Option<String>> {
        Ok(Some("mock_hash_67890".to_string()))
    }
}
