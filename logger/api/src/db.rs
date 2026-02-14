use anyhow::{Context, Result};
use sqlx::{PgPool, postgres::PgPoolOptions};
use sqlx::types::{Uuid, Json};
use crate::models::{LogEntry, CreateLogRequest, LogQueryParams};

/// Database connection pool manager
pub struct Database {
    pool: PgPool,
}

impl Database {
    /// Create a new database connection pool
    pub async fn new(database_url: &str) -> Result<Self> {
        let pool = PgPoolOptions::new()
            .max_connections(20)
            .connect(database_url)
            .await
            .context("Failed to connect to database")?;
        
        Ok(Self { pool })
    }

    /// Get reference to the connection pool
    pub fn pool(&self) -> &PgPool {
        &self.pool
    }

    /// Health check - verify database connectivity
    pub async fn health_check(&self) -> bool {
        sqlx::query("SELECT 1")
            .fetch_one(&self.pool)
            .await
            .is_ok()
    }

    /// Insert a new log entry
    pub async fn insert_log(
        &self,
        request: &CreateLogRequest,
        hash: &str,
    ) -> Result<LogEntry> {
        let log = sqlx::query_as::<_, LogEntry>(
            r#"
            INSERT INTO logs (event_type, severity, data, hash, blockchain_status)
            VALUES ($1, $2, $3, $4, 'pending')
            RETURNING *
            "#,
        )
        .bind(&request.event_type)
        .bind(&request.severity)
        .bind(Json(&request.data))
        .bind(hash)
        .fetch_one(&self.pool)
        .await
        .context("Failed to insert log entry")?;

        Ok(log)
    }

    /// Update log entry with blockchain transaction signature
    pub async fn update_log_tx_signature(
        &self,
        log_id: Uuid,
        tx_signature: &str,
        status: &str,
    ) -> Result<()> {
        sqlx::query(
            r#"
            UPDATE logs
            SET tx_signature = $1, blockchain_status = $2, updated_at = NOW()
            WHERE id = $3
            "#,
        )
        .bind(tx_signature)
        .bind(status)
        .bind(log_id)
        .execute(&self.pool)
        .await
        .context("Failed to update log transaction signature")?;

        Ok(())
    }

    /// Get log entry by ID
    pub async fn get_log_by_id(&self, log_id: Uuid) -> Result<Option<LogEntry>> {
        let log = sqlx::query_as::<_, LogEntry>(
            r#"
            SELECT * FROM logs WHERE id = $1
            "#,
        )
        .bind(log_id)
        .fetch_optional(&self.pool)
        .await
        .context("Failed to fetch log entry")?;

        Ok(log)
    }

    /// Query logs with filters and pagination
    pub async fn query_logs(
        &self,
        params: &LogQueryParams,
    ) -> Result<(Vec<LogEntry>, i64)> {
        let limit = params.limit.unwrap_or(100).min(1000);
        let offset = params.offset.unwrap_or(0);

        // Build dynamic query
        let mut query = String::from(
            r#"
            SELECT * FROM logs
            WHERE 1=1
            "#,
        );

        let mut count_query = String::from(
            r#"
            SELECT COUNT(*) FROM logs
            WHERE 1=1
            "#,
        );

        // Add filters
        if params.event_type.is_some() {
            query.push_str(" AND event_type = $1");
            count_query.push_str(" AND event_type = $1");
        }
        if params.severity.is_some() {
            let param_num = if params.event_type.is_some() { 2 } else { 1 };
            query.push_str(&format!(" AND severity = ${}", param_num));
            count_query.push_str(&format!(" AND severity = ${}", param_num));
        }
        if params.from_date.is_some() {
            let param_num = 1 + params.event_type.is_some() as i32 + params.severity.is_some() as i32;
            query.push_str(&format!(" AND created_at >= ${}", param_num));
            count_query.push_str(&format!(" AND created_at >= ${}", param_num));
        }
        if params.to_date.is_some() {
            let param_num = 1 + params.event_type.is_some() as i32 
                            + params.severity.is_some() as i32 
                            + params.from_date.is_some() as i32;
            query.push_str(&format!(" AND created_at <= ${}", param_num));
            count_query.push_str(&format!(" AND created_at <= ${}", param_num));
        }

        query.push_str(" ORDER BY created_at DESC");
        
        // Add pagination params
        let limit_param = 1 + params.event_type.is_some() as i32 
                           + params.severity.is_some() as i32 
                           + params.from_date.is_some() as i32 
                           + params.to_date.is_some() as i32;
        query.push_str(&format!(" LIMIT ${} OFFSET ${}", limit_param, limit_param + 1));

        // Execute queries
        let mut logs_query = sqlx::query_as::<_, LogEntry>(&query);
        let mut count_query_exec = sqlx::query_scalar::<_, i64>(&count_query);

        // Bind parameters in order
        if let Some(ref event_type) = params.event_type {
            logs_query = logs_query.bind(event_type);
            count_query_exec = count_query_exec.bind(event_type);
        }
        if let Some(ref severity) = params.severity {
            logs_query = logs_query.bind(severity);
            count_query_exec = count_query_exec.bind(severity);
        }
        if let Some(ref from_date) = params.from_date {
            logs_query = logs_query.bind(from_date);
            count_query_exec = count_query_exec.bind(from_date);
        }
        if let Some(ref to_date) = params.to_date {
            logs_query = logs_query.bind(to_date);
            count_query_exec = count_query_exec.bind(to_date);
        }
        
        logs_query = logs_query.bind(limit).bind(offset);

        let logs = logs_query.fetch_all(&self.pool).await
            .context("Failed to query logs")?;
        
        let total = count_query_exec.fetch_one(&self.pool).await
            .context("Failed to count logs")?;

        Ok((logs, total))
    }

    /// Delete old logs (for maintenance)
    pub async fn delete_logs_older_than(&self, days: i64) -> Result<u64> {
        let result = sqlx::query(
            r#"
            DELETE FROM logs
            WHERE created_at < NOW() - INTERVAL '1 day' * $1
            "#,
        )
        .bind(days)
        .execute(&self.pool)
        .await
        .context("Failed to delete old logs")?;

        Ok(result.rows_affected())
    }
}
