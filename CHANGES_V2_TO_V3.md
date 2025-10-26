# V2 to V3 Changes Summary

## 🎯 Major Changes

### 1. Reduced Instruments (19 → 11)
**V2**: 15 forex pairs + 4 indices = 19 instruments
**V3**: 8 FTMO forex pairs + 3 instruments = 11 instruments

**Removed pairs**:
- USD_CAD, NZD_USD, NZD_JPY, EUR_JPY, GBP_NZD, AUD_CAD, NZD_CAD
- Nikkei 225, ASX 200

**Retained (11 FTMO instruments)**:
- EURUSD, USDJPY, GBPUSD, AUDUSD, EURAUD, AUDJPY, GBPJPY, GBPAUD
- XAUUSD (Gold), WTI Oil, NAS100

**Impact**: 52% faster scans (114 → 55 API calls)

### 2. EMA → SMA Conversion
**V2**: EMA 9/21/50
**V3**: SMA 20/50/200

**Rationale**:
- SMAs provide cleaner, less noisy signals
- 200 SMA is industry standard for long-term trend
- 20/50 cross is widely recognized signal
- Easier to interpret for most traders

### 3. Reduced Timeframes (6 → 5)
**V2**: M5, M15, M30, H1, H4, D1
**V3**: M5, M15, H1, H4, D1

**Removed**: M30 (redundant between M15 and H1)

**Impact**: 17% fewer API calls

### 4. New Strategy Tabs

#### MA Cross (NEW)
- **Focus**: 20/50 SMA crossovers
- **Confirmation**: 200 SMA trend alignment
- **Detection**: Golden Cross (bullish), Death Cross (bearish)
- **Strength Scoring**: 50-90% based on trend confirmation

#### MA Pullback (NEW)
- **Requirement**: All 3 SMAs aligned for 3+ bars
- **Signal**: Price pulls back to 20, 50, or 200 SMA
- **Best Entries**: Pullback to 20 SMA in strong trend
- **Use Case**: Enter trending markets at better prices

#### Supertrend (ADJUSTED)
- **V2**: ATR=10, Multiplier=3.0
- **V3**: ATR=14, Multiplier=4.0
- **Impact**: Less sensitive, fewer false signals
- **Can be disabled**: Set in config if too noisy

### 5. Confidence Scoring System (NEW)
**Purpose**: Filter out low-quality signals

**Scoring Breakdown** (0-100%):
- Timeframe Alignment: 30 points
- MA Convergence: 25 points
- Trend Strength (ADX): 20 points
- Volatility Check: 15 points
- Historical Win Rate: 10 points

**Alert Threshold**: Only signals ≥70% confidence trigger Telegram alerts

### 6. Risk Management System (NEW)
**FTMO-Compliant for 100K Account**:
- Risk per trade: 1% ($1,000)
- Max daily loss: 5% ($5,000)
- Max total loss: 10% ($10,000)

**Features**:
- Automatic position sizing
- Stop loss distance in pips
- Take profit calculation (default 2:1 R:R)
- Instrument-specific pip values (JPY, Gold, Oil, NAS100)

### 7. Technical Analysis Tab (NEW)
**Daily Pivot Points**:
- PP, R1, R2, R3, S1, S2, S3
- Calculated from previous day's H/L/C

**Support/Resistance Levels**:
- H4 S/R levels (3 support, 3 resistance)
- H1 S/R levels (3 support, 3 resistance)
- Smart clustering of nearby levels

**Pattern Recognition**:
- Bullish/Bearish Engulfing
- Bullish/Bearish Pin Bars
- Doji candles

### 8. News Impact Tab (NEW)
**Data Sources**:
- Forex Factory: Economic calendar (high-impact events)
- News API: Real-time forex/commodity news

**Features**:
- Auto-categorization by currency pairs
- Shows relevant news for each of the 11 instruments
- Updates periodically (every 3rd scan to save API calls)

### 9. Dashboard Improvements
**V2**: 4 tabs (Strong Signals, EMA, Supertrend, Combined)
**V3**: 6 tabs
1. 🔥 High Confidence (≥70%)
2. 📈 MA Cross
3. 🎯 MA Pullback
4. 📊 Technical Analysis
5. 📰 News Impact
6. 📋 All Instruments

**UI Enhancements**:
- Confidence badges (color-coded)
- Better visual hierarchy
- Cleaner card layouts
- More informative tooltips

### 10. Performance Tracking (NEW)
**Database Schema** (PostgreSQL):
- `signals`: Every signal generated
- `signal_outcomes`: Track what happened to signals
- `daily_performance`: Daily aggregate stats
- `strategy_performance`: Win rates by strategy
- `instrument_performance`: Best-performing pairs
- `trades`: Actual trades taken
- `account_snapshots`: Daily account tracking

**Queries & Views**:
- High confidence signals view
- Recent performance view (30 days)
- Win rate calculation function

## 📊 Performance Comparison

| Metric | V2 | V3 | Improvement |
|--------|----|----|-------------|
| Instruments | 19 | 11 | 42% reduction |
| Timeframes | 6 | 5 | 17% reduction |
| API Calls/Scan | 114 | 55 | 52% faster |
| Scan Time | 2-4 min | ~90 sec | 55% faster |
| Strategies | 2 | 3 | +1 strategy |
| Tabs | 4 | 6 | +2 tabs |

