"""
SHAP-based Explainable AI for Risk Predictions

Extends RiskPredictor with SHAP explanations for model interpretability.
"""

import shap
import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from .predictor import RiskPredictor

logger = logging.getLogger(__name__)


class ExplainableRiskPredictor(RiskPredictor):
    """
    Risk predictor with SHAP-based explainability.
    
    Provides feature contribution analysis for each prediction.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with SHAP explainers."""
        super().__init__(*args, **kwargs)
        
        logger.info("Initializing SHAP explainers...")
        
        try:
            # XGBoost TreeExplainer
            self.xgb_explainer = shap.TreeExplainer(self.xgb_model)
            logger.info("✅ XGBoost SHAP explainer ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize SHAP: {e}")
            self.xgb_explainer = None
    
    def predict_with_explanation(
        self, 
        engineered_features: Dict[str, float], 
        tcs_score: float
    ) -> Dict:
        """
        Predict with SHAP explanations.
        
        Args:
            engineered_features: 58 features from FeatureEngineer
            tcs_score: Temporal Confidence Score
        
        Returns:
            Prediction dict with added 'explainability' field
        """
        # Get base prediction
        prediction = self.predict(engineered_features, tcs_score)
        
        if 'error' in prediction or self.xgb_explainer is None:
            return prediction
        
        try:
            # Prepare data
            X = pd.DataFrame([engineered_features])
            X = X[self.feature_names]
            
            # Handle missing features
            for col in self.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            
            X_scaled = self.scaler.transform(X)
            
            # Calculate SHAP values
            shap_values = self.xgb_explainer.shap_values(X_scaled)
            
            # Get predicted class
            predicted_class = prediction['models']['xgboost']['predicted_class']
            
            # Extract feature contributions for predicted class
            feature_contributions = shap_values[predicted_class][0]
            
            # Create explanations
            explanations = []
            for i, feature_name in enumerate(self.feature_names):
                contribution = feature_contributions[i]
                feature_value = engineered_features.get(feature_name, 0.0)
                
                explanations.append({
                    'feature': feature_name,
                    'value': float(feature_value),
                    'contribution': float(contribution),
                    'impact': 'positive' if contribution > 0 else 'negative',
                    'explanation': self._get_feature_explanation(feature_name, feature_value, contribution)
                })
            
            # Sort by absolute contribution
            explanations.sort(key=lambda x: abs(x['contribution']), reverse=True)
            
            # Add explainability to prediction
            prediction['explainability'] = {
                'method': 'SHAP (SHapley Additive exPlanations)',
                'base_value': float(self.xgb_explainer.expected_value[predicted_class]),
                'top_features': explanations[:10],  # Top 10 contributors
                'all_features': explanations  # Full list for detailed analysis
            }
            
            logger.debug(f"Generated SHAP explanations with {len(explanations)} features")
            
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            prediction['explainability'] = {
                'error': 'Explanation generation failed',
                'message': str(e)
            }
        
        return prediction
    
    def _get_feature_explanation(self, feature_name: str, value: float, contribution: float) -> str:
        """
        Generate human-readable explanation for feature contribution.
        
        Args:
            feature_name: Name of feature
            value: Feature value
            contribution: SHAP contribution value
        
        Returns:
            Human-readable explanation
        """
        # Feature group explanations
        explanations_map = {
            'peg_distance_abs': f"{'Large' if value > 0.5 else 'Small'} deviation from $1.00 peg {'increases' if contribution > 0 else 'decreases'} risk",
            'volatility_6h': f"{'High' if value > 0.001 else 'Low'} volatility {'indicates' if contribution > 0 else 'reduces'} instability",
            'max_deviation_6h': f"Recent extreme deviation {'signals' if contribution > 0 else 'does not indicate'} stress",
            'correlation_with_btc_24h': f"{'High' if abs(value) > 0.5 else 'Low'} BTC correlation {'increases' if contribution > 0 else 'reduces'} unique risk",
            'btc_price_change_6h': f"BTC {'decline' if value < 0 else 'rise'} {'adds to' if contribution > 0 else 'reduces'} market stress",
            'price_cv_6h': f"{'High' if value > 1 else 'Low'} relative volatility {'increases' if contribution > 0 else 'stabilizes'} risk",
            'extreme_deviation_flag': f"{'Extreme' if value == 1 else 'Normal'} deviation status",
            'volatility_spike': f"{'Volatility spike detected' if value == 1 else 'Normal volatility'}",
            'market_crash_indicator': f"{'Market crash conditions' if value == 1 else 'Stable market conditions'}",
            'time_below_peg_6h': f"{'Prolonged' if value > 12 else 'Brief'} time below peg",
        }
        
        return explanations_map.get(
            feature_name,
            f"{feature_name} = {value:.4f} {'increases' if contribution > 0 else 'decreases'} risk"
        )
    
    def generate_force_plot(
        self, 
        engineered_features: Dict[str, float],
        output_path: str = 'force_plot.html'
    ) -> str:
        """
        Generate SHAP force plot visualization.
        
        Args:
            engineered_features: 58 features
            output_path: Path to save HTML file
        
        Returns:
            Path to generated HTML file
        """
        if self.xgb_explainer is None:
            raise RuntimeError("SHAP explainer not initialized")
        
        try:
            # Prepare data
            X = pd.DataFrame([engineered_features])
            X = X[self.feature_names]
            
            for col in self.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            
            X_scaled = self.scaler.transform(X)
            
            # Calculate SHAP values
            shap_values = self.xgb_explainer.shap_values(X_scaled)
            
            # Get predicted class
            predicted_class = int(self.xgb_model.predict(X_scaled)[0])
            
            # Generate force plot
            shap.force_plot(
                self.xgb_explainer.expected_value[predicted_class],
                shap_values[predicted_class][0],
                X_scaled[0],
                feature_names=self.feature_names,
                matplotlib=False,
                show=False,
                out_name=output_path
            )
            
            logger.info(f"✅ Force plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Force plot generation failed: {e}")
            raise
    
    def get_feature_importance(self) -> List[Dict]:
        """
        Get global feature importance from XGBoost model.
        
        Returns:
            List of dicts with feature names and importance scores
        """
        importance = self.xgb_model.feature_importances_
        
        features = []
        for i, name in enumerate(self.feature_names):
            features.append({
                'feature': name,
                'importance': float(importance[i])
            })
        
        # Sort by importance (descending)
        features.sort(key=lambda x: x['importance'], reverse=True)
        
        return features
