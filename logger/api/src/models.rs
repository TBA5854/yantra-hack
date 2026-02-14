use serde::{Deserialize, Serialize};
use sqlx::types::{Json, Uuid};
use chrono::{DateTime, Utc};
use validator::Validate;

/// Log entry stored in the database
#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct LogEntry {
    pub id: Uuid,
    pub event_type: String,
    pub severity: String,
    pub data: Json<serde_json::Value>,
    pub hash: String,
    pub tx_signature: Option<String>,
    pub blockchain_status: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Request to create a new log entry
#[derive(Debug, Deserialize, Validate)]
pub struct CreateLogRequest {
    #[validate(length(min = 1, max = 255))]
    pub event_type: String,
    
    #[validate(length(min = 1, max = 50))]
    pub severity: String,
    
    pub data: serde_json::Value,
}

/// Response after creating a log entry
#[derive(Debug, Serialize)]
pub struct CreateLogResponse {
    pub id: Uuid,
    pub hash: String,
    pub tx_signature: Option<String>,
    pub blockchain_status: String,
    pub created_at: DateTime<Utc>,
}

/// Query parameters for listing logs
#[derive(Debug, Deserialize)]
pub struct LogQueryParams {
    pub event_type: Option<String>,
    pub severity: Option<String>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
    pub from_date: Option<DateTime<Utc>>,
    pub to_date: Option<DateTime<Utc>>,
}

/// Response for log verification
#[derive(Debug, Serialize)]
pub struct VerificationResponse {
    pub log_id: Uuid,
    pub is_valid: bool,
    pub local_hash: String,
    pub blockchain_hash: Option<String>,
    pub tx_signature: Option<String>,
    pub blockchain_status: String,
    pub message: String,
}

/// Pagination metadata
#[derive(Debug, Serialize)]
pub struct PaginatedResponse<T> {
    pub data: Vec<T>,
    pub total: i64,
    pub limit: i64,
    pub offset: i64,
}

/// Health check response
#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub database: bool,
    pub solana_rpc: bool,
    pub version: String,
}

/// Error response
#[derive(Debug, Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub message: String,
}

impl CreateLogRequest {
    /// Compute SHA-256 hash of the log data
    pub fn compute_hash(&self) -> String {
        use sha2::{Sha256, Digest};
        
        // Create a deterministic string from the log data
        let data_str = format!(
            "{}:{}:{}",
            self.event_type,
            self.severity,
            serde_json::to_string(&self.data).unwrap_or_default()
        );
        
        let mut hasher = Sha256::new();
        hasher.update(data_str.as_bytes());
        let result = hasher.finalize();
        hex::encode(result)
    }
}

impl From<LogEntry> for CreateLogResponse {
    fn from(entry: LogEntry) -> Self {
        CreateLogResponse {
            id: entry.id,
            hash: entry.hash,
            tx_signature: entry.tx_signature,
            blockchain_status: entry.blockchain_status,
            created_at: entry.created_at,
        }
    }
}
