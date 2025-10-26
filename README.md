# V3 Forex Screener - FTMO 11 Instruments

Comprehensive forex screener optimized for 11 FTMO instruments with SMA-based strategies, confidence scoring, risk management, and technical analysis.

## 🎯 Key Features

### V3 Improvements over V2
- **Reduced Instruments**: 19 → 11 FTMO instruments (52% faster scans)
- **SMA Instead of EMA**: Using 20, 50, 200 SMAs for cleaner signals
- **New Strategies**:
  - MA Cross (20/50 crossover with 200 confirmation)
  - MA Pullback (aligned MAs with pullback opportunities)
  - Adjusted Supertrend (less sensitive, fewer false signals)
- **Confidence Scoring**: 0-100% confidence score for each signal (alerts only >70%)
- **Risk Calculator**: FTMO-compliant position sizing for 100K account (1% risk per trade)
- **Technical Analysis Tab**: Daily pivot points, S/R levels for H4 and H1
- **News Impact Tab**: Real-time forex news categorized by pairs
- **Performance Tracking**: PostgreSQL database schema for signal tracking

### 11 FTMO Instruments
- **8 Forex Pairs**: EURUSD, USDJPY, GBPUSD, AUDUSD, EURAUD, AUDJPY, GBPJPY, GBPAUD
- **3 Other Instruments**: XAUUSD (Gold), WTI Oil, NAS100 (NASDAQ)

## 📋 Dashboard Tabs

