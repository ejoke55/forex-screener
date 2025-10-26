"""
V3 Forex Screener - Main Application
Optimized for 11 FTMO instruments with SMA strategies
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.instruments import OANDA_PAIRS, YFINANCE_INSTRUMENTS, TIMEFRAMES, get_display_name
from config.api_config import CANDLE_COUNT
from connectors.oanda_connector import OandaConnector
from connectors.yfinance_connector import YFinanceConnector
from strategies.sma_strategy import SMAStrategy
from strategies.ma_cross_strategy import MACrossStrategy
from strategies.ma_pullback_strategy import MAPullbackStrategy
from strategies.supertrend_mtf import SupertrendStrategy
from utils.confidence_scorer import ConfidenceScorer
from utils.risk_calculator import RiskCalculator
from utils.technical_analysis import TechnicalAnalyzer


class V3ForexScreener:
    def __init__(self):
        # Initialize connectors
        self.oanda = OandaConnector()
        self.yfinance = YFinanceConnector()

        # Initialize strategies
        self.sma_strategy = SMAStrategy()
        self.ma_cross_strategy = MACrossStrategy()
        self.ma_pullback_strategy = MAPullbackStrategy()
        self.supertrend_strategy = SupertrendStrategy()

        # Initialize utilities
        self.confidence_scorer = ConfidenceScorer()
        self.risk_calculator = RiskCalculator()
        self.technical_analyzer = TechnicalAnalyzer()

    def fetch_data(self, instrument, source='oanda'):
        """
        Fetch multi-timeframe data for an instrument

        Args:
            instrument: Instrument symbol
            source: 'oanda' or 'yfinance'

        Returns:
            dict: {timeframe: DataFrame}
        """
        data_dict = {}

        for tf in TIMEFRAMES:
            try:
                if source == 'oanda':
                    df = self.oanda.get_candles(instrument, tf, count=CANDLE_COUNT)
                else:
                    df = self.yfinance.get_candles(instrument, tf, count=CANDLE_COUNT)

                data_dict[tf] = df
            except Exception as e:
                print(f"[ERROR] Failed to fetch {instrument} {tf}: {str(e)}")
                data_dict[tf] = None

        return data_dict

    def analyze_instrument(self, instrument, source='oanda'):
        """
        Comprehensive analysis of an instrument

        Args:
            instrument: Instrument symbol
            source: Data source

        Returns:
            dict: Complete analysis results
        """
        display_name = get_display_name(instrument)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing {display_name}...")

        # Fetch data
        data_dict = self.fetch_data(instrument, source)

        # Run strategies
        sma_results = self.sma_strategy.analyze_timeframes(data_dict)
        ma_cross_results = self.ma_cross_strategy.analyze_timeframes(data_dict)
        ma_pullback_results = self.ma_pullback_strategy.analyze_timeframes(data_dict)
        supertrend_results = self.supertrend_strategy.analyze_timeframes(data_dict)

        # Calculate confidence scores for each strategy
        sma_confidence = self.confidence_scorer.calculate_confidence(
            sma_results,
            ma_cross_results,
            ma_pullback_results,
            data_dict.get('H4'),
            'sma_trend'
        )

        ma_cross_confidence = self.confidence_scorer.calculate_confidence(
            ma_cross_results,
            ma_cross_results,
            ma_pullback_results,
            data_dict.get('H4'),
            'ma_cross'
        )

        ma_pullback_confidence = self.confidence_scorer.calculate_confidence(
            ma_pullback_results,
            ma_cross_results,
            ma_pullback_results,
            data_dict.get('H4'),
            'ma_pullback'
        )

        # Technical analysis
        technical_analysis = self.technical_analyzer.analyze_instrument(data_dict, display_name)

        # Compile results
        results = {
            'instrument': display_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_dict': data_dict,

            # Strategy results
            'sma': sma_results,
            'ma_cross': ma_cross_results,
            'ma_pullback': ma_pullback_results,
            'supertrend': supertrend_results,

            # Confidence scores
            'sma_confidence': sma_confidence,
            'ma_cross_confidence': ma_cross_confidence,
            'ma_pullback_confidence': ma_pullback_confidence,

            # Technical analysis
            'technical_analysis': technical_analysis,

            # Overall signal (based on highest confidence strategy)
            'best_strategy': None,
            'best_confidence': 0,
            'overall_signal': 'NEUTRAL',
        }

        # Determine best strategy
        confidence_scores = [
            ('SMA Trend', sma_confidence['confidence'], sma_results.get('overall', 'NEUTRAL')),
            ('MA Cross', ma_cross_confidence['confidence'], ma_cross_results.get('overall', 'NEUTRAL')),
            ('MA Pullback', ma_pullback_confidence['confidence'], ma_pullback_results.get('overall', 'NEUTRAL')),
        ]

        best = max(confidence_scores, key=lambda x: x[1])
        results['best_strategy'] = best[0]
        results['best_confidence'] = best[1]
        results['overall_signal'] = best[2]

        return results

    def scan_all_instruments(self):
        """
        Scan all 11 FTMO instruments

        Returns:
            dict: {instrument: results}
        """
        print("\n" + "=" * 80)
        print(f"V3 FOREX SCREENER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print(f"Scanning 11 FTMO instruments...")
        print("=" * 80 + "\n")

        all_results = {}

        # Scan OANDA pairs
        for pair in OANDA_PAIRS:
            try:
                results = self.analyze_instrument(pair, source='oanda')
                display_name = results['instrument']
                all_results[display_name] = results

                # Print summary
                signal = results['overall_signal']
                confidence = results['best_confidence']
                strategy = results['best_strategy']

                print(f"  ✓ {display_name}: {signal} ({strategy}, {confidence}% confidence)")

            except Exception as e:
                print(f"  ✗ {pair}: ERROR - {str(e)}")

        # Scan yfinance instruments
        for yf_symbol, standard_symbol, name in YFINANCE_INSTRUMENTS:
            try:
                results = self.analyze_instrument(yf_symbol, source='yfinance')
                results['instrument'] = standard_symbol  # Use standard symbol
                all_results[standard_symbol] = results

                # Print summary
                signal = results['overall_signal']
                confidence = results['best_confidence']
                strategy = results['best_strategy']

                print(f"  ✓ {standard_symbol}: {signal} ({strategy}, {confidence}% confidence)")

            except Exception as e:
                print(f"  ✗ {standard_symbol}: ERROR - {str(e)}")

        print("\n" + "=" * 80)
        print(f"Scan complete! Analyzed {len(all_results)} instruments")
        print("=" * 80 + "\n")

        return all_results


if __name__ == "__main__":
    print("V3 Forex Screener - Testing Mode")
    print("=" * 80)

    screener = V3ForexScreener()

    # Test single instrument
    print("\n[TEST] Analyzing EURUSD...")
    results = screener.analyze_instrument('EUR_USD', source='oanda')

    print(f"\n[RESULTS] {results['instrument']}")
    print(f"Overall Signal: {results['overall_signal']}")
    print(f"Best Strategy: {results['best_strategy']} ({results['best_confidence']}% confidence)")
    print(f"\nSMA: {results['sma']['overall']} (Score: {results['sma']['score']})")
    print(f"MA Cross: {results['ma_cross']['overall']} (Score: {results['ma_cross']['score']})")
    print(f"MA Pullback: {results['ma_pullback']['overall']} (Score: {results['ma_pullback']['score']})")

    if results['technical_analysis']['daily_pivots']:
        print(f"\nDaily Pivot: {results['technical_analysis']['daily_pivots']['PP']}")
        print(f"Resistance: R1={results['technical_analysis']['daily_pivots']['R1']}, R2={results['technical_analysis']['daily_pivots']['R2']}")
        print(f"Support: S1={results['technical_analysis']['daily_pivots']['S1']}, S2={results['technical_analysis']['daily_pivots']['S2']}")
