"""
Notification system for Forex Screener
Supports: Telegram, Discord, Email, Desktop notifications
"""
import sys
import os
import requests
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TelegramNotifier:
    """Send notifications via Telegram bot"""

    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message):
        """Send a message to Telegram"""
        if not self.bot_token or not self.chat_id:
            print("[WARN] Telegram credentials not configured")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                print("[OK] Telegram message sent!")
                return True
            else:
                print(f"[ERROR] Telegram error: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to send Telegram: {str(e)}")
            return False

    def send_signal(self, symbol, score, trend, timeframes):
        """Send a formatted trading signal"""
        signal_type = "🟢 BUY" if score > 0 else "🔴 SELL"
        strength = "🔥 STRONG" if abs(score) >= 5 else "MODERATE"

        message = f"""
<b>{strength} {signal_type} SIGNAL</b>

📊 <b>Symbol:</b> {symbol}
📈 <b>Score:</b> {score}/6
🎯 <b>Trend:</b> {trend}

<b>Timeframes:</b>
M5: {self._format_tf(timeframes.get('M5', 0))}
M15: {self._format_tf(timeframes.get('M15', 0))}
M30: {self._format_tf(timeframes.get('M30', 0))}
H1: {self._format_tf(timeframes.get('H1', 0))}
H4: {self._format_tf(timeframes.get('H4', 0))}
D1: {self._format_tf(timeframes.get('D', 0))}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def _format_tf(self, value):
        """Format timeframe value"""
        if value > 0:
            return "✅ UP"
        elif value < 0:
            return "❌ DOWN"
        else:
            return "⚠️ MIXED"


class DiscordNotifier:
    """Send notifications via Discord webhook"""

    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv('DISCORD_WEBHOOK_URL')

    def send_message(self, message, title="Forex Screener Alert"):
        """Send a message to Discord"""
        if not self.webhook_url:
            print("[WARN] Discord webhook not configured")
            return False

        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 3447003,  # Blue
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }

            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 204:
                print("[OK] Discord message sent!")
                return True
            else:
                print(f"[ERROR] Discord error: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] Failed to send Discord: {str(e)}")
            return False

    def send_signal(self, symbol, score, trend, timeframes):
        """Send a formatted trading signal"""
        signal_type = "BUY 🟢" if score > 0 else "SELL 🔴"
        strength = "🔥 STRONG" if abs(score) >= 5 else "MODERATE"
        color = 3066993 if score > 0 else 15158332  # Green or Red

        tf_text = "\n".join([
            f"M5: {self._format_tf(timeframes.get('M5', 0))}",
            f"M15: {self._format_tf(timeframes.get('M15', 0))}",
            f"M30: {self._format_tf(timeframes.get('M30', 0))}",
            f"H1: {self._format_tf(timeframes.get('H1', 0))}",
            f"H4: {self._format_tf(timeframes.get('H4', 0))}",
            f"D1: {self._format_tf(timeframes.get('D', 0))}"
        ])

        data = {
            "embeds": [{
                "title": f"{strength} {signal_type} - {symbol}",
                "color": color,
                "fields": [
                    {"name": "Score", "value": f"{score}/6", "inline": True},
                    {"name": "Trend", "value": trend, "inline": True},
                    {"name": "Timeframes", "value": tf_text, "inline": False}
                ],
                "footer": {"text": "Forex Multi-Timeframe Screener"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            print(f"[ERROR] Discord send failed: {str(e)}")
            return False

    def _format_tf(self, value):
        """Format timeframe value"""
        if value > 0:
            return "✅ UP"
        elif value < 0:
            return "❌ DOWN"
        else:
            return "⚠️ MIXED"


class DesktopNotifier:
    """Send desktop notifications (Windows/Mac/Linux)"""

    def __init__(self):
        self.available = self._check_availability()

    def _check_availability(self):
        """Check if desktop notifications are available"""
        try:
            if sys.platform == 'win32':
                from win10toast import ToastNotifier
                return True
            elif sys.platform == 'darwin':
                return True  # macOS
            else:
                return True  # Linux with notify-send
        except:
            return False

    def send_notification(self, title, message):
        """Send desktop notification"""
        if not self.available:
            print("[WARN] Desktop notifications not available")
            return False

        try:
            if sys.platform == 'win32':
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    title,
                    message,
                    duration=10,
                    threaded=True
                )
                return True

            elif sys.platform == 'darwin':
                # macOS
                os.system(f"""
                    osascript -e 'display notification "{message}" with title "{title}"'
                """)
                return True

            else:
                # Linux
                os.system(f'notify-send "{title}" "{message}"')
                return True

        except Exception as e:
            print(f"[ERROR] Desktop notification failed: {str(e)}")
            return False

    def send_signal(self, symbol, score, signal_type):
        """Send a signal notification"""
        title = f"Trading Signal: {symbol}"
        message = f"{signal_type} - Score: {score}/6"
        return self.send_notification(title, message)


class NotificationManager:
    """Manage all notification channels"""

    def __init__(self, telegram=True, discord=True, desktop=True):
        self.notifiers = []

        if telegram:
            tg = TelegramNotifier()
            if tg.bot_token and tg.chat_id:
                self.notifiers.append(('Telegram', tg))

        if discord:
            dc = DiscordNotifier()
            if dc.webhook_url:
                self.notifiers.append(('Discord', dc))

        if desktop:
            dn = DesktopNotifier()
            if dn.available:
                self.notifiers.append(('Desktop', dn))

        print(f"[INFO] Notification channels: {[n[0] for n in self.notifiers]}")

    def send_signal(self, symbol, score, trend, timeframes):
        """Send signal to all configured channels"""
        success_count = 0

        for name, notifier in self.notifiers:
            try:
                if notifier.send_signal(symbol, score, trend, timeframes):
                    success_count += 1
            except Exception as e:
                print(f"[ERROR] {name} notification failed: {str(e)}")

        return success_count > 0

    def send_batch_signals(self, signals):
        """Send multiple signals"""
        for symbol, info in signals:
            score = info.get('score', 0)
            trend = info.get('trend', 'MIXED')
            self.send_signal(symbol, score, trend, info)


# Test functions
def test_telegram():
    """Test Telegram notifications"""
    print("\n=== Testing Telegram ===")
    print("Set environment variables:")
    print("  export TELEGRAM_BOT_TOKEN='your_bot_token'")
    print("  export TELEGRAM_CHAT_ID='your_chat_id'")

    notifier = TelegramNotifier()
    if notifier.bot_token and notifier.chat_id:
        notifier.send_signal(
            'EUR/USD',
            6,
            'STRONG UP',
            {'M5': 1, 'M15': 1, 'M30': 1, 'H1': 1, 'H4': 1, 'D': 1}
        )
    else:
        print("[WARN] Telegram not configured")


def test_discord():
    """Test Discord notifications"""
    print("\n=== Testing Discord ===")
    print("Set environment variable:")
    print("  export DISCORD_WEBHOOK_URL='your_webhook_url'")

    notifier = DiscordNotifier()
    if notifier.webhook_url:
        notifier.send_signal(
            'GBP/USD',
            -5,
            'STRONG DOWN',
            {'M5': -1, 'M15': -1, 'M30': -1, 'H1': -1, 'H4': -1, 'D': 0}
        )
    else:
        print("[WARN] Discord not configured")


def test_desktop():
    """Test desktop notifications"""
    print("\n=== Testing Desktop Notifications ===")

    notifier = DesktopNotifier()
    if notifier.available:
        notifier.send_signal('USD/JPY', 4, '🟢 BUY')
    else:
        print("[WARN] Desktop notifications not available")


if __name__ == "__main__":
    print("=" * 60)
    print("NOTIFICATION SYSTEM TEST")
    print("=" * 60)

    test_telegram()
    test_discord()
    test_desktop()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
