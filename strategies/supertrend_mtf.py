"""
Supertrend Multi-Timeframe Strategy
Based on ATR-based Supertrend indicator
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.strategies import SUPERTREND_CONFIG


class SupertrendStrategy:
    def __init__(self, atr_period=None, multiplier=None):
        self.atr_period = atr_period or SUPERTREND_CONFIG['atr_period']
        self.multiplier = multiplier or SUPERTREND_CONFIG['multiplier']

    def calculate_atr(self, df):
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean()

        return atr

    def calculate_supertrend(self, df):
        """
        Calculate Supertrend indicator

        Returns:
            int: 1 for uptrend, -1 for downtrend
        """
        if df is None or len(df) < self.atr_period + 1:
            return 0

        df = df.copy()

        # Calculate ATR
        atr = self.calculate_atr(df)

        # Calculate basic bands
        hl_avg = (df['high'] + df['low']) / 2
        upper_band = hl_avg + (self.multiplier * atr)
        lower_band = hl_avg - (self.multiplier * atr)

        # Initialize supertrend
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)

        # First value
        supertrend.iloc[0] = lower_band.iloc[0]
        direction.iloc[0] = 1

        for i in range(1, len(df)):
            # Current close
            curr_close = df['close'].iloc[i]
            prev_close = df['close'].iloc[i-1]

            # Update bands
            if curr_close > upper_band.iloc[i-1]:
                direction.iloc[i] = 1
            elif curr_close < lower_band.iloc[i-1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i-1]

                # Adjust bands if needed
                if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i-1]:
                    lower_band.iloc[i] = lower_band.iloc[i-1]
                if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i-1]:
                    upper_band.iloc[i] = upper_band.iloc[i-1]

            # Set supertrend value
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]

        # Return latest trend direction
        return int(direction.iloc[-1])

    def analyze_timeframes(self, data_dict):
        """
        Analyze multiple timeframes

        Args:
            data_dict (dict): Dictionary of {timeframe: DataFrame}

        Returns:
            dict: Results with trend per timeframe and overall score
        """
        results = {}
        score = 0

        timeframes = ['M5', 'M15', 'M30', 'H1', 'H4', 'D']

        for tf in timeframes:
            if tf in data_dict and data_dict[tf] is not None:
                trend = self.calculate_supertrend(data_dict[tf])
                results[tf] = trend
                score += trend
            else:
                results[tf] = 0

        results['score'] = score

        # Determine overall trend
        if score >= 5:
            results['trend'] = 'STRONG UP'
        elif score >= 3:
            results['trend'] = 'UP'
        elif score <= -5:
            results['trend'] = 'STRONG DOWN'
        elif score <= -3:
            results['trend'] = 'DOWN'
        else:
            results['trend'] = 'MIXED'

        return results


if __name__ == "__main__":
    # Test with sample data
    print("Testing Supertrend Strategy...")

    # Create sample OHLC data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    np.random.seed(42)

    sample_data = pd.DataFrame({
        'open': 1.1000 + np.random.randn(100).cumsum() * 0.001,
        'high': 1.1000 + np.random.randn(100).cumsum() * 0.001 + 0.0005,
        'low': 1.1000 + np.random.randn(100).cumsum() * 0.001 - 0.0005,
        'close': 1.1000 + np.random.randn(100).cumsum() * 0.001,
        'volume': np.random.randint(1000, 5000, 100)
    }, index=dates)

    strategy = SupertrendStrategy()
    trend = strategy.calculate_supertrend(sample_data)

    print(f"[OK] Supertrend calculated: {trend}")
    print(f"Trend: {'UP' if trend > 0 else 'DOWN'}")
