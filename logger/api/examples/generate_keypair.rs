// Example: Generate a Solana keypair
// Run with: cargo run --example generate_keypair

use solana_sdk::signature::{Keypair, Signer};
use std::io::{self, Write};

fn main() {
    let keypair = Keypair::new();
    
    // Output as JSON array format (compatible with Solana CLI)
    let keypair_bytes = keypair.to_bytes();
    let json = serde_json::to_string(&keypair_bytes.to_vec()).unwrap();
    
    // Print to stdout (can be redirected to file)
    println!("{}", json);
    
    // Print info to stderr so it doesn't mix with the JSON output
    eprintln!("\n✅ Keypair generated successfully!");
    eprintln!("📍 Public Key: {}", keypair.pubkey());
    eprintln!("\n⚠️  IMPORTANT: Keep this keypair safe and secure!");
    eprintln!("⚠️  Never share your private key with anyone!");
    eprintln!("\n💰 Fund this wallet on devnet:");
    eprintln!("   https://faucet.solana.com");
}
