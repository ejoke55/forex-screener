"""
MA Cross Strategy for V3
Focused on 20/50 SMA crossovers with 200 SMA confirmation
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.strategies import MA_CROSS_CONFIG


class MACrossStrategy:
    def __init__(self, fast_ma=None, slow_ma=None, confirm_ma=None):
        self.fast_ma = fast_ma or MA_CROSS_CONFIG['fast_ma']
        self.slow_ma = slow_ma or MA_CROSS_CONFIG['slow_ma']
        self.confirm_ma = confirm_ma or MA_CROSS_CONFIG['confirm_ma']
        self.min_separation = MA_CROSS_CONFIG['min_separation']

    def calculate_sma(self, df, period):
        """Calculate Simple Moving Average"""
        return df['close'].rolling(window=period).mean()

    def detect_cross(self, df):
        """
        Detect MA crossover signals

        Returns:
            tuple: (signal, cross_type, strength)
                signal: 1 for bullish cross, -1 for bearish cross, 0 for no cross
                cross_type: 'GOLDEN', 'DEATH', or 'NONE'
                strength: 0-100 score based on trend confirmation
        """
        if df is None or len(df) < self.confirm_ma:
            return 0, 'NONE', 0

        df = df.copy()

        # Calculate MAs
        fast = self.calculate_sma(df, self.fast_ma)
        slow = self.calculate_sma(df, self.slow_ma)
        confirm = self.calculate_sma(df, self.confirm_ma)

        # Current and previous values
        fast_curr = fast.iloc[-1]
        fast_prev = fast.iloc[-2]
        slow_curr = slow.iloc[-1]
        slow_prev = slow.iloc[-2]
        confirm_curr = confirm.iloc[-1]
        price_curr = df['close'].iloc[-1]

        # Check for crossover
        signal = 0
        cross_type = 'NONE'
        strength = 0

        # Bullish cross (Golden Cross): fast crosses above slow
        if fast_prev <= slow_prev and fast_curr > slow_curr:
            if abs(fast_curr - slow_curr) >= self.min_separation:
                signal = 1
                cross_type = 'GOLDEN'

                # Calculate strength based on 200 SMA confirmation
                if price_curr > confirm_curr and fast_curr > confirm_curr:
                    strength = 90  # Strong signal with trend confirmation
                elif price_curr > confirm_curr:
                    strength = 70  # Good signal
                else:
                    strength = 50  # Weak signal (counter-trend)

        # Bearish cross (Death Cross): fast crosses below slow
        elif fast_prev >= slow_prev and fast_curr < slow_curr:
            if abs(fast_curr - slow_curr) >= self.min_separation:
                signal = -1
                cross_type = 'DEATH'

                # Calculate strength based on 200 SMA confirmation
                if price_curr < confirm_curr and fast_curr < confirm_curr:
                    strength = 90  # Strong signal with trend confirmation
                elif price_curr < confirm_curr:
                    strength = 70  # Good signal
                else:
                    strength = 50  # Weak signal (counter-trend)

        return signal, cross_type, strength

    def check_ongoing_trend(self, df):
        """Check if MAs are in trending alignment (not crossing, but aligned)"""
        if df is None or len(df) < self.confirm_ma:
            return 0, 0

        df = df.copy()

        # Calculate MAs
        fast = self.calculate_sma(df, self.fast_ma)
        slow = self.calculate_sma(df, self.slow_ma)
        confirm = self.calculate_sma(df, self.confirm_ma)

        fast_val = fast.iloc[-1]
        slow_val = slow.iloc[-1]
        confirm_val = confirm.iloc[-1]

        # Check alignment
        if fast_val > slow_val > confirm_val:
            # Strong uptrend
            return 1, 80
        elif fast_val < slow_val < confirm_val:
            # Strong downtrend
            return -1, 80
        elif fast_val > slow_val and slow_val > confirm_val:
            # Moderate uptrend
            return 1, 60
        elif fast_val < slow_val and slow_val < confirm_val:
            # Moderate downtrend
            return -1, 60
        else:
            return 0, 0

    def analyze_timeframes(self, data_dict):
        """
        Analyze multiple timeframes for MA crosses

        Args:
            data_dict (dict): Dictionary of {timeframe: DataFrame}

        Returns:
            dict: Results with cross signals and trends
        """
        results = {}
        score = 0
        cross_detected = False

        timeframes = ['M5', 'M15', 'H1', 'H4', 'D']

        for tf in timeframes:
            if tf in data_dict and data_dict[tf] is not None:
                # Check for cross
                signal, cross_type, strength = self.detect_cross(data_dict[tf])

                if signal != 0:
                    cross_detected = True
                    results[f'{tf}_cross'] = cross_type
                    results[f'{tf}_strength'] = strength
                    score += signal * (strength / 100)  # Weight by strength
                else:
                    # Check ongoing trend
                    trend_signal, trend_strength = self.check_ongoing_trend(data_dict[tf])
                    results[f'{tf}_cross'] = 'ALIGNED' if trend_signal != 0 else 'NONE'
                    results[f'{tf}_strength'] = trend_strength
                    score += trend_signal * (trend_strength / 100)

                results[tf] = signal if signal != 0 else (1 if results[f'{tf}_cross'] == 'ALIGNED' and trend_signal > 0 else -1 if results[f'{tf}_cross'] == 'ALIGNED' else 0)
            else:
                results[tf] = 0
                results[f'{tf}_cross'] = 'NONE'
                results[f'{tf}_strength'] = 0

        results['score'] = int(score)

        # Determine overall signal
        if cross_detected:
            if score >= 3:
                results['overall'] = 'STRONG BUY (CROSS)'
            elif score >= 1.5:
                results['overall'] = 'BUY (CROSS)'
            elif score <= -3:
                results['overall'] = 'STRONG SELL (CROSS)'
            elif score <= -1.5:
                results['overall'] = 'SELL (CROSS)'
            else:
                results['overall'] = 'NEUTRAL'
        else:
            if score >= 3:
                results['overall'] = 'STRONG BUY (TREND)'
            elif score >= 1.5:
                results['overall'] = 'BUY (TREND)'
            elif score <= -3:
                results['overall'] = 'STRONG SELL (TREND)'
            elif score <= -1.5:
                results['overall'] = 'SELL (TREND)'
            else:
                results['overall'] = 'NEUTRAL'

        results['cross_detected'] = cross_detected

        return results


if __name__ == "__main__":
    # Test with sample data
    print("Testing MA Cross Strategy...")

    # Create sample OHLC data with a crossover
    dates = pd.date_range(start='2024-01-01', periods=300, freq='H')
    np.random.seed(42)

    # Create data that will produce a golden cross
    price_data = np.concatenate([
        np.linspace(1.0800, 1.0850, 150),  # Downtrend
        np.linspace(1.0850, 1.0950, 150),  # Uptrend (causes cross)
    ])
    noise = np.random.randn(300) * 0.0003

    sample_data = pd.DataFrame({
        'open': price_data + noise,
        'high': price_data + noise + 0.0005,
        'low': price_data + noise - 0.0005,
        'close': price_data + noise,
        'volume': np.random.randint(1000, 5000, 300)
    }, index=dates)

    strategy = MACrossStrategy()
    signal, cross_type, strength = strategy.detect_cross(sample_data)

    print(f"[OK] MA Cross signal: {signal}")
    print(f"Cross Type: {cross_type}")
    print(f"Strength: {strength}%")
