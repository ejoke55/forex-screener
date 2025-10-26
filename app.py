"""
V3 Forex Screener - Flask Web Dashboard
Main application with MA Cross, MA Pullback, Technical Analysis, and News tabs
"""
import sys
import os
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screener_v3 import V3ForexScreener
from utils.news_fetcher import NewsFetcher
from utils.risk_calculator import RiskCalculator
from notifications import TelegramNotifier
from config.api_config import TELEGRAM_ENABLED, MIN_CONFIDENCE_THRESHOLD

app = Flask(__name__)

# Global storage for latest results
latest_results = {
    'screener_results': {},
    'news': {},
    'last_update': None,
    'scanning': False,
    'scan_count': 0
}

# Alert tracking to prevent spam
# Format: {instrument: {'signal': 'BUY', 'confidence': 75, 'timestamp': datetime}}
alert_history = {}
ALERT_COOLDOWN_MINUTES = 60  # Only re-alert same signal after 1 hour

# Initialize components
screener = V3ForexScreener()
news_fetcher = NewsFetcher()
risk_calculator = RiskCalculator()
telegram = TelegramNotifier() if TELEGRAM_ENABLED else None

def background_scanner():
    """Run screener in background every 5 minutes"""
    while True:
        try:
            latest_results['scanning'] = True
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting background scan...")

            # Run screener
            results = screener.scan_all_instruments()
            latest_results['screener_results'] = results
            latest_results['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            latest_results['scan_count'] += 1

            # Fetch news (every 3rd scan to reduce API calls)
            if latest_results['scan_count'] % 3 == 0:
                try:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching news...")
                    news = news_fetcher.fetch_all_news()
                    latest_results['news'] = news
                except Exception as e:
                    print(f"[ERROR] News fetch failed: {str(e)}")

            # Send Telegram alerts for high-confidence signals
            if telegram:
                send_high_confidence_alerts(results)

            latest_results['scanning'] = False

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan complete! Next scan in 5 minutes...")

            # Wait 5 minutes
            time.sleep(300)

        except Exception as e:
            print(f"[ERROR] Background scan failed: {str(e)}")
            import traceback
            traceback.print_exc()
            latest_results['scanning'] = False
            time.sleep(60)  # Wait 1 minute before retry

def send_high_confidence_alerts(results):
    """Send Telegram alerts for signals above confidence threshold (with deduplication)"""
    current_time = datetime.now()

    for instrument, data in results.items():
        confidence = data.get('best_confidence', 0)
        signal = data.get('overall_signal', 'NEUTRAL')

        # Only alert on BUY/SELL signals above confidence threshold
        if confidence >= MIN_CONFIDENCE_THRESHOLD and ('BUY' in signal or 'SELL' in signal):

            # Check if we should send alert (avoid spam)
            should_alert = False

            if instrument not in alert_history:
                # First time seeing this instrument - send alert
                should_alert = True
                reason = "NEW"
            else:
                last_alert = alert_history[instrument]
                last_signal = last_alert['signal']
                last_confidence = last_alert['confidence']
                last_time = last_alert['timestamp']
                time_diff_minutes = (current_time - last_time).total_seconds() / 60

                # Alert if signal changed (BUY → SELL or vice versa)
                if signal != last_signal:
                    should_alert = True
                    reason = "SIGNAL_CHANGE"

                # Alert if confidence increased significantly (+15% or more)
                elif confidence >= last_confidence + 15:
                    should_alert = True
                    reason = "CONFIDENCE_BOOST"

                # Alert if cooldown period passed (1 hour)
                elif time_diff_minutes >= ALERT_COOLDOWN_MINUTES:
                    should_alert = True
                    reason = "COOLDOWN_EXPIRED"

            if should_alert:
                # Send alert
                message = format_alert_message(instrument, data)
                success = telegram.send_message(message)

                if success:
                    # Update alert history
                    alert_history[instrument] = {
                        'signal': signal,
                        'confidence': confidence,
                        'timestamp': current_time
                    }
                    print(f"[ALERT] {instrument}: {signal} {confidence}% ({reason})")
            else:
                print(f"[SKIP] {instrument}: {signal} {confidence}% (already alerted)")

def format_alert_message(instrument, data):
    """Format Telegram alert message"""
    confidence = data['best_confidence']
    signal = data['overall_signal']
    strategy = data['best_strategy']
    current_price = data['technical_analysis'].get('current_price', 'N/A')

    # Determine signal type
    if 'BUY' in signal:
        emoji = "🟢"
        direction = "BUY"
    elif 'SELL' in signal:
        emoji = "🔴"
        direction = "SELL"
    else:
        emoji = "⚪"
        direction = "NEUTRAL"

    message = f"""
<b>{emoji} {direction} SIGNAL - {instrument}</b>

<b>Confidence:</b> {confidence}%
<b>Strategy:</b> {strategy}
<b>Signal:</b> {signal}
<b>Current Price:</b> {current_price}

<b>Timeframes:</b>
M5: {format_tf(data['sma'].get('M5', 0))}
M15: {format_tf(data['sma'].get('M15', 0))}
H1: {format_tf(data['sma'].get('H1', 0))}
H4: {format_tf(data['sma'].get('H4', 0))}
D1: {format_tf(data['sma'].get('D', 0))}

⏰ {data['timestamp']}
"""

    return message

def format_tf(value):
    """Format timeframe value"""
    if value > 0:
        return "✅ UP"
    elif value < 0:
        return "❌ DOWN"
    else:
        return "⚠️ MIXED"

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/results')
def get_results():
    """API endpoint to get latest screener results"""
    # Remove DataFrames from results before serializing to JSON
    clean_results = {
        'screener_results': {},
        'news': latest_results.get('news', {}),
        'last_update': latest_results.get('last_update'),
        'scanning': latest_results.get('scanning', False),
        'scan_count': latest_results.get('scan_count', 0)
    }

    # Copy screener results without data_dict (which contains DataFrames)
    for instrument, data in latest_results.get('screener_results', {}).items():
        clean_data = {k: v for k, v in data.items() if k != 'data_dict'}
        clean_results['screener_results'][instrument] = clean_data

    return jsonify(clean_results)

@app.route('/api/instrument/<instrument>')
def get_instrument_details(instrument):
    """Get detailed analysis for specific instrument"""
    results = latest_results.get('screener_results', {}).get(instrument, {})

    if not results:
        return jsonify({'error': 'Instrument not found'}), 404

    # Remove data_dict (DataFrames) before serializing
    clean_results = {k: v for k, v in results.items() if k != 'data_dict'}
    return jsonify(clean_results)

@app.route('/api/news')
def get_news():
    """Get news categorized by pairs"""
    return jsonify(latest_results.get('news', {}))

@app.route('/api/risk_calculate', methods=['POST'])
def calculate_risk():
    """Calculate risk for a trade"""
    data = request.json

    try:
        entry = float(data['entry'])
        stop_loss = float(data['stop_loss'])
        take_profit = float(data.get('take_profit', 0))
        instrument = data.get('instrument', 'EURUSD')

        # If no TP provided, calculate with 2:1 R:R
        if take_profit == 0:
            take_profit = risk_calculator.calculate_take_profit(entry, stop_loss, 2.0)

        recommendation = risk_calculator.get_trade_recommendation(
            entry, stop_loss, take_profit, instrument
        )

        return jsonify(recommendation)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/scan')
def trigger_scan():
    """Manually trigger a scan"""
    if not latest_results['scanning']:
        threading.Thread(target=run_single_scan, daemon=True).start()
        return jsonify({'status': 'Scan started'})
    else:
        return jsonify({'status': 'Scan already in progress'})

def run_single_scan():
    """Run a single scan cycle"""
    latest_results['scanning'] = True

    try:
        results = screener.scan_all_instruments()
        latest_results['screener_results'] = results
        latest_results['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"[ERROR] Scan failed: {str(e)}")

    latest_results['scanning'] = False

def run_initial_scan():
    """Run one scan before starting the server"""
    print("\n[INFO] Running initial scan...")
    latest_results['scanning'] = True

    try:
        results = screener.scan_all_instruments()
        latest_results['screener_results'] = results
        latest_results['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[OK] Initial scan complete: {len(results)} instruments analyzed")

        # Fetch news
        try:
            news = news_fetcher.fetch_all_news()
            latest_results['news'] = news
            print(f"[OK] News fetched")
        except:
            print(f"[WARN] News fetch failed (continuing without news)")

    except Exception as e:
        print(f"[ERROR] Initial scan failed: {str(e)}")

    latest_results['scanning'] = False

if __name__ == '__main__':
    print("=" * 80)
    print("V3 FOREX SCREENER WEB DASHBOARD")
    print("=" * 80)
    print("\nStarting web server...")

    # Run initial scan
    run_initial_scan()

    # Start background scanner
    scanner_thread = threading.Thread(target=background_scanner, daemon=True)
    scanner_thread.start()

    print("\n[OK] Dashboard ready!")
    print("\nOpen your browser and go to:")
    print("\n    http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 80)

    # Start Flask app
    # Use PORT from environment (Render sets this) or default to 5000 for local
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
