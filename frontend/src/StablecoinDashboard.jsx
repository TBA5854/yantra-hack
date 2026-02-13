import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingDown, TrendingUp, Activity, Shield, Database, Brain, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

// Mock data for demonstration
const STABLECOINS = [
  {
    id: 'usdt',
    name: 'Tether USD',
    symbol: 'USDT',
    price: 0.9998,
    pegDeviation: -0.02,
    riskScore: 15,
    rating: 'AAA',
    liquidity: 8500000000,
    liquidityChange: -2.3,
    reserveHealth: 98,
    marketCap: 95000000000,
    volume24h: 52000000000,
    alerts: []
  },
  {
    id: 'usdc',
    name: 'USD Coin',
    symbol: 'USDC',
    price: 1.0001,
    pegDeviation: 0.01,
    riskScore: 8,
    rating: 'AAA',
    liquidity: 6200000000,
    liquidityChange: 1.2,
    reserveHealth: 99,
    marketCap: 38000000000,
    volume24h: 8500000000,
    alerts: []
  },
  {
    id: 'dai',
    name: 'Dai',
    symbol: 'DAI',
    price: 0.9972,
    pegDeviation: -0.28,
    riskScore: 42,
    rating: 'BB',
    liquidity: 950000000,
    liquidityChange: -8.7,
    reserveHealth: 87,
    marketCap: 5200000000,
    volume24h: 420000000,
    alerts: ['Liquidity stress detected', 'Peg deviation increasing']
  },
  {
    id: 'busd',
    name: 'Binance USD',
    symbol: 'BUSD',
    price: 0.9825,
    pegDeviation: -1.75,
    riskScore: 78,
    rating: 'D',
    liquidity: 420000000,
    liquidityChange: -24.5,
    reserveHealth: 62,
    marketCap: 3800000000,
    volume24h: 890000000,
    alerts: ['Critical: High de-pegging risk', 'Reserve concentration warning', 'Liquidity crisis']
  }
];

const HISTORICAL_DATA = [
  { time: '00:00', usdt: 1.0000, usdc: 1.0000, dai: 0.9985, busd: 0.9920 },
  { time: '04:00', usdt: 0.9999, usdc: 1.0001, dai: 0.9982, busd: 0.9905 },
  { time: '08:00', usdt: 0.9998, usdc: 1.0000, dai: 0.9978, busd: 0.9880 },
  { time: '12:00', usdt: 0.9997, usdc: 1.0002, dai: 0.9975, busd: 0.9850 },
  { time: '16:00', usdt: 0.9998, usdc: 1.0001, dai: 0.9973, busd: 0.9835 },
  { time: '20:00', usdt: 0.9998, usdc: 1.0001, dai: 0.9972, busd: 0.9825 }
];

