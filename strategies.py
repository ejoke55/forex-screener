"""
Strategy parameter configuration for V3
Using SMMA (Smoothed Moving Average) with 20, 50, 200 periods
"""

# SMMA Strategy Parameters
# Using 20, 50, 200 Smoothed Moving Averages (SMMA/RMA)
# SMMA provides smoother trends than SMA, reducing false signals
SMA_CONFIG = {
    'fast_sma': 20,      # Fast SMMA 20 (replaces 9 EMA)
    'medium_sma': 50,    # Medium SMMA 50 (replaces 21 EMA)
    'slow_sma': 200,     # Slow SMMA 200 (replaces 50 EMA)
    'use_adx': True,
    'adx_period': 14,
    'adx_strong': 25,
    'adx_weak': 20,
}

# MA Cross Strategy Parameters
# Focused on 20/50 cross as the primary signal
MA_CROSS_CONFIG = {
    'fast_ma': 20,
    'slow_ma': 50,
    'confirm_ma': 200,  # Used for trend confirmation
    'min_separation': 0.0001,  # Minimum price separation to confirm cross
}

# MA Pullback Strategy Parameters
# All 3 MAs aligned in one direction, then look for pullback
MA_PULLBACK_CONFIG = {
    'fast_ma': 20,
    'medium_ma': 50,
    'slow_ma': 200,
    'pullback_threshold': 0.5,  # % pullback to trigger signal
    'min_alignment_bars': 3,     # Minimum bars with MA alignment
}

# Supertrend Strategy Parameters (adjusted or will be removed based on testing)
# Increasing multiplier to reduce sensitivity
SUPERTREND_CONFIG = {
    'atr_period': 14,      # Increased from 10
    'multiplier': 4.0,     # Increased from 3.0 to reduce false signals
    'enabled': True,       # Set to False to completely disable
}

# Confidence Scoring Weights (Total = 100 points)
# Prioritizes core timeframes: M15, H1, H4 (M5 and D1 for context only)
CONFIDENCE_WEIGHTS = {
    'timeframe_alignment': 40,    # 40 points for M15/H1/H4 weighted alignment
    'ma_convergence': 15,         # 15 points for MA signal convergence
    'trend_strength': 15,         # 15 points for ADX trend strength
    'volatility_check': 15,       # 15 points for favorable volatility
    'historical_win_rate': 15,    # 15 points for strategy win rate
}

# Minimum confidence threshold for alerts
MIN_CONFIDENCE_THRESHOLD = 70  # Only alert on signals >= 70%

print("[CONFIG V3] Strategy parameters loaded")
print(f"[CONFIG V3] SMMA: {SMA_CONFIG['fast_sma']}/{SMA_CONFIG['medium_sma']}/{SMA_CONFIG['slow_sma']}")
print(f"[CONFIG V3] MA Cross: {MA_CROSS_CONFIG['fast_ma']}/{MA_CROSS_CONFIG['slow_ma']}")
print(f"[CONFIG V3] Supertrend: {'ENABLED' if SUPERTREND_CONFIG['enabled'] else 'DISABLED'}")
print(f"[CONFIG V3] Min Confidence: {MIN_CONFIDENCE_THRESHOLD}%")
