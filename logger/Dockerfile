FROM rust:1.83-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy manifests
COPY api/Cargo.toml api/Cargo.toml

# Create dummy main.rs to cache dependencies
RUN mkdir -p api/src && \
    echo "fn main() {}" > api/src/main.rs && \
    cd api && \
    cargo build --release && \
    rm -rf src

# Copy source code
COPY api/src api/src
COPY api/examples api/examples

# Build for release
RUN cd api && cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/api/target/release/solana-logger-api /app/

# Expose port
EXPOSE 8080

# Run the binary
CMD ["/app/solana-logger-api"]
