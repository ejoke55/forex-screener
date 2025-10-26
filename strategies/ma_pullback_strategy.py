"""
MA Pullback Strategy for V3
All 3 MAs aligned in one direction, then look for pullback opportunities
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.strategies import MA_PULLBACK_CONFIG


class MAPullbackStrategy:
    def __init__(self, fast_ma=None, medium_ma=None, slow_ma=None):
        self.fast_ma = fast_ma or MA_PULLBACK_CONFIG['fast_ma']
        self.medium_ma = medium_ma or MA_PULLBACK_CONFIG['medium_ma']
        self.slow_ma = slow_ma or MA_PULLBACK_CONFIG['slow_ma']
        self.pullback_threshold = MA_PULLBACK_CONFIG['pullback_threshold']
        self.min_alignment_bars = MA_PULLBACK_CONFIG['min_alignment_bars']

    def calculate_sma(self, df, period):
        """Calculate Simple Moving Average"""
        return df['close'].rolling(window=period).mean()

    def check_ma_alignment(self, df):
        """
        Check if all MAs are aligned in one direction

        Returns:
            tuple: (alignment, bars_aligned)
                alignment: 1 for bullish, -1 for bearish, 0 for no alignment
                bars_aligned: number of consecutive bars with alignment
        """
        if df is None or len(df) < self.slow_ma + self.min_alignment_bars:
            return 0, 0

        df = df.copy()

        # Calculate MAs
        fast = self.calculate_sma(df, self.fast_ma)
        medium = self.calculate_sma(df, self.medium_ma)
        slow = self.calculate_sma(df, self.slow_ma)

        # Check current alignment
        fast_val = fast.iloc[-1]
        medium_val = medium.iloc[-1]
        slow_val = slow.iloc[-1]

        current_alignment = 0
        if fast_val > medium_val > slow_val:
            current_alignment = 1  # Bullish alignment
        elif fast_val < medium_val < slow_val:
            current_alignment = -1  # Bearish alignment

        if current_alignment == 0:
            return 0, 0

        # Count consecutive bars with this alignment
        bars_aligned = 0
        for i in range(len(df) - 1, len(df) - 21, -1):  # Check last 20 bars
            if i < self.slow_ma:
                break

            f_val = fast.iloc[i]
            m_val = medium.iloc[i]
            s_val = slow.iloc[i]

            if current_alignment == 1 and f_val > m_val > s_val:
                bars_aligned += 1
            elif current_alignment == -1 and f_val < m_val < s_val:
                bars_aligned += 1
            else:
                break

        return current_alignment, bars_aligned

    def detect_pullback(self, df):
        """
        Detect pullback to MA after trend alignment

        Returns:
            tuple: (signal, pullback_type, strength)
                signal: 1 for buy pullback, -1 for sell pullback, 0 for none
                pullback_type: 'TO_20MA', 'TO_50MA', 'TO_200MA', or 'NONE'
                strength: 0-100 score
        """
        if df is None or len(df) < self.slow_ma:
            return 0, 'NONE', 0

        df = df.copy()

        # Check MA alignment first
        alignment, bars_aligned = self.check_ma_alignment(df)

        if alignment == 0 or bars_aligned < self.min_alignment_bars:
            return 0, 'NONE', 0

        # Calculate MAs
        fast = self.calculate_sma(df, self.fast_ma)
        medium = self.calculate_sma(df, self.medium_ma)
        slow = self.calculate_sma(df, self.slow_ma)

        # Current values
        price_curr = df['close'].iloc[-1]
        fast_val = fast.iloc[-1]
        medium_val = medium.iloc[-1]
        slow_val = slow.iloc[-1]

        # Check for pullback to each MA
        signal = 0
        pullback_type = 'NONE'
        strength = 0

        if alignment == 1:  # Bullish trend
            # Look for price pulling back to MAs (buying opportunity)
            # Check distance from MAs
            dist_to_fast = ((price_curr - fast_val) / fast_val) * 100
            dist_to_medium = ((price_curr - medium_val) / medium_val) * 100
            dist_to_slow = ((price_curr - slow_val) / slow_val) * 100

            # Pullback to 20 MA (strongest signal)
            if -0.2 <= dist_to_fast <= 0.2:
                signal = 1
                pullback_type = 'TO_20MA'
                strength = 90 if bars_aligned >= 5 else 80

            # Pullback to 50 MA (good signal)
            elif -0.2 <= dist_to_medium <= 0.2:
                signal = 1
                pullback_type = 'TO_50MA'
                strength = 80 if bars_aligned >= 5 else 70

            # Pullback to 200 MA (long-term support)
            elif -0.3 <= dist_to_slow <= 0.3:
                signal = 1
                pullback_type = 'TO_200MA'
                strength = 70 if bars_aligned >= 5 else 60

        elif alignment == -1:  # Bearish trend
            # Look for price pulling back to MAs (selling opportunity)
            dist_to_fast = ((price_curr - fast_val) / fast_val) * 100
            dist_to_medium = ((price_curr - medium_val) / medium_val) * 100
            dist_to_slow = ((price_curr - slow_val) / slow_val) * 100

            # Pullback to 20 MA (strongest signal)
            if -0.2 <= dist_to_fast <= 0.2:
                signal = -1
                pullback_type = 'TO_20MA'
                strength = 90 if bars_aligned >= 5 else 80

            # Pullback to 50 MA (good signal)
            elif -0.2 <= dist_to_medium <= 0.2:
                signal = -1
                pullback_type = 'TO_50MA'
                strength = 80 if bars_aligned >= 5 else 70

            # Pullback to 200 MA (long-term resistance)
            elif -0.3 <= dist_to_slow <= 0.3:
                signal = -1
                pullback_type = 'TO_200MA'
                strength = 70 if bars_aligned >= 5 else 60

        return signal, pullback_type, strength

    def analyze_timeframes(self, data_dict):
        """
        Analyze multiple timeframes for pullback opportunities

        Args:
            data_dict (dict): Dictionary of {timeframe: DataFrame}

        Returns:
            dict: Results with pullback signals
        """
        results = {}
        score = 0
        pullback_detected = False

        timeframes = ['M5', 'M15', 'H1', 'H4', 'D']

        for tf in timeframes:
            if tf in data_dict and data_dict[tf] is not None:
                # Check for pullback
                signal, pullback_type, strength = self.detect_pullback(data_dict[tf])

                if signal != 0:
                    pullback_detected = True

                results[tf] = signal
                results[f'{tf}_pullback'] = pullback_type
                results[f'{tf}_strength'] = strength

                # Add to score (weighted by strength)
                score += signal * (strength / 100)
            else:
                results[tf] = 0
                results[f'{tf}_pullback'] = 'NONE'
                results[f'{tf}_strength'] = 0

        results['score'] = int(score)

        # Determine overall signal
        if pullback_detected:
            if score >= 3:
                results['overall'] = 'STRONG BUY (PULLBACK)'
            elif score >= 1.5:
                results['overall'] = 'BUY (PULLBACK)'
            elif score <= -3:
                results['overall'] = 'STRONG SELL (PULLBACK)'
            elif score <= -1.5:
                results['overall'] = 'SELL (PULLBACK)'
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

        results['pullback_detected'] = pullback_detected

        return results


if __name__ == "__main__":
    # Test with sample data
    print("Testing MA Pullback Strategy...")

    # Create sample OHLC data with trend and pullback
    dates = pd.date_range(start='2024-01-01', periods=300, freq='H')
    np.random.seed(42)

    # Create uptrend with pullback
    price_trend = np.linspace(1.0800, 1.0900, 300)
    # Add a pullback in the middle
    pullback = np.zeros(300)
    pullback[250:270] = -0.0020  # Pullback period

    sample_data = pd.DataFrame({
        'open': price_trend + pullback + np.random.randn(300) * 0.0003,
        'high': price_trend + pullback + np.random.randn(300) * 0.0003 + 0.0005,
        'low': price_trend + pullback + np.random.randn(300) * 0.0003 - 0.0005,
        'close': price_trend + pullback + np.random.randn(300) * 0.0003,
        'volume': np.random.randint(1000, 5000, 300)
    }, index=dates)

    strategy = MAPullbackStrategy()
    signal, pullback_type, strength = strategy.detect_pullback(sample_data)

    print(f"[OK] Pullback signal: {signal}")
    print(f"Pullback Type: {pullback_type}")
    print(f"Strength: {strength}%")

    # Check alignment
    alignment, bars = strategy.check_ma_alignment(sample_data)
    print(f"MA Alignment: {'BULLISH' if alignment > 0 else 'BEARISH' if alignment < 0 else 'NONE'}")
    print(f"Bars Aligned: {bars}")
