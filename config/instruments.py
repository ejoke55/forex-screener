"""
Instrument configuration for V3 Forex Screener
Optimized for 11 FTMO instruments only
"""

# OANDA Forex Pairs (8 pairs)
OANDA_PAIRS = [
    'EUR_USD',    # EURUSD
    'USD_JPY',    # USDJPY
    'GBP_USD',    # GBPUSD
    'AUD_USD',    # AUDUSD
    'EUR_AUD',    # EURAUD
    'AUD_JPY',    # AUDJPY
    'GBP_JPY',    # GBPJPY
    'GBP_AUD',    # GBPAUD
]

# yfinance Instruments (3 instruments)
# Note: Using proxies for instruments that may not have direct yfinance symbols
YFINANCE_INSTRUMENTS = [
    ('GC=F', 'XAUUSD', 'Gold'),      # Gold/XAUUSD
    ('CL=F', 'WTI', 'WTI Oil'),      # WTI Crude Oil
    ('^NDX', 'NAS100', 'NASDAQ 100'), # NASDAQ 100
]

# Timeframes to analyze
# Using H4, H1, M15, M5 as primary timeframes for day trading
# D1 for higher timeframe context
TIMEFRAMES = ['M5', 'M15', 'H1', 'H4', 'D']
TIMEFRAME_LABELS = ['M5', 'M15', 'H1', 'H4', 'D1']

# Timeframe mapping for OANDA
OANDA_TIMEFRAME_MAP = {
    'M5': 'M5',
    'M15': 'M15',
    'H1': 'H1',
    'H4': 'H4',
    'D': 'D',
}

# Timeframe mapping for yfinance
YFINANCE_TIMEFRAME_MAP = {
    'M5': '5m',
    'M15': '15m',
    'H1': '1h',
    'H4': '4h',
    'D': '1d',
}

# Display names for instruments
def get_display_name(symbol):
    """Get friendly display name for symbol"""
    # Check if it's a yfinance symbol
    for yf_symbol, standard_symbol, name in YFINANCE_INSTRUMENTS:
        if symbol == yf_symbol or symbol == standard_symbol:
            return standard_symbol  # Return standard symbol like XAUUSD

    # OANDA forex pair - format nicely
    return symbol.replace('_', '')

# Total instrument count
TOTAL_FOREX = len(OANDA_PAIRS)  # 8
TOTAL_INSTRUMENTS_YF = len(YFINANCE_INSTRUMENTS)  # 3
TOTAL_INSTRUMENTS = TOTAL_FOREX + TOTAL_INSTRUMENTS_YF  # 11
TOTAL_TIMEFRAMES = len(TIMEFRAMES)  # 5

# Expected API calls per scan (significantly reduced from V2's 114)
API_CALLS_PER_SCAN = TOTAL_INSTRUMENTS * TOTAL_TIMEFRAMES  # 55 calls

print(f"[CONFIG V3] Loaded {TOTAL_FOREX} forex pairs + {TOTAL_INSTRUMENTS_YF} instruments = {TOTAL_INSTRUMENTS} total")
print(f"[CONFIG V3] {TOTAL_TIMEFRAMES} timeframes = {API_CALLS_PER_SCAN} API calls per scan")
print(f"[CONFIG V3] Reduction: 114 → {API_CALLS_PER_SCAN} calls (52% faster)")
