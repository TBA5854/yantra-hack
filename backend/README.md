# Multi-Chain Stablecoin Risk Intelligence Platform

**Comprehensive risk monitoring for stablecoins across Ethereum, Arbitrum, and Solana with Temporal Confidence Scoring (TCS)**

## 🎯 Overview

This platform implements a **4-layer progressive architecture** for monitoring stablecoin risk across multiple blockchains with heterogeneous finality characteristics. It quantifies epistemic uncertainty through **Temporal Confidence Scores (TCS)**, providing meta-awareness about the reliability of risk assessments.

### Key Innovation: Temporal Confidence Score (TCS)

**Problem**: When aggregating data from multiple blockchains with different finality times (Ethereum: 15 min, Arbitrum: 13 sec, Solana: 2 min), how confident should we be in our risk assessment?

**Solution**: TCS quantifies confidence by combining:

```
TCS = (finality_weight * chain_confidence * completeness) / staleness_penalty

Where:
- finality_weight = Weighted avg of event finality across sources
- chain_confidence = Min finality across all chains (weakest link)
- completeness = Fraction of expected data sources present
- staleness_penalty = Penalty for data age
```

## 🏗️ Architecture

### Progressive 4-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Sharded Scaling (Future)                           │
│   • Feature-based sharding                                   │
│   • Load balancing & fault tolerance                         │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Multi-Chain Synchronization                         │
│   • Cross-chain aggregation                                  │
│   • Reorg-aware event versioning                             │
│   • Heterogeneous finality handling                          │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Multi-Coin Monitoring                               │
│   • Coin registry & configuration                            │
│   • Cross-coin comparison                                    │
└─────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Perfected Single-Coin Core ✅ IMPLEMENTED          │
│   • Multi-source data ingestion (6 sources)                  │
│   • Data quality pipeline                                    │
│   • TCS calculation                                          │
│   • Window state machine                                     │
└─────────────────────────────────────────────────────────────┘
```

### Supported Chains

| Chain     | Finality Time | Tier1 (0.3) | Tier2 (0.8) | Tier3 (1.0) |
|-----------|--------------|-------------|-------------|-------------|
| Ethereum  | ~12.8 min    | 12 sec      | 6.4 min     | 12.8 min    |
| Arbitrum  | ~15 min      | 1 sec       | 13 sec      | 15 min      |
| Solana    | ~2 min       | 400 ms      | 13 sec      | 2 min       |

### Data Sources (Layer 1)

1. **Price** - CoinGecko API
2. **Liquidity** - DEX data (Uniswap, Curve, Orca) - *Planned*
3. **Supply** - On-chain transfer events - *Planned*
4. **Volatility** - Market volatility metrics - *Planned*
5. **Sentiment** - Twitter/Reddit analysis - *Planned*

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- `uv` (Python package manager)
- API keys (optional for demo):
  - CoinGecko API key
  - Twitter API keys
  - Reddit API keys

### Installation

```bash
# Clone repository
cd backend

# Install dependencies (already done if you followed setup)
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your API keys (optional for basic demo)
nano .env
```

### Run Layer 1 Demo

```bash
# Activate virtual environment
source .venv/bin/activate

# Run single-window demo
python -m src.layer1_core.demo_layer1
```

This demonstrates:
- ✅ Price data fetching from CoinGecko
- ✅ Data quality pipeline (normalization, deduplication, outlier detection)
- ✅ TCS calculation with full breakdown
- ✅ Window state machine (OPEN → PROVISIONAL → FINAL)
- ✅ Cross-source aggregation
- ✅ Depeg detection
- ✅ Attestation decision logic

## 📁 Project Structure

```
backend/
├── src/
│   ├── layer1_core/           # ✅ Layer 1: Single-Coin Core
│   │   ├── sources/           # Data source connectors
│   │   │   └── price_source.py    # CoinGecko price fetcher
│   │   ├── finality/          # Blockchain finality tracking
│   │   │   └── tracker.py         # Multi-chain finality trackers
│   │   ├── tcs/               # Temporal Confidence Score
│   │   │   └── calculator.py      # TCS calculation engine
│   │   ├── quality/           # Data quality pipeline
│   │   │   └── pipeline.py        # Quality filters + backpressure
│   │   ├── pipeline/          # Streaming pipeline
│   │   │   └── window_manager.py  # Window state machine
│   │   └── demo_layer1.py     # 🎬 Demo script
│   │
│   ├── layer2_multicoin/      # 🔜 Layer 2: Multi-Coin (Planned)
│   ├── layer3_multichain/     # 🔜 Layer 3: Multi-Chain (Planned)
│   ├── layer4_sharded/        # 🔜 Layer 4: Sharded (Planned)
│   │
│   ├── common/
│   │   ├── config.py          # ✅ Chain-aware configuration
│   │   ├── schema.py          # ✅ Unified event schema with TCS
│   │   └── utils/
│   │
│   └── attestation/           # 🔜 Blockchain attestation (Planned)
│
├── pyproject.toml             # ✅ uv project config
├── .env.example               # ✅ Environment template
└── README.md                  # ✅ This file
```

## 🧪 Layer 1 Implementation Status

### ✅ Completed Components

| Component | File | Status | Description |
|-----------|------|--------|-------------|
| **Config** | `common/config.py` | ✅ Done | Chain-aware config with finality tiers |
| **Schema** | `common/schema.py` | ✅ Done | Unified event schema with TCS fields |
| **Finality Tracker** | `layer1_core/finality/tracker.py` | ✅ Done | Multi-chain finality tracking (stubs) |
| **TCS Calculator** | `layer1_core/tcs/calculator.py` | ✅ Done | Full TCS calculation with 5 components |
| **Window Manager** | `layer1_core/pipeline/window_manager.py` | ✅ Done | State machine (OPEN→PROVISIONAL→FINAL) |
| **Quality Pipeline** | `layer1_core/quality/pipeline.py` | ✅ Done | Normalization, dedup, outliers, backpressure |
| **Price Source** | `layer1_core/sources/price_source.py` | ✅ Done | CoinGecko API integration |
| **Demo** | `layer1_core/demo_layer1.py` | ✅ Done | End-to-end demonstration |

### 🔜 Pending (Next Phase)

- [ ] Implement remaining data sources (liquidity, supply, volatility, sentiment)
- [ ] Connect finality trackers to real blockchain RPCs
- [ ] Implement Pathway streaming engine
- [ ] Add persistence layer (database)
- [ ] Build monitoring dashboard (Grafana)
- [ ] Implement attestation to blockchain

## 📊 TCS Calculation Details

### Formula Breakdown

```python
# Component 1: Finality Weight
finality_weight = sum(
    event.finality_conf * source_importance[event.source]
    for event in events
) / total_importance

