"""
Web3 Logger Integration Client

Sends ML risk predictions to the Rust logger API for on-chain attestation.
"""

import aiohttp
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LoggerClient:
    """
    HTTP client for Web3 logger API.
    
    Sends risk predictions to logger service which:
    1. Stores log in Postgres
    2. Computes hash
    3. Submits to Solana blockchain
    4. Returns transaction signature
    """
    
    def __init__(self, logger_api_url: str = 'http://localhost:8080'):
        """Initialize client with logger API URL."""
        self.base_url = logger_api_url.rstrip('/')
        self.api_version = 'v1'
        logger.info(f"LoggerClient initialized: {self.base_url}")
    
    async def send_risk_prediction(
        self, 
        prediction: Dict, 
        coin: str,
        chain: str = 'ethereum'
    ) -> Optional[str]:
        """
        Send ML risk prediction to logger for attestation.
        
        Args:
            prediction: Prediction dict from ExplainableRiskPredictor
            coin: Coin ticker (USDC, USDT, etc.)
            chain: Chain name
        
        Returns:
            Transaction hash from Solana, or None if failed
        """
        # Determine severity based on risk score
        risk_score = prediction.get('risk_score', 0)
        severity = self._get_severity(risk_score)
        
        # Build log payload
        payload = {
            'event_type': 'ml_risk_prediction',
            'severity': severity,
            'data': {
                'coin': coin,
                'chain': chain,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'risk_score': risk_score,
                'rating': prediction.get('rating'),
                'tcs_score': prediction.get('tcs_score'),
                'models': prediction.get('models', {}),
                'ensemble': prediction.get('ensemble', {}),
                'explainability': {
                    'top_features': prediction.get('explainability', {}).get('top_features', [])[:5]
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/{self.api_version}/logs"
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        tx_hash = data.get('transaction_hash')
                        
                        if tx_hash:
                            logger.info(f"✅ Prediction attested: {coin} @ {risk_score:.1f} → {tx_hash[:8]}...")
                            return tx_hash
                        else:
                            logger.warning(f"⚠️  Prediction logged but no TX hash: {coin}")
                            return None
                    else:
                        error = await response.text()
                        logger.error(f"❌ Logger API error {response.status}: {error}")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Connection error to logger API: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error sending to logger: {e}")
            return None
    
    async def verify_attestation(self, tx_hash: str) -> Optional[Dict]:
        """
        Verify an attestation on Solana.
        
        Args:
            tx_hash: Transaction hash from previous send_risk_prediction call
        
        Returns:
            Verification result dict or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/{self.api_version}/logs/{tx_hash}/verify"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Attestation verified: {tx_hash[:8]}...")
                        return data
                    else:
                        logger.error(f"❌ Verification failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return None
    
    async def get_health(self) -> bool:
        """Check if logger API is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/api/{self.api_version}/health"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    healthy = response.status == 200
                    if healthy:
                        logger.info("✅ Logger API is healthy")
                    else:
                        logger.warning(f"⚠️  Logger API unhealthy: {response.status}")
                    return healthy
                    
        except Exception as e:
            logger.error(f"❌ Logger API health check failed: {e}")
            return False
    
    def _get_severity(self, risk_score: float) -> str:
        """
        Map risk score to log severity.
        
        Only 'warning' and above get attested to blockchain.
        """
        if risk_score >= 80:
            return 'critical'  # Immediate blockchain attestation
        elif risk_score >= 60:
            return 'warning'   # Blockchain attestation
        else:
            return 'info'      # Database only (no attestation)
