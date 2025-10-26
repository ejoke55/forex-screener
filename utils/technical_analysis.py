"""
Technical Analysis Module for V3
Includes pivot points, support/resistance levels, and pattern recognition
"""
import pandas as pd
import numpy as np


class TechnicalAnalyzer:
    def __init__(self):
        pass

    def calculate_pivot_points(self, df):
        """
        Calculate standard pivot points (daily)

        Args:
            df: DataFrame with OHLC data

        Returns:
            dict: Pivot points (PP, R1, R2, R3, S1, S2, S3)
        """
        if df is None or len(df) < 1:
            return None

        # Get previous day's data (last row if daily, or aggregate if intraday)
        high = df['high'].iloc[-1]
        low = df['low'].iloc[-1]
        close = df['close'].iloc[-1]

        # Calculate pivot point
        pp = (high + low + close) / 3

        # Calculate resistance levels
        r1 = (2 * pp) - low
        r2 = pp + (high - low)
        r3 = high + 2 * (pp - low)

        # Calculate support levels
        s1 = (2 * pp) - high
        s2 = pp - (high - low)
        s3 = low - 2 * (high - pp)

        return {
            'PP': round(pp, 5),
            'R1': round(r1, 5),
            'R2': round(r2, 5),
            'R3': round(r3, 5),
            'S1': round(s1, 5),
            'S2': round(s2, 5),
            'S3': round(s3, 5)
        }

    def find_support_resistance(self, df, lookback=20, min_touches=2):
        """
        Find key support and resistance levels

        Args:
            df: DataFrame with OHLC data
            lookback: Number of periods to look back
            min_touches: Minimum touches to confirm S/R

        Returns:
            dict: Support and resistance levels
        """
        if df is None or len(df) < lookback:
            return {'support': [], 'resistance': []}

        df = df.copy()
        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values

        # Find local peaks (resistance)
        resistance_levels = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance_levels.append(highs[i])

        # Find local troughs (support)
        support_levels = []
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support_levels.append(lows[i])

        # Cluster nearby levels (within 0.1%)
        def cluster_levels(levels, tolerance=0.001):
            if not levels:
                return []

            levels = sorted(levels)
            clusters = []
            current_cluster = [levels[0]]

            for level in levels[1:]:
                if abs(level - current_cluster[-1]) / current_cluster[-1] <= tolerance:
                    current_cluster.append(level)
                else:
                    clusters.append(np.mean(current_cluster))
                    current_cluster = [level]

            clusters.append(np.mean(current_cluster))
            return [round(c, 5) for c in clusters]

        # Get top 3 support and resistance levels
        support_clustered = cluster_levels(support_levels)[-3:] if support_levels else []
        resistance_clustered = cluster_levels(resistance_levels)[-3:] if resistance_levels else []

        return {
            'support': sorted(support_clustered),
            'resistance': sorted(resistance_clustered, reverse=True)
        }

    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        if df is None or len(df) < period:
            return None

        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr.iloc[-1]

    def identify_price_action_pattern(self, df):
        """
        Identify price action patterns

        Args:
            df: DataFrame with OHLC data

        Returns:
            str: Pattern name or 'NONE'
        """
        if df is None or len(df) < 10:
            return 'NONE'

        closes = df['close'].values[-10:]
        highs = df['high'].values[-10:]
        lows = df['low'].values[-10:]

        # Check for engulfing patterns
        if len(closes) >= 2:
            prev_body = abs(closes[-2] - df['open'].iloc[-2])
            curr_body = abs(closes[-1] - df['open'].iloc[-1])

            # Bullish engulfing
            if closes[-2] < df['open'].iloc[-2] and \
               closes[-1] > df['open'].iloc[-1] and \
               curr_body > prev_body * 1.5:
                return 'BULLISH_ENGULFING'

            # Bearish engulfing
            if closes[-2] > df['open'].iloc[-2] and \
               closes[-1] < df['open'].iloc[-1] and \
               curr_body > prev_body * 1.5:
                return 'BEARISH_ENGULFING'

        # Check for doji
        if len(closes) >= 1:
            body = abs(closes[-1] - df['open'].iloc[-1])
            hl_range = highs[-1] - lows[-1]

            if body < hl_range * 0.1:
                return 'DOJI'

        # Check for pin bar
        if len(closes) >= 1:
            body = abs(closes[-1] - df['open'].iloc[-1])
            upper_wick = highs[-1] - max(closes[-1], df['open'].iloc[-1])
            lower_wick = min(closes[-1], df['open'].iloc[-1]) - lows[-1]

            if upper_wick > body * 2 and lower_wick < body * 0.5:
                return 'BEARISH_PIN'
            if lower_wick > body * 2 and upper_wick < body * 0.5:
                return 'BULLISH_PIN'

        return 'NONE'

    def analyze_instrument(self, data_dict, instrument):
        """
        Comprehensive technical analysis for an instrument

        Args:
            data_dict: dict with timeframe data
            instrument: instrument name

        Returns:
            dict: Complete technical analysis
        """
        analysis = {
            'instrument': instrument,
            'daily_pivots': None,
            'h4_sr_levels': None,
            'h1_sr_levels': None,
            'current_price': None,
            'atr_h4': None,
            'atr_h1': None,
            'pattern_h4': 'NONE',
            'pattern_h1': 'NONE',
            'key_levels': []
        }

        # Get daily pivot points
        if 'D' in data_dict and data_dict['D'] is not None:
            analysis['daily_pivots'] = self.calculate_pivot_points(data_dict['D'])

        # Get H4 S/R levels
        if 'H4' in data_dict and data_dict['H4'] is not None:
            analysis['h4_sr_levels'] = self.find_support_resistance(data_dict['H4'])
            analysis['atr_h4'] = self.calculate_atr(data_dict['H4'])
            analysis['pattern_h4'] = self.identify_price_action_pattern(data_dict['H4'])
            analysis['current_price'] = data_dict['H4']['close'].iloc[-1]

        # Get H1 S/R levels
        if 'H1' in data_dict and data_dict['H1'] is not None:
            analysis['h1_sr_levels'] = self.find_support_resistance(data_dict['H1'])
            analysis['atr_h1'] = self.calculate_atr(data_dict['H1'])
            analysis['pattern_h1'] = self.identify_price_action_pattern(data_dict['H1'])
            if analysis['current_price'] is None:
                analysis['current_price'] = data_dict['H1']['close'].iloc[-1]

        # Compile key levels (pivot points + S/R)
        key_levels = []
        if analysis['daily_pivots']:
            for level_type, level_value in analysis['daily_pivots'].items():
                key_levels.append({
                    'type': f'PIVOT_{level_type}',
                    'price': level_value,
                    'timeframe': 'D'
                })

        if analysis['h4_sr_levels']:
            for s_level in analysis['h4_sr_levels']['support']:
                key_levels.append({'type': 'SUPPORT', 'price': s_level, 'timeframe': 'H4'})
            for r_level in analysis['h4_sr_levels']['resistance']:
                key_levels.append({'type': 'RESISTANCE', 'price': r_level, 'timeframe': 'H4'})

        if analysis['h1_sr_levels']:
            for s_level in analysis['h1_sr_levels']['support']:
                key_levels.append({'type': 'SUPPORT', 'price': s_level, 'timeframe': 'H1'})
            for r_level in analysis['h1_sr_levels']['resistance']:
                key_levels.append({'type': 'RESISTANCE', 'price': r_level, 'timeframe': 'H1'})

        # Sort key levels by price
        analysis['key_levels'] = sorted(key_levels, key=lambda x: x['price'], reverse=True)

        return analysis


