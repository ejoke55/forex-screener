-- V3 Forex Screener Database Schema
-- PostgreSQL schema for performance tracking

-- Signals table - stores every signal generated
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    instrument VARCHAR(20) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,  -- BUY/SELL
    confidence DECIMAL(5,2) NOT NULL,
    entry_price DECIMAL(10,5),
    stop_loss DECIMAL(10,5),
    take_profit DECIMAL(10,5),

    -- Timeframe signals
    m5_signal INTEGER,
    m15_signal INTEGER,
    h1_signal INTEGER,
    h4_signal INTEGER,
    d_signal INTEGER,

    -- ADX strength
    m5_adx VARCHAR(20),
    m15_adx VARCHAR(20),
    h1_adx VARCHAR(20),
    h4_adx VARCHAR(20),
    d_adx VARCHAR(20),

    -- Overall score
    overall_score INTEGER,

    -- Technical analysis
    daily_pivot DECIMAL(10,5),
    r1 DECIMAL(10,5),
    r2 DECIMAL(10,5),
    r3 DECIMAL(10,5),
    s1 DECIMAL(10,5),
    s2 DECIMAL(10,5),
    s3 DECIMAL(10,5),

    -- Pattern detected
    pattern VARCHAR(50),

    -- Metadata
    scan_id INTEGER,
    alerted BOOLEAN DEFAULT FALSE
);

-- Signal outcomes table - tracks what happened to signals
CREATE TABLE IF NOT EXISTS signal_outcomes (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES signals(id),
    outcome VARCHAR(10),  -- WIN/LOSS/OPEN/EXPIRED
    close_price DECIMAL(10,5),
    pips_gained DECIMAL(10,2),
    profit_loss DECIMAL(10,2),
    closed_at TIMESTAMP,
    duration_hours INTEGER,
    notes TEXT
);

-- Daily performance table - daily aggregate stats
CREATE TABLE IF NOT EXISTS daily_performance (
    date DATE PRIMARY KEY,
    total_signals INTEGER DEFAULT 0,
    signals_taken INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    total_pips DECIMAL(10,2),
    total_profit DECIMAL(10,2),
    max_drawdown DECIMAL(10,2),
    best_trade DECIMAL(10,2),
    worst_trade DECIMAL(10,2),
    average_confidence DECIMAL(5,2)
);

-- Strategy performance table - performance by strategy
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy VARCHAR(50) NOT NULL,
    period VARCHAR(20),  -- 'daily', 'weekly', 'monthly', 'all_time'
    start_date DATE,
    end_date DATE,
    total_signals INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    average_pips DECIMAL(10,2),
    total_profit DECIMAL(10,2),
    average_confidence DECIMAL(5,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Instrument performance table - performance by instrument
CREATE TABLE IF NOT EXISTS instrument_performance (
    id SERIAL PRIMARY KEY,
    instrument VARCHAR(20) NOT NULL,
    period VARCHAR(20),
    start_date DATE,
    end_date DATE,
    total_signals INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    average_pips DECIMAL(10,2),
    total_profit DECIMAL(10,2),
    best_strategy VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trades table - actual trades taken
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER REFERENCES signals(id),
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    instrument VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- BUY/SELL
    entry_price DECIMAL(10,5) NOT NULL,
    stop_loss DECIMAL(10,5) NOT NULL,
    take_profit DECIMAL(10,5) NOT NULL,
    position_size DECIMAL(10,2) NOT NULL,
    risk_amount DECIMAL(10,2) NOT NULL,
    risk_percent DECIMAL(5,2) NOT NULL,

    -- Outcome
    closed_at TIMESTAMP,
    close_price DECIMAL(10,5),
    outcome VARCHAR(10),  -- WIN/LOSS/BREAKEVEN/OPEN
    pips_gained DECIMAL(10,2),
    profit_loss DECIMAL(10,2),

    -- Account tracking
    account_balance_before DECIMAL(12,2),
    account_balance_after DECIMAL(12,2),

    -- Notes
    notes TEXT
);

-- Account tracking table - daily account snapshots
CREATE TABLE IF NOT EXISTS account_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    account_balance DECIMAL(12,2) NOT NULL,
    daily_pnl DECIMAL(10,2),
    total_pnl DECIMAL(10,2),
    drawdown_percent DECIMAL(5,2),
    trades_today INTEGER DEFAULT 0,
    win_rate_today DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_signals_instrument ON signals(instrument);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_confidence ON signals(confidence);
CREATE INDEX IF NOT EXISTS idx_outcomes_signal_id ON signal_outcomes(signal_id);
CREATE INDEX IF NOT EXISTS idx_trades_instrument ON trades(instrument);
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at);

-- Create views for easy querying

-- View: High confidence signals
CREATE OR REPLACE VIEW high_confidence_signals AS
SELECT
    s.*,
    o.outcome
FROM signals s
LEFT JOIN signal_outcomes o ON s.id = o.signal_id
WHERE s.confidence >= 70
ORDER BY s.timestamp DESC;

-- View: Recent performance (last 30 days)
CREATE OR REPLACE VIEW recent_performance AS
SELECT
    strategy,
    COUNT(*) as total_signals,
    SUM(CASE WHEN o.outcome = 'WIN' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN o.outcome = 'LOSS' THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN o.outcome IN ('WIN', 'LOSS') THEN
        CASE WHEN o.outcome = 'WIN' THEN 1.0 ELSE 0.0 END
    END) * 100, 2) as win_rate,
    ROUND(AVG(s.confidence), 2) as avg_confidence
FROM signals s
LEFT JOIN signal_outcomes o ON s.id = o.signal_id
WHERE s.timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY strategy;

-- Sample query functions

-- Function to calculate win rate for a strategy
CREATE OR REPLACE FUNCTION get_strategy_win_rate(strategy_name VARCHAR)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    win_rate DECIMAL(5,2);
BEGIN
    SELECT
        COALESCE(
            ROUND(
                AVG(CASE WHEN o.outcome IN ('WIN', 'LOSS') THEN
                    CASE WHEN o.outcome = 'WIN' THEN 1.0 ELSE 0.0 END
                END) * 100,
                2
            ),
            0
        )
    INTO win_rate
    FROM signals s
    LEFT JOIN signal_outcomes o ON s.id = o.signal_id
    WHERE s.strategy = strategy_name
        AND s.timestamp >= CURRENT_DATE - INTERVAL '90 days';

    RETURN win_rate;
END;
$$ LANGUAGE plpgsql;

-- Usage examples:
-- SELECT * FROM high_confidence_signals LIMIT 10;
-- SELECT * FROM recent_performance;
-- SELECT get_strategy_win_rate('ma_cross');
