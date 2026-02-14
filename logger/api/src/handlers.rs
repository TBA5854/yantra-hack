use actix_web::{web, HttpResponse, Responder};
use validator::Validate;
use std::sync::Arc;
use log::{info, error};

use crate::models::*;
use crate::db::Database;
use crate::solana::SolanaClient;

/// Application state shared across handlers
pub struct AppState {
    pub db: Database,
    pub solana: Arc<SolanaClient>,
}

/// Health check endpoint
/// GET /health
pub async fn health_check(state: web::Data<AppState>) -> impl Responder {
    let db_healthy = state.db.health_check().await;
    let solana_healthy = state.solana.health_check().await;

    let response = HealthResponse {
        status: if db_healthy && solana_healthy {
            "healthy".to_string()
        } else {
            "degraded".to_string()
        },
        database: db_healthy,
        solana_rpc: solana_healthy,
        version: env!("CARGO_PKG_VERSION").to_string(),
    };

    HttpResponse::Ok().json(response)
}

/// Create a new log entry
/// POST /api/v1/logs
pub async fn create_log(
    state: web::Data<AppState>,
    request: web::Json<CreateLogRequest>,
) -> impl Responder {
    // Validate request
    if let Err(e) = request.validate() {
        return HttpResponse::BadRequest().json(ErrorResponse {
            error: "validation_error".to_string(),
            message: e.to_string(),
        });
    }

    // Compute hash
    let hash = request.compute_hash();
    info!("Creating log entry with hash: {}", hash);

    // Insert into database
    let log_entry = match state.db.insert_log(&request, &hash).await {
        Ok(entry) => entry,
        Err(e) => {
            error!("Failed to insert log: {}", e);
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "database_error".to_string(),
                message: "Failed to create log entry".to_string(),
            });
        }
    };

    // Submit to blockchain (async, non-blocking)
    let log_id = log_entry.id;
    let hash_clone = hash.clone();
    let db_clone = state.db.pool().clone();
    let solana_clone = Arc::clone(&state.solana);

    // Spawn background task for blockchain submission
    tokio::spawn(async move {
        match solana_clone.submit_log_hash(&hash_clone).await {
            Ok(signature) => {
                info!("Log {} submitted to blockchain: {}", log_id, signature);
                
                // Update database with transaction signature
                let db = Database { pool: db_clone };
                if let Err(e) = db.update_log_tx_signature(log_id, &signature, "confirmed").await {
                    error!("Failed to update log tx signature: {}", e);
                }
            }
            Err(e) => {
                error!("Failed to submit log to blockchain: {}", e);
                
                // Update status to failed
                let db = Database { pool: db_clone };
                if let Err(e) = db.update_log_tx_signature(log_id, "", "failed").await {
                    error!("Failed to update log status: {}", e);
                }
            }
        }
    });

    HttpResponse::Created().json(CreateLogResponse::from(log_entry))
}

/// Get log by ID
/// GET /api/v1/logs/{id}
pub async fn get_log(
    state: web::Data<AppState>,
    path: web::Path<String>,
) -> impl Responder {
    let log_id = match path.parse() {
        Ok(id) => id,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "invalid_id".to_string(),
                message: "Invalid log ID format".to_string(),
            });
        }
    };

    match state.db.get_log_by_id(log_id).await {
        Ok(Some(log)) => HttpResponse::Ok().json(log),
        Ok(None) => HttpResponse::NotFound().json(ErrorResponse {
            error: "not_found".to_string(),
            message: "Log entry not found".to_string(),
        }),
        Err(e) => {
            error!("Failed to fetch log: {}", e);
            HttpResponse::InternalServerError().json(ErrorResponse {
                error: "database_error".to_string(),
                message: "Failed to fetch log entry".to_string(),
            })
        }
    }
}

/// Query logs with filters
/// GET /api/v1/logs?event_type=...&severity=...&limit=...&offset=...
pub async fn query_logs(
    state: web::Data<AppState>,
    params: web::Query<LogQueryParams>,
) -> impl Responder {
    match state.db.query_logs(&params).await {
        Ok((logs, total)) => {
            let limit = params.limit.unwrap_or(100);
            let offset = params.offset.unwrap_or(0);
            
            let response = PaginatedResponse {
                data: logs,
                total,
                limit,
                offset,
            };
            
            HttpResponse::Ok().json(response)
        }
        Err(e) => {
            error!("Failed to query logs: {}", e);
            HttpResponse::InternalServerError().json(ErrorResponse {
                error: "database_error".to_string(),
                message: "Failed to query logs".to_string(),
            })
        }
    }
}

