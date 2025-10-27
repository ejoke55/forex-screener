"""
API Configuration for V3 Forex Screener
"""
import os

# OANDA API Configuration
# Using same credentials as V2
OANDA_API_KEY = os.getenv('OANDA_API_KEY', '07050b50de2e9b1e541c7a2542c5d61a-8f0a7a6e27acde0a126234528edcc7bf')
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID', '101-001-24355333-001')
OANDA_BASE_URL = 'https://api-fxpractice.oanda.com'  # Practice account

# OANDA Rate Limits
OANDA_RATE_LIMIT = 120  # requests per second
OANDA_MAX_CONCURRENT = 20

# yfinance Configuration
# No API key needed - free access
YFINANCE_RATE_LIMIT = 2  # requests per second (conservative)

# Screener Settings
SCAN_INTERVAL = 900  # seconds (15 minutes)
REQUEST_DELAY = 0.1  # seconds between requests (to be safe)

# Candle count for calculations (increased for 200 SMA)
CANDLE_COUNT = 500  # number of historical candles to fetch

# Alert thresholds
STRONG_SIGNAL_THRESHOLD = 5  # Score >= 5 or <= -5
TREND_CHANGE_THRESHOLD = 3   # Score crosses above 3 or below -3
CONFIDENCE_ALERT_THRESHOLD = 70  # Only alert on confidence >= 70%
MIN_CONFIDENCE_THRESHOLD = 70  # Alias for consistency

# Risk Management Settings (for 100K FTMO account)
ACCOUNT_SIZE = 100000  # $100K account
RISK_PER_TRADE = 1.0   # 1% risk per trade
MAX_DAILY_LOSS = 5.0   # 5% max daily loss (FTMO rule)
MAX_TOTAL_LOSS = 10.0  # 10% max total loss (FTMO rule)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# News API Configuration (for news impact feature)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')  # Get free key from newsapi.org
FOREX_FACTORY_URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'

print("[CONFIG V3] API configuration loaded")
print(f"[CONFIG V3] OANDA URL: {OANDA_BASE_URL}")
print(f"[CONFIG V3] Account Size: ${ACCOUNT_SIZE:,}")
print(f"[CONFIG V3] Risk per Trade: {RISK_PER_TRADE}%")
print(f"[CONFIG V3] Scan interval: {SCAN_INTERVAL}s ({SCAN_INTERVAL/60:.1f} minutes)")
print(f"[CONFIG V3] Telegram: {'ENABLED' if TELEGRAM_ENABLED else 'DISABLED'}")