## 🗂️ File Structure Comparison

### V2 Structure
```
forex_screener/
├── config/
│   ├── instruments.py (19 instruments)
│   ├── strategies.py (EMA config)
│   └── api_config.py
├── strategies/
│   ├── ema_triple_cross.py
│   └── supertrend_mtf.py
├── connectors/
│   ├── oanda_connector.py
│   └── yfinance_connector.py
├── web_dashboard.py
├── notifications.py
└── templates/
    └── dashboard.html
```

### V3 Structure
```
V3_forex_screener/
├── config/
│   ├── instruments.py (11 instruments)
│   ├── strategies.py (SMA + MA configs)
│   └── api_config.py (+ risk settings)
├── strategies/
│   ├── sma_strategy.py (NEW)
│   ├── ma_cross_strategy.py (NEW)
│   ├── ma_pullback_strategy.py (NEW)
│   └── supertrend_mtf.py (adjusted)
├── connectors/
│   ├── oanda_connector.py
│   └── yfinance_connector.py
├── utils/ (NEW)
│   ├── confidence_scorer.py (NEW)
│   ├── risk_calculator.py (NEW)
│   ├── technical_analyzer.py (NEW)
│   └── news_fetcher.py (NEW)
├── screener_v3.py (NEW - main screener)
├── app.py (NEW - Flask app)
├── notifications.py
├── templates/
│   └── dashboard.html (completely redesigned)
├── database_schema.sql (NEW)
├── requirements.txt
├── README.md (comprehensive)
├── DEPLOYMENT.md (NEW)
├── .env.example (NEW)
├── .gitignore (NEW)
├── Procfile (NEW)
└── runtime.txt (NEW)
```

## 🚀 Migration Path (V2 → V3)

### Option 1: Clean Deployment (Recommended)
1. Keep V2 running
2. Deploy V3 to new Render service
3. Test V3 thoroughly
4. Switch traffic to V3
5. Decommission V2

### Option 2: Update Existing Deployment
1. Backup V2 code and data
2. Push V3 to same GitHub repo (different branch or replace)
3. Update Render build settings if needed
4. Deploy

### Option 3: Run Both in Parallel
- V2: `https://forex-screener.onrender.com`
- V3: `https://forex-screener-v3.onrender.com`
- Compare results side-by-side

## ✅ Feature Parity Check

| Feature | V2 | V3 |
|---------|----|----|
| Multi-timeframe analysis | ✅ | ✅ |
| OANDA data | ✅ | ✅ |
| yfinance data | ✅ | ✅ |
| EMA strategy | ✅ | ➡️ SMA |
| Supertrend | ✅ | ✅ (adjusted) |
| Web dashboard | ✅ | ✅ (enhanced) |
| Telegram alerts | ✅ | ✅ (with confidence filter) |
| Auto-refresh | ✅ | ✅ |
| Background scanning | ✅ | ✅ (5 min interval) |
| MA Cross detection | ❌ | ✅ NEW |
| MA Pullback | ❌ | ✅ NEW |
| Confidence scoring | ❌ | ✅ NEW |
| Risk calculator | ❌ | ✅ NEW |
| Technical analysis | ❌ | ✅ NEW |
| News impact | ❌ | ✅ NEW |
| Performance tracking | ❌ | ✅ NEW |
| Pivot points | ❌ | ✅ NEW |
| S/R levels | ❌ | ✅ NEW |
| Pattern recognition | ❌ | ✅ NEW |

## 🎓 What You Need to Know

### If You're Using V2
**Key Differences**:
- Fewer instruments (only your 11 FTMO pairs)
- SMA instead of EMA (different signals)
- New confidence score (only high-quality alerts)
- More features (technical analysis, news, risk calc)

**Behavior Changes**:
- Fewer Telegram alerts (confidence filtering)
- Different signal timings (SMA vs EMA lag)
- More detailed information per signal

### Learning Curve
- **Easy**: If you understand V2, V3 is familiar but enhanced
- **UI**: Same layout, just more tabs
- **Strategies**: More options, but each clearly labeled
- **Configuration**: Similar to V2, just more settings

## 📈 Expected Results

### Signal Quality
- **Fewer signals**: Due to confidence filtering
- **Higher quality**: Only signals ≥70% confidence
- **Better timing**: MA pullbacks catch better entries
- **Less noise**: Adjusted Supertrend parameters

### Trading Impact
- **More selective**: Won't trade every signal
- **Better risk management**: Automatic position sizing
- **Improved entries**: Pullback strategy
- **Context-aware**: News and technical levels

## 🔄 Rollback Plan

If V3 doesn't work as expected:

1. **Keep V2 backup**: Don't delete V2 folder
2. **Separate Render service**: Deploy V3 to new service
3. **Easy rollback**: Just switch Render URL back to V2
4. **Data preserved**: No data loss if kept separate

---

**Recommendation**: Deploy V3 alongside V2 initially, compare for 1-2 weeks, then fully migrate.
