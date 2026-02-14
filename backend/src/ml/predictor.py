"""
ML Model Predictor for Stablecoin Risk Assessment

Loads pre-trained models and performs risk prediction with TCS gating.
Uses ensemble of Isolation Forest (anomaly) + XGBoost (classification).
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RiskPredictor:
    """
    ML-based risk prediction system with ensemble models.
    
    Combines:
    - Isolation Forest: Unsupervised anomaly detection
    - XGBoost: Supervised risk classification
    """
    
    def __init__(self, model_dir: str = 'src/data/models'):
        """
        Initialize predictor by loading all model files.
        
        Args:
            model_dir: Directory containing pickle files
        """
        self.model_dir = Path(model_dir)
        logger.info(f"Loading ML models from {self.model_dir}")
        
        # Load models
        try:
            with open(self.model_dir / 'isolation_forest.pkl', 'rb') as f:
                self.iso_forest = pickle.load(f)
            logger.info("✅ Isolation Forest loaded")
            
            with open(self.model_dir / 'xgboost_model.pkl', 'rb') as f:
                self.xgb_model = pickle.load(f)
            logger.info("✅ XGBoost loaded")
            
            with open(self.model_dir / 'scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("✅ Scaler loaded")
            
            with open(self.model_dir / 'feature_names.pkl', 'rb') as f:
                self.feature_names = pickle.load(f)
            logger.info(f"✅ Feature names loaded ({len(self.feature_names)} features)")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
        
        logger.info("✅ All models ready for inference")
    
    def predict(self, engineered_features: Dict[str, float], tcs_score: float) -> Dict:
        """
        Main prediction function with TCS gating.
        
        Args:
            engineered_features: Dict with 58 features from FeatureEngineer
            tcs_score: Temporal Confidence Score (0-1) from TCS calculator
        
        Returns:
            Dict with risk score, rating, model outputs, and metadata
        """
        # TCS Gate: only predict if confidence >= 0.7
        if tcs_score < 0.7:
            return {
                'error': 'Insufficient data confidence',
                'tcs_score': tcs_score,
                'message': 'Wait for blockchain finality before prediction',
                'risk_score': None,
                'rating': 'PENDING'
            }
        
        try:
            # Convert to DataFrame and reorder features
            X = pd.DataFrame([engineered_features])
            X = X[self.feature_names]
            
            # Handle any missing features (fill with 0)
            for col in self.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            
            # Scale features (CRITICAL: models trained on scaled data)
            X_scaled = self.scaler.transform(X)
            
            # Isolation Forest prediction
            iso_score_raw = self.iso_forest.decision_function(X_scaled)[0]
            iso_score = (1 - iso_score_raw) / 2  # Normalize to [0,1]
            iso_score = float(np.clip(iso_score, 0, 1))
            iso_pred = self.iso_forest.predict(X_scaled)[0]
            is_anomaly = (iso_pred == -1)
            
            # XGBoost prediction
            xgb_pred_class = int(self.xgb_model.predict(X_scaled)[0])
            xgb_probs = self.xgb_model.predict_proba(X_scaled)[0]
            xgb_risk_prob = 1 - xgb_probs[0]  # 1 - P(Safe)
            
            # Ensemble risk score (0-100)
            # 40% Isolation Forest + 60% XGBoost
            risk_score = (iso_score * 0.4 + xgb_risk_prob * 0.6) * 100
            
            # Risk rating
            rating, color = self._get_risk_rating(risk_score)
            
            return {
                'risk_score': float(risk_score),
                'rating': rating,
                'color': color,
                'tcs_score': tcs_score,
                'models': {
                    'isolation_forest': {
                        'anomaly_score': iso_score,
                        'is_anomaly': bool(is_anomaly),
                        'weight': 0.4
                    },
                    'xgboost': {
                        'predicted_class': xgb_pred_class,
                        'class_name': ['Safe', 'Warning', 'Critical', 'Collapse'][xgb_pred_class],
                        'probabilities': {
                            'Safe': float(xgb_probs[0]),
                            'Warning': float(xgb_probs[1]),
                            'Critical': float(xgb_probs[2]),
                            'Collapse': float(xgb_probs[3])
                        },
                        'weight': 0.6
                    }
                },
                'ensemble': {
                    'formula': '(ISO * 0.4) + (XGB * 0.6)',
                    'iso_contribution': float(iso_score * 0.4 * 100),
                    'xgb_contribution': float(xgb_risk_prob * 0.6 * 100)
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'error': 'Prediction failed',
                'message': str(e),
                'risk_score': None,
                'rating': 'ERROR'
            }
    
    def _get_risk_rating(self, score: float) -> tuple[str, str]:
        """
        Convert numeric risk score to letter rating and color.
        
        Returns:
            (rating, color) tuple
        """
        if score < 20:
            return 'AAA', 'green'
        elif score < 40:
            return 'AA', 'green'
        elif score < 60:
            return 'A', 'yellow'
        elif score < 80:
            return 'B', 'orange'
        else:
            return 'C', 'red'
    
    def get_model_info(self) -> Dict:
        """Get metadata about loaded models."""
        return {
            'models': {
                'isolation_forest': 'Anomaly detection (unsupervised)',
                'xgboost': 'Multi-class classifier (supervised)'
            },
            'num_features': len(self.feature_names),
            'feature_names': self.feature_names,
            'ensemble_weights': {
                'isolation_forest': 0.4,
                'xgboost': 0.6
            },
            'risk_ratings': {
                'AAA': '0-20 (Minimal risk)',
                'AA': '20-40 (Low risk)',
                'A': '40-60 (Medium risk)',
                'B': '60-80 (High risk)',
                'C': '80-100 (Critical risk)'
            },
            'tcs_threshold': 0.7
        }
