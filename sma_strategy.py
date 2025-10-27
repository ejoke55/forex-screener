"""
SMMA (Smoothed Moving Average) Multi-Timeframe Strategy for V3
Using 20, 50, 200 Smoothed Moving Averages (SMMA/RMA)
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.strategies import SMA_CONFIG


class SMAStrategy:
    def __init__(self, fast_sma=None, medium_sma=None, slow_sma=None, use_adx=None, adx_period=None, adx_strong=None):
        self.fast_sma = fast_sma or SMA_CONFIG['fast_sma']
        self.medium_sma = medium_sma or SMA_CONFIG['medium_sma']
        self.slow_sma = slow_sma or SMA_CONFIG['slow_sma']
        self.use_adx = use_adx if use_adx is not None else SMA_CONFIG['use_adx']
        self.adx_period = adx_period or SMA_CONFIG['adx_period']
        self.adx_strong = adx_strong or SMA_CONFIG['adx_strong']

    def calculate_sma(self, df, period):
        """Calculate Smoothed Moving Average (SMMA/RMA)

        SMMA formula:
        - First value: Simple average of first N values
        - Subsequent: SMMA = (SMMA_prev * (N-1) + Current_Price) / N

        This provides smoother trends than SMA, similar to Wilder's smoothing.
        """
        close = df['close']
        smma = pd.Series(index=close.index, dtype=float)

        # First SMMA value is simple average of first N values
        smma.iloc[period - 1] = close.iloc[:period].mean()

        # Calculate subsequent SMMA values recursively
        for i in range(period, len(close)):
            smma.iloc[i] = (smma.iloc[i - 1] * (period - 1) + close.iloc[i]) / period

        return smma

    def calculate_adx(self, df, period=14):
        """Calculate ADX (Average Directional Index)"""
        if df is None or len(df) < period + 1:
            return None

        high = df['high']
        low = df['low']
        close = df['close']

        # Calculate +DM and -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Smooth TR, +DM, -DM
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    def calculate_sma_trend(self, df):
        """
        Calculate SMMA trend based on alignment

        Returns:
            tuple: (trend, adx_strength, adx_val)
                trend: 1 for uptrend, -1 for downtrend, 0 for mixed
                adx_strength: 'STRONG', 'MODERATE', 'WEAK', or 'N/A'
                adx_val: ADX numeric value or None
        """
        if df is None or len(df) < self.slow_sma:
            return 0, 'N/A', None

        df = df.copy()

        # Calculate SMMAs (20, 50, 200 Smoothed Moving Averages)
        sma_fast = self.calculate_sma(df, self.fast_sma)
        sma_medium = self.calculate_sma(df, self.medium_sma)
        sma_slow = self.calculate_sma(df, self.slow_sma)

        # Get latest values
        fast_val = sma_fast.iloc[-1]
        medium_val = sma_medium.iloc[-1]
        slow_val = sma_slow.iloc[-1]
        current_price = df['close'].iloc[-1]

        # Check alignment
        if fast_val > medium_val > slow_val:
            trend = 1  # Uptrend
        elif fast_val < medium_val < slow_val:
            trend = -1  # Downtrend
        else:
            trend = 0  # Mixed

        # ADX filter (optional)
        adx_strength = 'N/A'
        adx_val = None
        if self.use_adx:
            adx = self.calculate_adx(df, self.adx_period)
            if adx is not None:
                adx_val = adx.iloc[-1]
                if adx_val >= self.adx_strong:
                    adx_strength = 'STRONG'
                elif adx_val >= SMA_CONFIG['adx_weak']:
                    adx_strength = 'MODERATE'
                else:
                    adx_strength = 'WEAK'

        return trend, adx_strength, adx_val

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
        adx_values = []

        timeframes = ['M5', 'M15', 'H1', 'H4', 'D']

        for tf in timeframes:
            if tf in data_dict and data_dict[tf] is not None:
                trend, adx_strength, adx_val = self.calculate_sma_trend(data_dict[tf])
                results[tf] = trend
                results[f'{tf}_adx'] = adx_strength
                results[f'{tf}_adx_value'] = adx_val if adx_val is not None else 0
                score += trend

                if adx_strength != 'N/A':
                    adx_values.append(adx_strength)
            else:
                results[tf] = 0
                results[f'{tf}_adx'] = 'N/A'
                results[f'{tf}_adx_value'] = 0

        results['score'] = score

        # Determine overall trend
        if score >= 4:
            results['overall'] = 'STRONG BUY'
        elif score >= 3:
            results['overall'] = 'BUY'
        elif score <= -4:
            results['overall'] = 'STRONG SELL'
        elif score <= -3:
            results['overall'] = 'SELL'
        else:
            results['overall'] = 'NEUTRAL'

        # Overall strength
        if adx_values:
            strong_count = adx_values.count('STRONG')
            if strong_count >= len(adx_values) * 0.6:
                results['strength'] = 'STRONG'
            elif strong_count >= len(adx_values) * 0.3:
                results['strength'] = 'MODERATE'
            else:
                results['strength'] = 'WEAK'
        else:
            results['strength'] = 'N/A'

        return results


if __name__ == "__main__":
    # Test with sample data
    print("Testing SMA Strategy...")

    # Create sample OHLC data
    dates = pd.date_range(start='2024-01-01', periods=300, freq='H')
    np.random.seed(42)

    # Create uptrending data
    price_trend = np.linspace(1.0800, 1.0900, 300)
    noise = np.random.randn(300) * 0.0005

    sample_data = pd.DataFrame({
        'open': price_trend + noise,
        'high': price_trend + noise + 0.0005,
        'low': price_trend + noise - 0.0005,
        'close': price_trend + noise,
        'volume': np.random.randint(1000, 5000, 300)
    }, index=dates)

    strategy = SMAStrategy()
    trend, adx_strength, adx_val = strategy.calculate_sma_trend(sample_data)

    print(f"[OK] SMA trend calculated: {trend}")
    print(f"Trend: {'BULLISH' if trend > 0 else 'BEARISH' if trend < 0 else 'NEUTRAL'}")
    print(f"ADX Strength: {adx_strength}")
    print(f"ADX Value: {adx_val:.2f}" if adx_val else "ADX Value: N/A")