const StablecoinDashboard = () => {
  const [selectedCoin, setSelectedCoin] = useState(STABLECOINS[0]);
  const [liveUpdate, setLiveUpdate] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    if (liveUpdate) {
      const interval = setInterval(() => {
        setLastUpdate(new Date());
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [liveUpdate]);

  const getRiskColor = (score) => {
    if (score < 20) return 'rgb(34, 197, 94)';
    if (score < 40) return 'rgb(234, 179, 8)';
    if (score < 60) return 'rgb(249, 115, 22)';
    return 'rgb(239, 68, 68)';
  };

  const getRatingColor = (rating) => {
    if (rating === 'AAA' || rating === 'AA') return 'rgb(34, 197, 94)';
    if (rating === 'A' || rating === 'BBB') return 'rgb(234, 179, 8)';
    if (rating === 'BB' || rating === 'B') return 'rgb(249, 115, 22)';
    return 'rgb(239, 68, 68)';
  };

  const formatCurrency = (value) => {
    if (value >= 1000000000) return `$${(value / 1000000000).toFixed(2)}B`;
    if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
      fontFamily: '"Outfit", -apple-system, sans-serif',
      color: '#e2e8f0',
      padding: '2rem',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated background */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%)',
        pointerEvents: 'none',
        animation: 'pulse 10s ease-in-out infinite'
      }} />

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
        
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        
        .card {
          background: rgba(30, 41, 59, 0.6);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 16px;
          padding: 1.5rem;
          transition: all 0.3s ease;
          animation: slideIn 0.5s ease-out;
        }
        
        .card:hover {
          transform: translateY(-4px);
          border-color: rgba(59, 130, 246, 0.3);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .coin-card {
          cursor: pointer;
          position: relative;
          overflow: hidden;
        }
        
        .coin-card.selected {
          border-color: rgba(59, 130, 246, 0.5);
          background: rgba(59, 130, 246, 0.1);
        }
        
        .stat-value {
          font-family: 'JetBrains Mono', monospace;
          font-weight: 600;
          font-size: 1.5rem;
        }
        
        .pill {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 600;
        }
      `}</style>

      {/* Header */}
      <div style={{ position: 'relative', marginBottom: '2rem', animation: 'slideIn 0.5s ease-out' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'float 3s ease-in-out infinite'
            }}>
              <Shield size={28} color="white" />
            </div>
            <div>
              <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: 0, background: 'linear-gradient(135deg, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                StableGuard
              </h1>
              <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.875rem', fontWeight: 500 }}>
                AI-Powered Stablecoin Risk Monitoring
              </p>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="pill" style={{ 
              background: liveUpdate ? 'rgba(34, 197, 94, 0.2)' : 'rgba(100, 116, 139, 0.2)',
              border: `1px solid ${liveUpdate ? 'rgba(34, 197, 94, 0.3)' : 'rgba(100, 116, 139, 0.3)'}`,
              color: liveUpdate ? '#4ade80' : '#94a3b8'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: liveUpdate ? '#22c55e' : '#64748b',
                animation: liveUpdate ? 'pulse 2s ease-in-out infinite' : 'none'
              }} />
              {liveUpdate ? 'Live' : 'Paused'}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#94a3b8', fontFamily: 'JetBrains Mono' }}>
              Last updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>

      {/* Stablecoin Cards Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '1rem', 
        marginBottom: '2rem' 
      }}>
        {STABLECOINS.map((coin, index) => (
          <div
            key={coin.id}
            className={`card coin-card ${selectedCoin.id === coin.id ? 'selected' : ''}`}
            onClick={() => setSelectedCoin(coin)}
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
              <div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>
                  {coin.symbol}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
                  {coin.name}
                </div>
              </div>
              <div className="pill" style={{ 
                background: `${getRatingColor(coin.rating)}20`,
                border: `1px solid ${getRatingColor(coin.rating)}40`,
                color: getRatingColor(coin.rating)
              }}>
                {coin.rating}
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div className="stat-value" style={{ color: Math.abs(coin.pegDeviation) > 0.5 ? '#f87171' : '#4ade80' }}>
                ${coin.price.toFixed(4)}
              </div>
              <div style={{ fontSize: '0.875rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                {coin.pegDeviation >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                {coin.pegDeviation >= 0 ? '+' : ''}{coin.pegDeviation}%
              </div>
            </div>

            <div style={{ 
              width: '100%', 
              height: '8px', 
              background: 'rgba(51, 65, 85, 0.5)', 
              borderRadius: '9999px',
              overflow: 'hidden',
              marginBottom: '0.75rem'
            }}>
              <div style={{
                width: `${coin.riskScore}%`,
                height: '100%',
                background: `linear-gradient(90deg, ${getRiskColor(coin.riskScore)}, ${getRiskColor(coin.riskScore)}dd)`,
                transition: 'width 1s ease-out'
              }} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                Risk Score
              </span>
              <span style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, fontSize: '1.125rem', color: getRiskColor(coin.riskScore) }}>
                {coin.riskScore}/100
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Price Chart */}
        <div className="card" style={{ animationDelay: '0.4s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
              Peg Stability (24h)
            </h2>
            <Activity size={20} color="#60a5fa" />
          </div>

          <div style={{ position: 'relative', height: '200px' }}>
            <svg width="100%" height="100%" viewBox="0 0 600 200" preserveAspectRatio="none">
              {/* Grid lines */}
              <line x1="0" y1="100" x2="600" y2="100" stroke="rgba(148, 163, 184, 0.2)" strokeWidth="1" strokeDasharray="5,5" />
              <line x1="0" y1="50" x2="600" y2="50" stroke="rgba(148, 163, 184, 0.1)" strokeWidth="1" strokeDasharray="5,5" />
              <line x1="0" y1="150" x2="600" y2="150" stroke="rgba(148, 163, 184, 0.1)" strokeWidth="1" strokeDasharray="5,5" />
              
              {/* Lines for each coin */}
              {['usdt', 'usdc', 'dai', 'busd'].map((coin, idx) => {
                const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
                const points = HISTORICAL_DATA.map((d, i) => {
                  const x = (i / (HISTORICAL_DATA.length - 1)) * 600;
                  const y = 100 - ((d[coin] - 0.98) * 5000);
                  return `${x},${y}`;
                }).join(' ');
                
                return (
                  <polyline
                    key={coin}
                    points={points}
                    fill="none"
                    stroke={colors[idx]}
                    strokeWidth="2"
                    style={{ transition: 'all 0.5s ease' }}
                  />
                );
              })}
            </svg>
            
            {/* Labels */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>
              {HISTORICAL_DATA.map(d => (
                <span key={d.time}>{d.time}</span>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            {STABLECOINS.map((coin, idx) => {
              const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
              return (
                <div key={coin.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: colors[idx] }} />
                  <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>{coin.symbol}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Risk Analysis */}
        <div className="card" style={{ animationDelay: '0.5s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <Brain size={24} color="#a78bfa" />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
              AI Analysis
            </h2>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
              Risk Assessment for {selectedCoin.symbol}
            </div>
            <div style={{
              fontSize: '3rem',
              fontFamily: 'JetBrains Mono',
              fontWeight: 800,
              color: getRiskColor(selectedCoin.riskScore),
              lineHeight: 1
            }}>
              {selectedCoin.riskScore}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginTop: '0.25rem' }}>
              out of 100
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Liquidity Health</span>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#4ade80' }}>
                  {selectedCoin.reserveHealth}%
                </span>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(51, 65, 85, 0.5)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ width: `${selectedCoin.reserveHealth}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #22c55e)', transition: 'width 1s ease' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Peg Stability</span>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: Math.abs(selectedCoin.pegDeviation) > 0.5 ? '#f87171' : '#4ade80' }}>
                  {(100 - Math.abs(selectedCoin.pegDeviation) * 10).toFixed(1)}%
                </span>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(51, 65, 85, 0.5)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ 
                  width: `${100 - Math.abs(selectedCoin.pegDeviation) * 10}%`, 
                  height: '100%', 
                  background: Math.abs(selectedCoin.pegDeviation) > 0.5 ? 'linear-gradient(90deg, #ef4444, #f87171)' : 'linear-gradient(90deg, #10b981, #22c55e)',
                  transition: 'width 1s ease'
                }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Market Confidence</span>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: '#60a5fa' }}>
                  {(100 - selectedCoin.riskScore * 0.8).toFixed(0)}%
                </span>
              </div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(51, 65, 85, 0.5)', borderRadius: '9999px', overflow: 'hidden' }}>
                <div style={{ width: `${100 - selectedCoin.riskScore * 0.8}%`, height: '100%', background: 'linear-gradient(90deg, #3b82f6, #60a5fa)', transition: 'width 1s ease' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
        {/* Market Stats */}
        <div className="card" style={{ animationDelay: '0.6s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <Database size={20} color="#60a5fa" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>
              Market Stats
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>Market Cap</div>
              <div className="stat-value" style={{ fontSize: '1.25rem' }}>
                {formatCurrency(selectedCoin.marketCap)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>24h Volume</div>
              <div className="stat-value" style={{ fontSize: '1.25rem' }}>
                {formatCurrency(selectedCoin.volume24h)}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>Liquidity</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div className="stat-value" style={{ fontSize: '1.25rem' }}>
                  {formatCurrency(selectedCoin.liquidity)}
                </div>
                <span style={{ 
                  fontSize: '0.875rem', 
                  color: selectedCoin.liquidityChange >= 0 ? '#22c55e' : '#ef4444',
                  fontWeight: 600
                }}>
                  {selectedCoin.liquidityChange >= 0 ? '+' : ''}{selectedCoin.liquidityChange}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts */}
        <div className="card" style={{ animationDelay: '0.7s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <AlertTriangle size={20} color="#f59e0b" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>
              Active Alerts
            </h3>
          </div>

          {selectedCoin.alerts.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {selectedCoin.alerts.map((alert, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'start',
                  gap: '0.75rem',
                  padding: '0.75rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: '8px'
                }}>
                  <AlertCircle size={16} color="#ef4444" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span style={{ fontSize: '0.875rem', color: '#fca5a5', lineHeight: 1.5 }}>
                    {alert}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '2rem 1rem',
              color: '#64748b'
            }}>
              <CheckCircle size={32} color="#22c55e" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontSize: '0.875rem', textAlign: 'center' }}>
                No alerts detected
              </div>
            </div>
          )}
        </div>

        {/* Web3 Status */}
        <div className="card" style={{ animationDelay: '0.8s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <Shield size={20} color="#8b5cf6" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0 }}>
              Web3 Status
            </h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem',
              background: 'rgba(34, 197, 94, 0.1)',
              border: '1px solid rgba(34, 197, 94, 0.2)',
              borderRadius: '8px'
            }}>
              <CheckCircle size={16} color="#22c55e" />
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#4ade80' }}>
                  Blockchain Synced
                </div>
                <div style={{ fontSize: '0.75rem', color: '#86efac', marginTop: '0.125rem' }}>
                  Block #18,234,567
                </div>
              </div>
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem',
              background: 'rgba(34, 197, 94, 0.1)',
              border: '1px solid rgba(34, 197, 94, 0.2)',
              borderRadius: '8px'
            }}>
              <CheckCircle size={16} color="#22c55e" />
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#4ade80' }}>
                  Risk Logs Verified
                </div>
                <div style={{ fontSize: '0.75rem', color: '#86efac', marginTop: '0.125rem' }}>
                  Immutable & transparent
                </div>
              </div>
            </div>

            <div style={{
              fontSize: '0.75rem',
              color: '#64748b',
              padding: '0.75rem',
              background: 'rgba(51, 65, 85, 0.3)',
              borderRadius: '8px',
              fontFamily: 'JetBrains Mono',
              wordBreak: 'break-all'
            }}>
              <div style={{ marginBottom: '0.25rem', color: '#94a3b8' }}>Latest TX:</div>
              0x7a8f...9b2e
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StablecoinDashboard;