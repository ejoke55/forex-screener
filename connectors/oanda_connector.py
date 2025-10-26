"""
OANDA API Connector for fetching forex data
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_config import OANDA_API_KEY, OANDA_ACCOUNT_ID, OANDA_BASE_URL, CANDLE_COUNT, REQUEST_DELAY
from config.instruments import OANDA_TIMEFRAME_MAP


class OandaConnector:
    def __init__(self, api_key=None, account_id=None):
        self.api_key = api_key or OANDA_API_KEY
        self.account_id = account_id or OANDA_ACCOUNT_ID
        self.base_url = OANDA_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def get_candles(self, instrument, timeframe, count=CANDLE_COUNT):
        """
        Fetch historical candles from OANDA

        Args:
            instrument (str): OANDA instrument (e.g., 'EUR_USD')
            timeframe (str): Timeframe (e.g., 'M5', 'H1', 'D')
            count (int): Number of candles to fetch

        Returns:
            pd.DataFrame: DataFrame with OHLC data
        """
        try:
            # Map timeframe
            granularity = OANDA_TIMEFRAME_MAP.get(timeframe, timeframe)

            # Build request
            endpoint = f"{self.base_url}/v3/instruments/{instrument}/candles"
            params = {
                'granularity': granularity,
                'count': count,
                'price': 'M'  # Mid prices
            }

            # Make request
            response = requests.get(endpoint, headers=self.headers, params=params)

            if response.status_code != 200:
                print(f"[ERROR] OANDA API error for {instrument} {timeframe}: {response.status_code}")
                return None

            data = response.json()

            if 'candles' not in data or len(data['candles']) == 0:
                print(f"[WARN] No candles returned for {instrument} {timeframe}")
                return None

            # Parse candles
            candles = []
            for candle in data['candles']:
                if candle['complete']:
                    candles.append({
                        'time': pd.to_datetime(candle['time']),
                        'open': float(candle['mid']['o']),
                        'high': float(candle['mid']['h']),
                        'low': float(candle['mid']['l']),
                        'close': float(candle['mid']['c']),
                        'volume': int(candle['volume'])
                    })

            df = pd.DataFrame(candles)
            df.set_index('time', inplace=True)

            # Add delay to respect rate limits
            time.sleep(REQUEST_DELAY)

            return df

        except Exception as e:
            print(f"[ERROR] Failed to fetch {instrument} {timeframe}: {str(e)}")
            return None

    def test_connection(self):
        """Test OANDA API connection"""
        try:
            endpoint = f"{self.base_url}/v3/accounts/{self.account_id}"
            response = requests.get(endpoint, headers=self.headers)

            if response.status_code == 200:
                print("[OK] OANDA connection successful")
                return True
            else:
                print(f"[ERROR] OANDA connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] OANDA connection error: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the connector
    print("Testing OANDA Connector...")
    connector = OandaConnector()

    # Test connection
    connector.test_connection()

    # Test data fetch
    print("\nFetching EUR_USD H1 data...")
    df = connector.get_candles('EUR_USD', 'H1', count=100)
    if df is not None:
        print(f"[OK] Fetched {len(df)} candles")
        print(df.tail())
    else:
        print("[ERROR] Failed to fetch data")