# Component 2: Chain Confidence (Weakest Link)
chain_confidence = min(
    min_finality_per_chain[chain]
    for chain in contributing_chains
)

# Component 3: Completeness
completeness = len(present_sources) / len(expected_sources)

# Component 4: Staleness Penalty
staleness_penalty = (
    1.0 if age < 5min else
    0.9 if age < 10min else
    0.7
)

# Final TCS
TCS = (finality_weight * chain_confidence * completeness) / staleness_penalty
```

### Finality Tier Mapping

| Tier | Confidence | Meaning | Example (Ethereum) |
|------|------------|---------|-------------------|
| **Tier 1** | 0.3 | Probable | 1 confirmation (~12 sec) |
| **Tier 2** | 0.8 | Highly Likely | 32 confirmations (~6.4 min) |
| **Tier 3** | 1.0 | Final | 64 confirmations (~12.8 min) |

## 🔄 Window State Machine

```
┌──────┐  provisional_delay (1 min)  ┌─────────────┐
│ OPEN │─────────────────────────────▶│ PROVISIONAL │
└──────┘                              └─────────────┘
   │                                         │
   │ Accepting new events                    │ Waiting for finality
   │                                         │
   │                                         │ finalization_delay (15 min)
   │                                         │
   │                                         ▼
   │                                  ┌───────┐
   └──────────────────────────────────│ FINAL │
                                      └───────┘
                                         │
                                         │ Immutable snapshot
                                         │ Ready for attestation
```

## 🎯 Use Cases

1. **DeFi Risk Management**
   - Monitor stablecoin depeg risk in real-time
   - Adjust collateral ratios based on TCS-weighted risk

2. **Trading Bots**
   - Only execute trades when TCS > 0.8 (high confidence)
   - Avoid acting on unfinalized data during reorgs

3. **Regulatory Compliance**
   - Provide auditable confidence metrics for risk reports
   - Attestation to blockchain for immutable record

4. **Research & Analytics**
   - Study cross-chain depeg correlation
   - Analyze finality impact on risk assessment

## 🛠️ Development Roadmap

### Phase 1: Foundation (✅ Current)
- [x] Layer 1 core implementation
- [x] TCS calculator
- [x] Window state machine
- [x] Demo script

### Phase 2: Data Sources (Next)
- [ ] Liquidity monitoring (DEX APIs)
- [ ] Supply tracking (on-chain events)
- [ ] Volatility metrics
- [ ] Sentiment analysis

### Phase 3: Multi-Chain (Layer 3)
- [ ] Cross-chain aggregation
- [ ] Reorg detection and correction
- [ ] Chain-specific finality trackers

### Phase 4: Production (Layer 4)
- [ ] Sharded architecture
- [ ] Load balancing
- [ ] Monitoring dashboard
- [ ] Blockchain attestation

## 📚 Documentation

- [Architecture Plan](/home/tba/.claude/plans/delegated-strolling-fountain.md) - Complete technical specification
- [Configuration Guide](src/common/config.py) - Chain and source configuration
- [Schema Reference](src/common/schema.py) - Event data models
- [TCS Deep Dive](src/layer1_core/tcs/calculator.py) - TCS calculation details

## 🤝 Contributing

This is a hackathon/research project. Contributions welcome!

### Key Areas for Contribution:
1. Additional data sources (Chainlink, The Graph, etc.)
2. Advanced sentiment analysis models
3. Reorg detection improvements
4. Dashboard UI development
5. Smart contract for attestation layer

## 📄 License

MIT License

## 🙏 Acknowledgments

- **Pathway** - Streaming data processing framework
- **CoinGecko** - Price data API
- **Ethereum, Arbitrum, Solana** - Blockchain infrastructure