1. **🔥 High Confidence** - Signals with confidence ≥70%
2. **📈 MA Cross** - 20/50 SMA crossover signals
3. **🎯 MA Pullback** - Pullback opportunities in trending markets
4. **📊 Technical Analysis** - Pivot points, S/R levels, patterns
5. **📰 News Impact** - Forex news impacting your instruments
6. **📋 All Instruments** - Overview of all 11 instruments

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- OANDA API account (practice or live)
- Telegram Bot (optional, for alerts)
- News API key (optional, from https://newsapi.org/)

### 2. Installation

```bash
# Navigate to V3 directory
cd /path/to/V3_forex_screener

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use any text editor
```

### 3. Configuration

Edit `.env` file:

```env
# Required
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here

# Optional (for Telegram alerts)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Optional (for news feature)
NEWS_API_KEY=your_news_api_key_here
```

### 4. Run the Dashboard

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## 📊 Strategy Details

### SMA Strategy (20, 50, 200 SMAs)
- **Fast SMA**: 20 periods
- **Medium SMA**: 50 periods
- **Slow SMA**: 200 periods
- **Signal**: All 3 SMAs aligned = strong trend
- **ADX Filter**: Confirms trend strength

### MA Cross Strategy
- **Primary Signal**: 20 SMA crosses 50 SMA
- **Confirmation**: Price and MAs relative to 200 SMA
- **Golden Cross**: 20 crosses above 50 (bullish)
- **Death Cross**: 20 crosses below 50 (bearish)

### MA Pullback Strategy
- **Requirement**: All 3 SMAs aligned for 3+ bars
- **Signal**: Price pulls back to 20, 50, or 200 SMA
- **Best Entry**: Pullback to 20 SMA in strong trend
- **Confirmation**: Trend alignment maintained

### Supertrend (Adjusted)
- **ATR Period**: 14 (increased from 10)
- **Multiplier**: 4.0 (increased from 3.0)
- **Purpose**: Less sensitive, fewer false signals
- **Can be disabled**: Set `SUPERTREND_CONFIG['enabled'] = False` in `config/strategies.py`

## 🎯 Confidence Scoring System

Signals are scored 0-100% based on:

| Factor | Max Points | Description |
|--------|-----------|-------------|
| Timeframe Alignment | 30 | How many timeframes agree |
| MA Convergence | 25 | Agreement between MA strategies |
| Trend Strength | 20 | ADX readings across timeframes |
| Volatility | 15 | Favorable ATR levels |
| Historical Win Rate | 10 | Strategy performance history |

**Alert Threshold**: Only signals with ≥70% confidence trigger Telegram alerts.

## 💰 Risk Management

### FTMO-Compliant Settings
- **Account Size**: $100,000
- **Risk per Trade**: 1% ($1,000)
- **Max Daily Loss**: 5% ($5,000)
- **Max Total Loss**: 10% ($10,000)

### Position Sizing
The risk calculator automatically determines:
- Position size in lots
- Stop loss distance in pips
- Take profit based on R:R ratio (default 2:1)
- Actual risk amount

### Example
For EURUSD trade:
- Entry: 1.0850
- Stop Loss: 1.0820 (30 pips)
- Take Profit: 1.0910 (60 pips, 2:1 R:R)
- Position Size: 0.33 lots
- Risk: $1,000 (1%)

## 📈 Technical Analysis

### Daily Pivot Points
- **PP** (Pivot Point): Main support/resistance
- **R1, R2, R3**: Resistance levels
- **S1, S2, S3**: Support levels
- **Calculation**: Based on previous day's High, Low, Close

### Support/Resistance Levels
- **H4 S/R**: Key levels from 4-hour chart
- **H1 S/R**: Key levels from 1-hour chart
- **Detection**: Local peaks and troughs
- **Clustering**: Nearby levels merged

### Pattern Recognition
- Bullish/Bearish Engulfing
- Pin Bars (Bullish/Bearish)
- Doji
- More patterns coming in future updates

## 📰 News Impact

### Data Sources
1. **Forex Factory**: Economic calendar (high-impact events)
2. **News API**: Real-time forex and commodity news

### Categorization
News automatically categorized by which pairs it affects:
- USD news → EURUSD, USDJPY, GBPUSD, AUDUSD
- Gold news → XAUUSD
- Oil news → WTI
- Central bank news → Relevant currency pairs

## 🗄️ Performance Tracking

### Database Setup (Optional)

1. Install PostgreSQL
2. Create database:
```bash
createdb forex_screener
```

3. Load schema:
```bash
psql forex_screener < database_schema.sql
```

4. Add DATABASE_URL to `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/forex_screener
```

### Tracked Metrics
- **Signals**: Every signal generated with full context
- **Outcomes**: What happened to each signal
- **Daily Performance**: Aggregate daily statistics
- **Strategy Performance**: Win rates by strategy
- **Instrument Performance**: Which pairs perform best

## 🔧 Deployment to Render

### Method 1: Connect GitHub Repo

1. **Push V3 to GitHub**:
```bash
cd V3_forex_screener
git init
git add .
git commit -m "Initial V3 commit"
git remote add origin https://github.com/YOUR_USERNAME/forex-screener.git
git push -u origin main
```

2. **Create Render Web Service**:
   - Go to https://render.com/
   - New → Web Service
   - Connect your GitHub repo
   - Select `V3_forex_screener` directory (if not root)
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

3. **Add Environment Variables** in Render dashboard:
   - `OANDA_API_KEY`
   - `OANDA_ACCOUNT_ID`
   - `TELEGRAM_BOT_TOKEN` (optional)
   - `TELEGRAM_CHAT_ID` (optional)
   - `NEWS_API_KEY` (optional)

### Method 2: Direct Deploy

1. Install Render CLI:
```bash
npm install -g render
```

2. Login to Render:
```bash
render login
```

3. Deploy:
```bash
render deploy
```

## 📱 Telegram Alerts

### Setup

1. **Create Bot**:
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions to get bot token

2. **Get Chat ID**:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":YOUR_CHAT_ID}`

3. **Add to .env**:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234...
TELEGRAM_CHAT_ID=123456789
```

### Alert Format

```
🟢 BUY SIGNAL - EURUSD

Confidence: 85%
Strategy: MA Cross
Signal: STRONG BUY (CROSS)
Current Price: 1.08500

Timeframes:
M5: ✅ UP
M15: ✅ UP
H1: ✅ UP
H4: ✅ UP
D1: ✅ UP

⏰ 2025-10-26 10:30:00
```

## 🔍 API Endpoints

- `GET /` - Dashboard
- `GET /api/results` - Latest scan results
- `GET /api/instrument/<instrument>` - Detailed analysis for instrument
- `GET /api/news` - News categorized by pairs
- `POST /api/risk_calculate` - Calculate risk for trade
- `GET /api/scan` - Trigger manual scan

## ⚙️ Configuration

### Adjust Confidence Threshold

Edit `config/api_config.py`:
```python
CONFIDENCE_ALERT_THRESHOLD = 70  # Change to 75, 80, etc.
```

### Adjust Risk Per Trade

Edit `config/api_config.py`:
```python
RISK_PER_TRADE = 1.0  # Change to 0.5, 2.0, etc.
```

### Disable Supertrend

Edit `config/strategies.py`:
```python
SUPERTREND_CONFIG = {
    'enabled': False  # Set to False to disable
}
```

### Change Scan Interval

Edit `app.py`:
```python
time.sleep(300)  # 300 seconds = 5 minutes
```

## 🐛 Troubleshooting

### Common Issues

1. **"OANDA connection failed"**
   - Check API key and account ID in `.env`
   - Verify OANDA account is active

2. **"No data available"**
   - Wait for initial scan to complete (2-3 minutes)
   - Check internet connection
   - Verify OANDA API rate limits not exceeded

3. **"Telegram alerts not working"**
   - Verify bot token and chat ID in `.env`
   - Check bot has been started (send `/start` to bot)
   - Verify confidence threshold is met

4. **"News not loading"**
   - News API key may be missing or invalid
   - Free News API has rate limits (100 requests/day)
   - Forex Factory calendar doesn't require API key

## 📊 Performance Optimization

### Reduce Scan Time
- Already optimized: 11 instruments vs 19 (42% faster)
- 5 timeframes vs 6 (17% faster)
- Total: ~55 API calls per scan vs 114

### Reduce Memory Usage
- Limit candle count in `config/api_config.py`:
```python
CANDLE_COUNT = 300  # Reduce from 500
```

### Increase Scan Frequency
- Not recommended due to API rate limits
- OANDA: Max 120 requests/second
- Current: 55 requests every 5 minutes = well within limits

## 📝 License

This project is for educational and personal use only. Use at your own risk when trading real money.

## 🙏 Credits

- **OANDA**: Forex data provider
- **yfinance**: Commodity and index data
- **Forex Factory**: Economic calendar
- **News API**: Forex news
- **Telegram**: Alert system

## 📞 Support

For issues and questions:
- Check logs in terminal
- Review configuration files
- Verify API credentials
- Check GitHub issues (if repo is public)

---

**Happy Trading! Remember: Past performance does not guarantee future results. Always use proper risk management.**
