mod models;
mod db;
mod solana;
mod handlers;

use actix_web::{web, App, HttpServer, middleware};
use actix_cors::Cors;
use dotenv::dotenv;
use std::env;
use std::sync::Arc;
use anyhow::Result;

use crate::db::Database;
use crate::solana::SolanaClient;
use crate::handlers::AppState;

#[actix_web::main]
async fn main() -> Result<()> {
    // Load environment variables
    dotenv().ok();
    
    // Initialize logger
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    log::info!("🚀 Starting Solana Logger Microservice");

    // Load configuration
    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");
    let solana_rpc_url = env::var("SOLANA_RPC_URL")
        .unwrap_or_else(|_| "https://api.devnet.solana.com".to_string());
    let solana_keypair_path = env::var("SOLANA_KEYPAIR_PATH")
        .unwrap_or_else(|_| "~/.config/solana/id.json".to_string());
    let api_host = env::var("API_HOST")
        .unwrap_or_else(|_| "0.0.0.0".to_string());
    let api_port = env::var("API_PORT")
        .unwrap_or_else(|_| "8080".to_string())
        .parse::<u16>()
        .expect("Invalid API_PORT");

    log::info!("📊 Connecting to database: {}", database_url);
    
    // Initialize database
    let db = Database::new(&database_url).await?;
    
    log::info!("✅ Database connected");

    // Initialize Solana client
    log::info!("🔗 Connecting to Solana RPC: {}", solana_rpc_url);
    let solana = match SolanaClient::new(&solana_rpc_url, &solana_keypair_path) {
        Ok(client) => {
            log::info!("✅ Solana client initialized");
            log::info!("💰 Wallet: {}", client.pubkey());
            if let Ok(balance) = client.get_balance() {
                log::info!("💰 Balance: {} lamports ({} SOL)", 
                    balance, 
                    balance as f64 / 1_000_000_000.0
                );
            }
            Arc::new(client)
        }
        Err(e) => {
            log::error!("❌ Failed to initialize Solana client: {}", e);
            log::warn!("⚠️  API will run without blockchain integration");
            log::warn!("⚠️  Set SOLANA_KEYPAIR_PATH to enable blockchain features");
            // For development, you might want to panic here
            // or create a mock client
            return Err(e);
        }
    };

    // Create app state
    let app_state = web::Data::new(AppState {
        db,
        solana,
    });

    log::info!("🌐 Starting HTTP server at {}:{}", api_host, api_port);

    // Start HTTP server
    HttpServer::new(move || {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            .app_data(app_state.clone())
            .wrap(middleware::Logger::default())
            .wrap(cors)
            .service(
                web::scope("/api/v1")
                    .route("/logs", web::post().to(handlers::create_log))
                    .route("/logs", web::get().to(handlers::query_logs))
                    .route("/logs/{id}", web::get().to(handlers::get_log))
                    .route("/logs/{id}/verify", web::get().to(handlers::verify_log))
                    .route("/stats", web::get().to(handlers::get_stats))
            )
            .route("/health", web::get().to(handlers::health_check))
    })
    .bind((api_host.as_str(), api_port))?
    .run()
    .await?;

    Ok(())
}
