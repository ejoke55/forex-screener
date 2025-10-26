"""
News Fetcher Module for V3
Fetches relevant forex news that may impact the 11 FTMO pairs
"""
import requests
import json
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import NEWS_API_KEY, FOREX_FACTORY_URL
from config.instruments import OANDA_PAIRS, YFINANCE_INSTRUMENTS


class NewsFetcher:
    def __init__(self, news_api_key=None):
        self.news_api_key = news_api_key or NEWS_API_KEY
        self.forex_factory_url = FOREX_FACTORY_URL

    def get_forex_factory_calendar(self):
        """
        Fetch economic calendar from Forex Factory

        Returns:
            list: Economic events for this week
        """
        try:
            response = requests.get(self.forex_factory_url, timeout=10)

            if response.status_code == 200:
                events = response.json()

                # Filter for high impact events
                high_impact_events = [
                    event for event in events
                    if event.get('impact') == 'High'
                ]

                return high_impact_events[:20]  # Return top 20 high impact events
            else:
                print(f"[WARN] Forex Factory API error: {response.status_code}")
                return []

        except Exception as e:
            print(f"[ERROR] Failed to fetch Forex Factory calendar: {str(e)}")
            return []

    def get_currency_news(self, currencies=['USD', 'EUR', 'GBP', 'JPY', 'AUD']):
        """
        Get latest news for specific currencies

        Args:
            currencies: List of currency codes

        Returns:
            list: News articles
        """
        if not self.news_api_key:
            return []

        try:
            # Build query
            query = ' OR '.join(currencies)

            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': f'{query} AND (forex OR economy OR central bank)',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'from': (datetime.now() - timedelta(days=1)).isoformat(),
                'apiKey': self.news_api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                print(f"[WARN] News API error: {response.status_code}")
                return []

        except Exception as e:
            print(f"[ERROR] Failed to fetch news: {str(e)}")
            return []

    def get_commodity_news(self):
        """Get news for commodities (Gold, Oil)"""
        if not self.news_api_key:
            return []

        try:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': '(gold OR oil OR crude) AND (price OR trading)',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': (datetime.now() - timedelta(days=1)).isoformat(),
                'apiKey': self.news_api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])
            else:
                return []

        except Exception as e:
            print(f"[ERROR] Failed to fetch commodity news: {str(e)}")
            return []

    def categorize_news_by_pairs(self, news_articles, economic_events):
        """
        Categorize news by which pairs they might affect

        Args:
            news_articles: List of news articles
            economic_events: List of economic events

        Returns:
            dict: News organized by instrument
        """
        pair_news = {}

        # Initialize with all FTMO pairs
        for pair in OANDA_PAIRS:
            pair_news[pair.replace('_', '')] = []

        # Add yfinance instruments
        for _, symbol, name in YFINANCE_INSTRUMENTS:
            pair_news[symbol] = []

        # Categorize news articles
        for article in news_articles:
            title = article.get('title', '').upper()
            description = article.get('description', '').upper() if article.get('description') else ''

            # Check which currencies are mentioned
            for pair in OANDA_PAIRS:
                clean_pair = pair.replace('_', '')
                base = clean_pair[:3]
                quote = clean_pair[3:]

                if base in title or base in description or quote in title or quote in description:
                    pair_news[clean_pair].append({
                        'title': article.get('title'),
                        'source': article.get('source', {}).get('name'),
                        'published_at': article.get('publishedAt'),
                        'url': article.get('url'),
                        'type': 'news'
                    })

            # Check commodities
            if 'GOLD' in title or 'GOLD' in description:
                pair_news['XAUUSD'].append({
                    'title': article.get('title'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt'),
                    'url': article.get('url'),
                    'type': 'news'
                })

            if 'OIL' in title or 'CRUDE' in title or 'OIL' in description:
                pair_news['WTI'].append({
                    'title': article.get('title'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt'),
                    'url': article.get('url'),
                    'type': 'news'
                })

        # Categorize economic events
        for event in economic_events:
            country = event.get('country', '')
            title = event.get('title', '')

            # Map countries to currencies
            currency_map = {
                'USD': ['EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD'],
                'EUR': ['EURUSD', 'EURAUD'],
                'GBP': ['GBPUSD', 'GBPJPY', 'GBPAUD'],
                'JPY': ['USDJPY', 'AUDJPY', 'GBPJPY'],
                'AUD': ['AUDUSD', 'EURAUD', 'AUDJPY', 'GBPAUD'],
            }

            for curr, pairs in currency_map.items():
                if curr in country.upper():
                    for pair in pairs:
                        pair_news[pair].append({
                            'title': title,
                            'source': 'Forex Factory',
                            'published_at': event.get('date'),
                            'impact': event.get('impact'),
                            'type': 'economic_event'
                        })

        # Limit to 5 most recent per pair
        for pair in pair_news:
            pair_news[pair] = pair_news[pair][:5]

        return pair_news

    def fetch_all_news(self):
        """
        Fetch all news and categorize by pairs

        Returns:
            dict: News organized by instrument
        """
        print("[INFO] Fetching forex news...")

        # Fetch news
        currency_news = self.get_currency_news()
        commodity_news = self.get_commodity_news()
        economic_events = self.get_forex_factory_calendar()

        all_articles = currency_news + commodity_news

        # Categorize
        categorized_news = self.categorize_news_by_pairs(all_articles, economic_events)

        print(f"[OK] Fetched {len(all_articles)} articles and {len(economic_events)} events")

        return categorized_news


if __name__ == "__main__":
    # Test news fetcher
    print("Testing News Fetcher...")
    print("Note: Requires NEWS_API_KEY environment variable for full functionality\n")

    fetcher = NewsFetcher()

    # Test Forex Factory calendar
    print("Fetching Forex Factory calendar...")
    events = fetcher.get_forex_factory_calendar()
    print(f"[OK] Fetched {len(events)} high-impact economic events")

    if events:
        print("\nSample events:")
        for event in events[:3]:
            print(f"  - {event.get('title')} ({event.get('country')})")

    # If NEWS_API_KEY is set, test news fetching
    if fetcher.news_api_key:
        print("\nFetching currency news...")
        news = fetcher.get_currency_news()
        print(f"[OK] Fetched {len(news)} news articles")

        if news:
            print("\nSample articles:")
            for article in news[:3]:
                print(f"  - {article.get('title')}")
    else:
        print("\n[INFO] Set NEWS_API_KEY environment variable to test news fetching")
        print("[INFO] Get free API key from https://newsapi.org/")