if __name__ == "__main__":
    # Test technical analyzer
    print("Testing Technical Analyzer...")

    # Create sample daily data
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    np.random.seed(42)

    sample_data = pd.DataFrame({
        'open': 1.0800 + np.random.randn(50).cumsum() * 0.002,
        'high': 1.0800 + np.random.randn(50).cumsum() * 0.002 + 0.005,
        'low': 1.0800 + np.random.randn(50).cumsum() * 0.002 - 0.005,
        'close': 1.0800 + np.random.randn(50).cumsum() * 0.002,
        'volume': np.random.randint(1000, 5000, 50)
    }, index=dates)

    analyzer = TechnicalAnalyzer()

    # Test pivot points
    pivots = analyzer.calculate_pivot_points(sample_data)
    print(f"\n[OK] Pivot Points:")
    for key, value in pivots.items():
        print(f"  {key}: {value}")

    # Test S/R levels
    sr_levels = analyzer.find_support_resistance(sample_data)
    print(f"\n[OK] Support/Resistance:")
    print(f"  Support: {sr_levels['support']}")
    print(f"  Resistance: {sr_levels['resistance']}")

    # Test ATR
    atr = analyzer.calculate_atr(sample_data)
    print(f"\n[OK] ATR: {atr:.5f}")

    # Test pattern
    pattern = analyzer.identify_price_action_pattern(sample_data)
    print(f"\n[OK] Pattern: {pattern}")
