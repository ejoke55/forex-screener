"""
yfinance Connector for fetching index/commodity data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_config import CANDLE_COUNT, REQUEST_DELAY
from config.instruments import YFINANCE_TIMEFRAME_MAP


class YFinanceConnector:
    def __init__(self):
        pass

    def get_candles(self, symbol, timeframe, count=CANDLE_COUNT):
        """
        Fetch historical candles from yfinance

        Args:
            symbol (str): yfinance symbol (e.g., '^N225', 'GC=F')
            timeframe (str): Timeframe (e.g., 'M5', 'H1', 'D')
            count (int): Number of candles to fetch

        Returns:
            pd.DataFrame: DataFrame with OHLC data
        """
        try:
            # Map timeframe
            interval = YFINANCE_TIMEFRAME_MAP.get(timeframe, '1h')

            # Calculate period based on interval and count
            period = self._calculate_period(interval, count)

            # Fetch data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df is None or len(df) == 0:
                print(f"[WARN] No data returned for {symbol} {timeframe}")
                return None

            # Rename columns to match OANDA format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Select only needed columns
            df = df[['open', 'high', 'low', 'close', 'volume']]

            # Take last 'count' candles
            df = df.tail(count)

            # Add delay to respect rate limits
            time.sleep(REQUEST_DELAY * 2)  # yfinance is more sensitive

            return df

        except Exception as e:
            print(f"[ERROR] Failed to fetch {symbol} {timeframe}: {str(e)}")
            return None

    def _calculate_period(self, interval, count):
        """Calculate period string based on interval and desired count"""
        # Mapping of intervals to approximate days needed
        interval_days = {
            '5m': count * 5 / (60 * 24),
            '15m': count * 15 / (60 * 24),
            '30m': count * 30 / (60 * 24),
            '1h': count * 1 / 24,
            '4h': count * 4 / 24,
            '1d': count,
        }

        days = interval_days.get(interval, count)

        # yfinance period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        if days <= 5:
            return '5d'
        elif days <= 30:
            return '1mo'
        elif days <= 90:
            return '3mo'
        elif days <= 180:
            return '6mo'
        elif days <= 365:
            return '1y'
        elif days <= 730:
            return '2y'
        else:
            return '5y'

    def test_connection(self):
        """Test yfinance connection"""
        try:
            # Try fetching a simple ticker
            ticker = yf.Ticker('^GSPC')
            info = ticker.info

            if info and 'symbol' in info:
                print("[OK] yfinance connection successful")
                return True
            else:
                print("[WARN] yfinance connection issue")
                return False
        except Exception as e:
            print(f"[ERROR] yfinance connection error: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the connector
    print("Testing yfinance Connector...")
    connector = YFinanceConnector()

    # Test connection
    connector.test_connection()

    # Test data fetch
    print("\nFetching Nikkei (^N225) 1H data...")
    df = connector.get_candles('^N225', 'H1', count=100)
    if df is not None:
        print(f"[OK] Fetched {len(df)} candles")
        print(df.tail())
    else:
        print("[ERROR] Failed to fetch data")

    print("\nFetching Gold (GC=F) 1H data...")
    df = connector.get_candles('GC=F', 'H1', count=100)
    if df is not None:
        print(f"[OK] Fetched {len(df)} candles")
        print(df.tail())
    else:
        print("[ERROR] Failed to fetch data")
