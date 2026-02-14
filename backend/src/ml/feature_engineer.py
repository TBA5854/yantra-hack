"""
Feature Engineering Pipeline for Stablecoin Risk Prediction

Transforms raw price data into 58 engineered features across 9 groups:
1. Peg Deviation Features (10)
2. Price Momentum Features (7)
3. Volatility Features (6)
4. Momentum Indicators (8)
5. Deviation Velocity (4)
6. Statistical Features (8)
7. Temporal Features (4)
8. BTC Context Features (10)
9. Coin Encoding (5)

Based on research-based feature engineering from Terra/Luna crash analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Complete feature engineering pipeline for stablecoin risk prediction.
    
    Maintains rolling 24-hour history buffers for each coin and computes
    58 features from raw price + BTC data.
    """
    
    def __init__(self, window_size: int = 96):
        """
        Initialize feature engineer.
        
        Args:
            window_size: Number of data points to keep (96 = 24h @ 15-min intervals)
        """
        self.window_size = window_size
        
        # Rolling history buffers per coin (24 hours of 15-min data)
        self.history_buffer: Dict[str, deque] = {
            'USDC': deque(maxlen=window_size),
            'USDT': deque(maxlen=window_size),
            'DAI': deque(maxlen=window_size),
            'BUSD': deque(maxlen=window_size),
        }
        
        logger.info(f"FeatureEngineer initialized with window_size={window_size}")
    
    def transform(self, raw_data: Dict) -> Optional<Dict[str, float]]:
        """
        Transform raw data point to 58 engineered features.
        
        Args:
            raw_data: {
                'timestamp': ISO8601 string,
                'coin': 'USDC' | 'USDT' | 'DAI' | 'BUSD',
                'price': float,
                'btc_price': float
            }
        
        Returns:
            Dictionary with 58 features, or None if insufficient data
        """
        coin = raw_data['coin']
        
        # Add to history buffer
        self.history_buffer[coin].append(raw_data)
        
        # Need at least 24 points (6 hours @ 15-min) for meaningful features
        if len(self.history_buffer[coin]) < 24:
            logger.debug(f"Insufficient history for {coin}: {len(self.history_buffer[coin])}/24")
            return None
        
        # Convert to DataFrame for feature calculation
        df = pd.DataFrame(list(self.history_buffer[coin]))
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Calculate all feature groups
        df = self._calculate_peg_features(df)
        df = self._calculate_price_momentum_features(df)
        df = self._calculate_volatility_features(df)
        df = self._calculate_momentum_indicators(df)
        df = self._calculate_deviation_velocity(df)
        df = self._calculate_statistical_features(df)
        df = self._calculate_temporal_features(df)
        df = self._calculate_btc_features(df)
        
        # Get latest row features
        latest = df.iloc[-1]
        
        # Extract feature values (exclude metadata columns)
        feature_cols = [col for col in df.columns 
                       if col not in ['timestamp', 'datetime', 'coin', 'price', 'btc_price']]
        
        features = {col: float(latest[col]) for col in feature_cols}
        
        # Add coin encoding (one-hot)
        for c in ['USDC', 'USDT', 'DAI', 'BUSD', 'UST']:
            features[f'coin_{c}'] = 1.0 if coin == c else 0.0
        
        logger.debug(f"Generated {len(features)} features for {coin}")
        return features
    
    def is_ready(self, coin: str) -> bool:
        """Check if sufficient history available for coin."""
        return len(self.history_buffer.get(coin, [])) >= 24
    
    # ============================================
    # FEATURE GROUP 1: PEG DEVIATION (10 features)
    # ============================================
    
    def _calculate_peg_features(self, df: pd.DataFrame, target_peg: float = 1.0) -> pd.DataFrame:
        """Calculate peg deviation features."""
        # 1. Peg deviation percentage
        df['peg_deviation_pct'] = ((df['price'] - target_peg) / target_peg) * 100
        
        # 2. Squared deviation (amplifies large deviations)
        df['peg_deviation_squared'] = df['peg_deviation_pct'] ** 2
        
        # 3. Absolute distance from peg
        df['peg_distance_abs'] = np.abs(df['peg_deviation_pct'])
        
        # 4. Binary flag: is price below peg?
        df['below_peg'] = (df['price'] < target_peg).astype(int)
        
        # 5. Time spent below peg in last 1 hour (4 points)
        df['time_below_peg_1h'] = df['below_peg'].rolling(window=4, min_periods=1).sum()
        
        # 6. Time spent below peg in last 6 hours (24 points)
        df['time_below_peg_6h'] = df['below_peg'].rolling(window=24, min_periods=1).sum()
        
        return df
    
    # ============================================
    # FEATURE GROUP 2: PRICE MOMENTUM (7 features)
    # ============================================
    
    def _calculate_price_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate price momentum features."""
        # 1. Price change in last 15 minutes (1 period)
        df['price_change_15min'] = df['price'].pct_change(periods=1) * 100
        
        # 2. Price change in last 1 hour (4 periods)
        df['price_change_1h'] = df['price'].pct_change(periods=4) * 100
        
        # 3. Price change in last 3 hours (12 periods)
        df['price_change_3h'] = df['price'].pct_change(periods=12) * 100
        
        # 4. Price change in last 6 hours (24 periods)
        df['price_change_6h'] = df['price'].pct_change(periods=24) * 100
        
        # 5. Price change in last 24 hours (96 periods)
        df['price_change_24h'] = df['price'].pct_change(periods=min(96, len(df))) * 100
        
        # 6. Log return (1 hour)
        df['log_return_1h'] = np.log(df['price'] / df['price'].shift(4))
        
        # 7. Cumulative return (24 hours)
        df['cumulative_return_24h'] = (
            (1 + df['price'].pct_change())
            .rolling(min(96, len(df)))
            .apply(lambda x: np.prod(x) - 1 if len(x) > 0 else 0)
        )
        
        return df
    
    # ============================================
    # FEATURE GROUP 3: VOLATILITY (6 features)
    # ============================================
    
    def _calculate_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility features."""
        # 1. Volatility over 1 hour
        df['volatility_1h'] = df['price'].rolling(window=4, min_periods=2).std()
        
        # 2. Volatility over 6 hours
        df['volatility_6h'] = df['price'].rolling(window=24, min_periods=2).std()
        
        # 3. Volatility over 24 hours
        df['volatility_24h'] = df['price'].rolling(window=min(96, len(df)), min_periods=2).std()
        
        # 4. Volatility ratio (short-term / medium-term)
        df['volatility_ratio_1h_6h'] = df['volatility_1h'] / (df['volatility_6h'] + 1e-8)
        
        # 5. Volatility spike flag
        df['volatility_spike'] = (
            df['volatility_1h'] > df['volatility_24h'].rolling(min(96, len(df))).mean() * 2
        ).astype(int)
        
        # 6. Price range in last 6 hours
        df['price_range_6h'] = (
            df['price'].rolling(24).max() - df['price'].rolling(24).min()
        )
        
        return df
    
    # ============================================
    # FEATURE GROUP 4: MOMENTUM INDICATORS (8 features)
    # ============================================
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical momentum indicators."""
        # 1-3. Simple Moving Averages
        df['sma_1h'] = df['price'].rolling(window=4).mean()
        df['sma_6h'] = df['price'].rolling(window=24).mean()
        df['sma_24h'] = df['price'].rolling(window=min(96, len(df))).mean()
        
        # 4-5. Momentum (distance from average)
        df['momentum_1h'] = df['price'] - df['sma_1h']
        df['momentum_6h'] = df['price'] - df['sma_6h']
        
        # 6-7. Exponential Moving Averages
        df['ema_1h'] = df['price'].ewm(span=4, adjust=False).mean()
        df['ema_6h'] = df['price'].ewm(span=24, adjust=False).mean()
        
        # 8. Moving Average Convergence
        df['ma_convergence'] = df['sma_1h'] - df['sma_6h']
        
        return df
    
    # ============================================
    # FEATURE GROUP 5: DEVIATION VELOCITY (4 features)
    # ============================================
    
    def _calculate_deviation_velocity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate rate of change in peg deviation."""
        # 1. Velocity: How fast is deviation changing? (1 hour)
        df['peg_deviation_velocity_1h'] = df['peg_deviation_pct'].diff(periods=4)
        
        # 2. Acceleration: How fast is velocity changing?
        df['peg_deviation_acceleration'] = df['peg_deviation_velocity_1h'].diff(periods=4)
        
        # 3. Maximum deviation in last 6 hours
        df['max_deviation_6h'] = df['peg_distance_abs'].rolling(24).max()
        
        # 4. Maximum deviation in last 24 hours
        df['max_deviation_24h'] = df['peg_distance_abs'].rolling(min(96, len(df))).max()
        
        return df
    
    # ============================================
    # FEATURE GROUP 6: STATISTICAL (8 features)
    # ============================================
    
    def _calculate_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate statistical measures."""
        # Helper: rolling statistics
        rolling_mean = df['price'].rolling(min(96, len(df))).mean()
        rolling_std = df['price'].rolling(min(96, len(df))).std()
        
        # 1. Z-score (how many std deviations from mean?)
        df['price_zscore'] = (df['price'] - rolling_mean) / (rolling_std + 1e-8)
        
        # 2. Coefficient of Variation (6 hours)
        df['price_cv_6h'] = (df['volatility_6h'] / df['sma_6h']) * 100
        
        # 3. Skewness (24 hours)
        df['price_skewness_24h'] = df['price'].rolling(min(96, len(df))).skew()
        
        # 4. Kurtosis (24 hours)
        df['price_kurtosis_24h'] = df['price'].rolling(min(96, len(df))).kurt()
        
        # 5. Extreme deviation flag (> 0.5% = 50 bps)
        df['extreme_deviation_flag'] = (df['peg_distance_abs'] > 0.5).astype(int)
        
        # 6. Ratio of extreme deviations in last 6h
        df['extreme_deviation_ratio_6h'] = df['extreme_deviation_flag'].rolling(24).mean()
        
        return df
    
    # ============================================
    # FEATURE GROUP 7: TEMPORAL (4 features)
    # ============================================
    
    def _calculate_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract time-based features."""
        # 1. Hour of day (0-23)
        df['hour_of_day'] = df['datetime'].dt.hour
        
        # 2. Day of week (0=Monday, 6=Sunday)
        df['day_of_week'] = df['datetime'].dt.dayofweek
        
        # 3. Is weekend? (Saturday/Sunday)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # 4. Minutes elapsed since start
        df['minutes_elapsed'] = (
            df['datetime'] - df['datetime'].min()
        ).dt.total_seconds() / 60
        
        return df
    
    # ============================================
    # FEATURE GROUP 8: BTC CONTEXT (10 features)
    # ============================================
    
    def _calculate_btc_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bitcoin market context features."""
        # 1. BTC price (already in data)
        
        # 2. BTC price change (1 hour)
        df['btc_price_change_1h'] = df['btc_price'].pct_change(4) * 100
        
        # 3. BTC price change (6 hours)
        df['btc_price_change_6h'] = df['btc_price'].pct_change(24) * 100
        
        # 4. BTC volatility (6 hours)
        df['btc_volatility_6h'] = df['btc_price'].rolling(24).std()
        
        # 5. BTC volatility (24 hours)
        df['btc_volatility_24h'] = df['btc_price'].rolling(min(96, len(df))).std()
        
        # 6. Correlation between stablecoin and BTC (24h)
        df['correlation_with_btc_24h'] = (
            df['price'].rolling(min(96, len(df))).corr(df['btc_price'])
        )
        
        # 7. Market crash indicator
        df['market_crash_indicator'] = (
            (df['btc_price_change_6h'] < -5) &  # BTC down >5%
            (df['peg_distance_abs'] > 0.5)       # Stablecoin depegging
        ).astype(int)
        
        # 8. BTC volatility ratio
        df['btc_volatility_ratio'] = (
            df['btc_volatility_6h'] / (df['btc_volatility_24h'] + 1e-8)
        )
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of all 58 feature names in order."""
        return [
            # Peg features (10)
            'peg_deviation_pct', 'peg_deviation_squared', 'peg_distance_abs',
            'below_peg', 'time_below_peg_1h', 'time_below_peg_6h',
            
            # Price momentum (7)
            'price_change_15min', 'price_change_1h', 'price_change_3h',
            'price_change_6h', 'price_change_24h', 'log_return_1h',
            'cumulative_return_24h',
            
            # Volatility (6)
            'volatility_1h', 'volatility_6h', 'volatility_24h',
            'volatility_ratio_1h_6h', 'volatility_spike', 'price_range_6h',
            
            # Momentum indicators (8)
            'sma_1h', 'sma_6h', 'sma_24h', 'momentum_1h', 'momentum_6h',
            'ema_1h', 'ema_6h', 'ma_convergence',
            
            # Deviation velocity (4)
            'peg_deviation_velocity_1h', 'peg_deviation_acceleration',
            'max_deviation_6h', 'max_deviation_24h',
            
            # Statistical (8)
            'price_zscore', 'price_cv_6h', 'price_skewness_24h',
            'price_kurtosis_24h', 'extreme_deviation_flag',
            'extreme_deviation_ratio_6h',
            
            # Temporal (4)
            'hour_of_day', 'day_of_week', 'is_weekend', 'minutes_elapsed',
            
            # BTC context (10)
            'btc_price_change_1h', 'btc_price_change_6h',
            'btc_volatility_6h', 'btc_volatility_24h',
            'correlation_with_btc_24h', 'market_crash_indicator',
            'btc_volatility_ratio',
            
            # Coin encoding (5)
            'coin_USDC', 'coin_USDT', 'coin_DAI', 'coin_BUSD', 'coin_UST'
        ]