/// Verify log entry against blockchain
/// GET /api/v1/logs/{id}/verify
pub async fn verify_log(
    state: web::Data<AppState>,
    path: web::Path<String>,
) -> impl Responder {
    let log_id = match path.parse() {
        Ok(id) => id,
        Err(_) => {
            return HttpResponse::BadRequest().json(ErrorResponse {
                error: "invalid_id".to_string(),
                message: "Invalid log ID format".to_string(),
            });
        }
    };

    // Get log from database
    let log = match state.db.get_log_by_id(log_id).await {
        Ok(Some(log)) => log,
        Ok(None) => {
            return HttpResponse::NotFound().json(ErrorResponse {
                error: "not_found".to_string(),
                message: "Log entry not found".to_string(),
            });
        }
        Err(e) => {
            error!("Failed to fetch log: {}", e);
            return HttpResponse::InternalServerError().json(ErrorResponse {
                error: "database_error".to_string(),
                message: "Failed to fetch log entry".to_string(),
            });
        }
    };

    // If no transaction signature, log hasn't been submitted yet
    let tx_signature = match &log.tx_signature {
        Some(sig) => sig,
        None => {
            return HttpResponse::Ok().json(VerificationResponse {
                log_id: log.id,
                is_valid: false,
                local_hash: log.hash,
                blockchain_hash: None,
                tx_signature: None,
                blockchain_status: log.blockchain_status,
                message: "Log not yet submitted to blockchain".to_string(),
            });
        }
    };

    // Verify hash on blockchain
    match state.solana.verify_log_hash(tx_signature).await {
        Ok(Some(blockchain_hash)) => {
            let is_valid = blockchain_hash == log.hash;
            HttpResponse::Ok().json(VerificationResponse {
                log_id: log.id,
                is_valid,
                local_hash: log.hash.clone(),
                blockchain_hash: Some(blockchain_hash),
                tx_signature: Some(tx_signature.clone()),
                blockchain_status: log.blockchain_status,
                message: if is_valid {
                    "Log verified successfully".to_string()
                } else {
                    "Hash mismatch - data may be corrupted".to_string()
                },
            })
        }
        Ok(None) => {
            HttpResponse::Ok().json(VerificationResponse {
                log_id: log.id,
                is_valid: false,
                local_hash: log.hash,
                blockchain_hash: None,
                tx_signature: Some(tx_signature.clone()),
                blockchain_status: log.blockchain_status,
                message: "Hash not found in blockchain transaction".to_string(),
            })
        }
        Err(e) => {
            error!("Failed to verify log on blockchain: {}", e);
            HttpResponse::InternalServerError().json(ErrorResponse {
                error: "blockchain_error".to_string(),
                message: format!("Failed to verify log: {}", e),
            })
        }
    }
}

/// Get blockchain statistics
/// GET /api/v1/stats
pub async fn get_stats(state: web::Data<AppState>) -> impl Responder {
    #[derive(serde::Serialize)]
    struct Stats {
        total_logs: i64,
        pending_logs: i64,
        confirmed_logs: i64,
        failed_logs: i64,
        wallet_pubkey: String,
        wallet_balance_lamports: Option<u64>,
    }

    // Query database for statistics
    let total_logs: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM logs")
        .fetch_one(state.db.pool())
        .await
        .unwrap_or(0);

    let pending_logs: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM logs WHERE blockchain_status = 'pending'"
    )
    .fetch_one(state.db.pool())
    .await
    .unwrap_or(0);

    let confirmed_logs: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM logs WHERE blockchain_status = 'confirmed'"
    )
    .fetch_one(state.db.pool())
    .await
    .unwrap_or(0);

    let failed_logs: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM logs WHERE blockchain_status = 'failed'"
    )
    .fetch_one(state.db.pool())
    .await
    .unwrap_or(0);

    let wallet_balance = state.solana.get_balance().ok();

    let stats = Stats {
        total_logs,
        pending_logs,
        confirmed_logs,
        failed_logs,
        wallet_pubkey: state.solana.pubkey().to_string(),
        wallet_balance_lamports: wallet_balance,
    };

    HttpResponse::Ok().json(stats)
}
