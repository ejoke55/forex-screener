"""
Confidence Scoring System for V3
Calculates confidence score (0-100%) based on multiple factors
Only signals with confidence >= 70% trigger alerts
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.strategies import CONFIDENCE_WEIGHTS, MIN_CONFIDENCE_THRESHOLD


class ConfidenceScorer:
    def __init__(self):
        self.weights = CONFIDENCE_WEIGHTS
        self.min_threshold = MIN_CONFIDENCE_THRESHOLD

    def calculate_timeframe_alignment_score(self, signal_data):
        """
        Calculate score based on weighted timeframe alignment (40 points max)

        Priority weighting (M5 and D1 shown for context only, not used in scoring):
        - M15 + H1 + H4 all agree: 40 points (highest - all core TFs aligned)
        - H1 + H4 agree: 20 points (higher TFs aligned)
        - M15 + H1 agree: 15 points (mid TFs aligned)
        - M15 + H4 agree: 10 points (spread alignment)
        - Others: 0 points

        Args:
            signal_data: dict with M5, M15, H1, H4, D values

        Returns:
            int: 0-40 points
        """
        # Extract core timeframe values (M15, H1, H4)
        # M5 and D1 are for context display only
        m15 = signal_data.get('M15', 0)
        h1 = signal_data.get('H1', 0)
        h4 = signal_data.get('H4', 0)

        # Helper function to check if values agree (same direction)
        def same_direction(a, b, c=None):
            """Check if 2 or 3 values have same sign (both/all positive or both/all negative)"""
            if c is None:
                # Two values
                return (a > 0 and b > 0) or (a < 0 and b < 0)
            else:
                # Three values
                return (a > 0 and b > 0 and c > 0) or (a < 0 and b < 0 and c < 0)

        # Priority 1: M15 + H1 + H4 all agree (40 points)
        if same_direction(m15, h1, h4):
            return 40

        # Priority 2: H1 + H4 agree (20 points)
        elif same_direction(h1, h4):
            return 20

        # Priority 3: M15 + H1 agree (15 points)
        elif same_direction(m15, h1):
            return 15

        # Priority 4: M15 + H4 agree (10 points)
        elif same_direction(m15, h4):
            return 10

        # No meaningful alignment
        else:
            return 0

    def calculate_ma_convergence_score(self, ma_cross_data, ma_pullback_data):
        """
        Calculate score based on MA strategy convergence (15 points max)

        Args:
            ma_cross_data: dict with MA cross results
            ma_pullback_data: dict with MA pullback results

        Returns:
            int: 0-15 points
        """
        score = 0

        # Check if both strategies agree
        cross_signal = ma_cross_data.get('score', 0)
        pullback_signal = ma_pullback_data.get('score', 0)

        # Both strongly bullish or bearish
        if (cross_signal >= 3 and pullback_signal >= 3) or (cross_signal <= -3 and pullback_signal <= -3):
            score = 15
        # Both moderately agree
        elif (cross_signal >= 1 and pullback_signal >= 1) or (cross_signal <= -1 and pullback_signal <= -1):
            score = 11
        # One strong, one moderate (same direction)
        elif (cross_signal > 0 and pullback_signal > 0) or (cross_signal < 0 and pullback_signal < 0):
            score = 7
        # Only one has signal
        elif cross_signal != 0 or pullback_signal != 0:
            score = 4

        return score

    def calculate_trend_strength_score(self, signal_data):
        """
        Calculate score based on ADX trend strength (15 points max)
        Priority on core timeframes: M15, H1, H4

        Args:
            signal_data: dict with ADX values for each timeframe

        Returns:
            int: 0-15 points
        """
        # Focus on core timeframes (M15, H1, H4)
        core_tfs = ['M15', 'H1', 'H4']
        adx_strengths = [signal_data.get(f'{tf}_adx', 'N/A') for tf in core_tfs]

        # Count strong ADX readings in core timeframes
        strong_count = adx_strengths.count('STRONG')
        moderate_count = adx_strengths.count('MODERATE')

        # Calculate score
        if strong_count == 3:
            return 15  # All core TFs have strong ADX
        elif strong_count == 2:
            return 12  # Two core TFs have strong ADX
        elif strong_count == 1:
            return 8   # One core TF has strong ADX
        elif moderate_count >= 2:
            return 5   # Two or more moderate ADX
        elif moderate_count == 1:
            return 3   # One moderate ADX
        else:
            return 0

    def calculate_volatility_score(self, df, atr_period=14):
        """
        Calculate score based on favorable volatility (15 points max)

        Args:
            df: DataFrame with OHLC data
            atr_period: ATR period

        Returns:
            int: 0-15 points
        """
        if df is None or len(df) < atr_period:
            return 5  # Neutral score

        # Calculate ATR
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=atr_period).mean()

        current_atr = atr.iloc[-1]
        avg_atr = atr.iloc[-50:].mean() if len(atr) >= 50 else atr.mean()

        # Calculate volatility ratio
        volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1

        # Optimal volatility is slightly above average (1.0-1.3)
        if 1.0 <= volatility_ratio <= 1.3:
            return 15  # Optimal volatility
        elif 0.8 <= volatility_ratio < 1.0:
            return 12  # Slightly low volatility
        elif 1.3 < volatility_ratio <= 1.5:
            return 10  # Slightly high volatility
        elif 0.6 <= volatility_ratio < 0.8:
            return 7   # Low volatility
        elif 1.5 < volatility_ratio <= 2.0:
            return 5   # High volatility
        else:
            return 2   # Extreme volatility (too low or too high)

    def calculate_historical_win_rate_score(self, strategy_name):
        """
        Calculate score based on strategy historical win rate (15 points max)

        Args:
            strategy_name: Name of the strategy

        Returns:
            int: 0-15 points
        """
        # Placeholder: In production, this would query the performance database
        # For now, return estimated win rates based on strategy type
        win_rates = {
            'ma_cross': 0.65,      # 65% win rate
            'ma_pullback': 0.70,   # 70% win rate
            'sma_trend': 0.68,     # 68% win rate (SMMA-based)
            'combined': 0.73,      # 73% win rate
        }

        win_rate = win_rates.get(strategy_name, 0.60)

        # Convert win rate to score (15 points max)
        return int(win_rate * 15)

    def calculate_confidence(self, signal_data, ma_cross_data=None, ma_pullback_data=None,
                           h4_df=None, strategy_name='combined'):
        """
        Calculate overall confidence score (0-100%)

        Args:
            signal_data: dict with timeframe signals and ADX values
            ma_cross_data: dict with MA cross results
            ma_pullback_data: dict with MA pullback results
            h4_df: DataFrame for H4 timeframe (for volatility calc)
            strategy_name: Name of strategy for win rate lookup

        Returns:
            dict: {
                'confidence': int (0-100),
                'breakdown': dict with individual scores,
                'meets_threshold': bool
            }
        """
        # Calculate individual scores
        timeframe_score = self.calculate_timeframe_alignment_score(signal_data)

        ma_convergence_score = 0
        if ma_cross_data and ma_pullback_data:
            ma_convergence_score = self.calculate_ma_convergence_score(ma_cross_data, ma_pullback_data)
        else:
            # If no MA data, give partial credit based on signal strength
            ma_convergence_score = min(abs(signal_data.get('score', 0)) * 3, 15)

        trend_strength_score = self.calculate_trend_strength_score(signal_data)
        volatility_score = self.calculate_volatility_score(h4_df) if h4_df is not None else 8
        win_rate_score = self.calculate_historical_win_rate_score(strategy_name)

        # Calculate total confidence
        confidence = (
            timeframe_score +
            ma_convergence_score +
            trend_strength_score +
            volatility_score +
            win_rate_score
        )

        # Cap at 100
        confidence = min(confidence, 100)

        return {
            'confidence': confidence,
            'breakdown': {
                'timeframe_alignment': timeframe_score,
                'ma_convergence': ma_convergence_score,
                'trend_strength': trend_strength_score,
                'volatility': volatility_score,
                'win_rate': win_rate_score
            },
            'meets_threshold': confidence >= self.min_threshold
        }


if __name__ == "__main__":
    # Test confidence scorer
    print("Testing Confidence Scorer...")

    scorer = ConfidenceScorer()

    # Test with strong signal
    test_signal = {
        'M5': 1, 'M15': 1, 'H1': 1, 'H4': 1, 'D': 1,
        'M5_adx': 'STRONG', 'M15_adx': 'STRONG', 'H1_adx': 'STRONG',
        'H4_adx': 'STRONG', 'D_adx': 'MODERATE',
        'score': 5
    }

    test_ma_cross = {'score': 4}
    test_ma_pullback = {'score': 3}

    result = scorer.calculate_confidence(
        test_signal,
        test_ma_cross,
        test_ma_pullback,
        strategy_name='combined'
    )

    print(f"\n[OK] Confidence: {result['confidence']}%")
    print(f"Meets Threshold (>={MIN_CONFIDENCE_THRESHOLD}%): {result['meets_threshold']}")
    print(f"\nBreakdown:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}")
