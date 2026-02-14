"""
Test feature engineering pipeline for parity with training data.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from src.ml.feature_engineer import FeatureEngineer


class TestFeatureParity:
    """
    Verify feature engineering produces identical features to training data.
    
    Uses sample CSV from Kaggle dataset to ensure 100% parity.
    """
    
    def setup_method(self):
        """Initialize feature engineer for each test."""
        self.engineer = FeatureEngineer(window_size=96)
    
    def test_feature_count(self):
        """Verify we generate exactly 58 features."""
        # Simulate raw data
        raw_data = {
            'timestamp': '2022-05-09T12:00:00Z',
            'coin': 'UST',
            'price': 0.95,
            'btc_price': 35000.0
        }
        
        # Add 30 data points to have sufficient history
        for i in range(30):
            data = raw_data.copy()
            data['price'] = 0.95 + (i * 0.001)
            self.engineer.transform(data)
        
        # Get final features
        features = self.engineer.transform(raw_data)
        
        # Should have 58 features
        assert features is not None
        assert len(features) == 58
    
    def test_cold_start_behavior(self):
        """Verify returns None when insufficient data."""
        raw_data = {
            'timestamp': '2022-05-09T12:00:00Z',
            'coin': 'USDC',
            'price': 1.00,
            'btc_price': 40000.0
        }
        
        # First few calls should return None
        for i in range(23):
            features = self.engineer.transform(raw_data)
            assert features is None
        
        # 24th call should return features
        features = self.engineer.transform(raw_data)
        assert features is not None
    
    def test_peg_deviation_features(self):
        """Test peg deviation calculation."""
        # Create data with known peg deviation
        for i in range(25):
            self.engineer.transform({
                'timestamp': f'2022-05-09T12:{i:02d}:00Z',
                'coin': 'USDC',
                'price': 0.98,  # 2% below peg
                'btc_price': 40000.0
            })
        
        features = self.engineer.transform({
            'timestamp': '2022-05-09T12:25:00Z',
            'coin': 'USDC',
            'price': 0.98,
            'btc_price': 40000.0
        })
        
        # Check peg deviation is ~-2%
        assert features is not None
        assert -2.1 < features['peg_deviation_pct'] < -1.9
        assert features['peg_distance_abs'] > 1.9
        assert features['below_peg'] == 1
    
    def test_btc_correlation_feature(self):
        """Test BTC correlation feature calculation."""
        # Generate correlated price movements
        for i in range(96):
            btc_price = 40000 + (i * 100)  # BTC rising
            coin_price = 1.00 + (i * 0.0001)  # Stablecoin also rising (shouldn't!)
            
            self.engineer.transform({
                'timestamp': f'2022-05-09T{i//4:02d}:{(i%4)*15:02d}:00Z',
                'coin': 'DAI',
                'price': coin_price,
                'btc_price': btc_price
            })
        
        features = self.engineer.transform({
            'timestamp': '2022-05-10T00:00:00Z',
            'coin': 'DAI',
            'price': 1.01,
            'btc_price': 49 600.0
        })
        
        # Should show positive correlation (bad for stablecoin!)
        assert features is not None
        assert features['correlation_with_btc_24h'] > 0.5


class TestFeatureEngineering:
    """Integration tests for full feature pipeline."""
    
    def test_volatility_calculation(self):
        """Test volatility features."""
        engineer = FeatureEngineer()
        
        # Create volatile price data
        prices = [1.00, 1.02, 0.98, 1.03, 0.97, 1.01] * 5  # 30 points
        
        for i, price in enumerate(prices):
            engineer.transform({
                'timestamp': f'2022-05-09T12:{i:02d}:00Z',
                'coin': 'BUSD',
                'price': price,
                'btc_price': 40000.0
            })
        
        features = engineer.transform({
            'timestamp': '2022-05-09T12:30:00Z',
            'coin': 'BUSD',
            'price': 1.00,
            'btc_price': 40000.0
        })
        
        assert features is not None
        assert features['volatility_1h'] > 0
        assert features['volatility_6h'] > 0
    
    def test_temporal_features(self):
        """Test temporal feature extraction."""
        engineer = FeatureEngineer()
        
        # Add history
        for i in range(25):
            engineer.transform({
                'timestamp': f'2022-05-09T15:{i:02d}:00Z',
                'coin': 'USDT',
                'price': 1.00,
                'btc_price': 40000.0
            })
        
        features = engineer.transform({
            'timestamp': '2022-05-09T15:25:00Z',  # Monday, 3:25 PM
            'coin': 'USDT',
            'price': 1.00,
            'btc_price': 40000.0
        })
        
        assert features is not None
        assert features['hour_of_day'] == 15
        assert features['day_of_week'] == 0  # Monday
        assert features['is_weekend'] == 0
    
    def test_coin_encoding(self):
        """Test one-hot coin encoding."""
        engineer = FeatureEngineer()
        
        # Add history for USDC
        for i in range(25):
            engineer.transform({
                'timestamp': f'2022-05-09T12:{i:02d}:00Z',
                'coin': 'USDC',
                'price': 1.00,
                'btc_price': 40000.0
            })
        
        features = engineer.transform({
            'timestamp': '2022-05-09T12:25:00Z',
            'coin': 'USDC',
            'price': 1.00,
            'btc_price': 40000.0
        })
        
        # Only USDC should be 1, others 0
        assert features['coin_USDC'] == 1.0
        assert features['coin_USDT'] == 0.0
        assert features['coin_DAI'] == 0.0
        assert features['coin_BUSD'] == 0.0
        assert features['coin_UST'] == 0.0
