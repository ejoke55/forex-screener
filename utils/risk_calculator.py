"""
Risk Calculator for V3
FTMO-compliant risk management for 100K account
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import ACCOUNT_SIZE, RISK_PER_TRADE, MAX_DAILY_LOSS, MAX_TOTAL_LOSS


class RiskCalculator:
    def __init__(self, account_balance=None, risk_percent=None):
        self.account_balance = account_balance or ACCOUNT_SIZE
        self.risk_percent = risk_percent or RISK_PER_TRADE
        self.max_daily_loss_percent = MAX_DAILY_LOSS
        self.max_total_loss_percent = MAX_TOTAL_LOSS

    def calculate_position_size(self, entry_price, stop_loss, instrument='EURUSD'):
        """
        Calculate FTMO-compliant position size

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            instrument: Trading instrument (for pip value calculation)

        Returns:
            dict: Position sizing details
        """
        risk_amount = self.account_balance * (self.risk_percent / 100)
        sl_distance = abs(entry_price - stop_loss)

        # Calculate pip value (varies by instrument)
        if 'JPY' in instrument:
            # JPY pairs: 1 pip = 0.01
            pips = sl_distance * 100
            pip_value = 10  # For standard lot
        elif 'XAU' in instrument or 'GOLD' in instrument:
            # Gold: 1 pip = 0.10
            pips = sl_distance * 10
            pip_value = 10
        elif 'WTI' in instrument or 'OIL' in instrument:
            # Oil: 1 pip = 0.01
            pips = sl_distance * 100
            pip_value = 10
        elif 'NAS' in instrument:
            # NAS100: 1 pip = 0.10
            pips = sl_distance * 10
            pip_value = 1
        else:
            # Standard forex pairs: 1 pip = 0.0001
            pips = sl_distance * 10000
            pip_value = 10  # For standard lot

        # Calculate lot size
        position_size = risk_amount / (pips * pip_value) if pips > 0 else 0

        # Round to 2 decimal places
        position_size = round(position_size, 2)

        # Calculate actual risk amount with rounded position size
        actual_risk = position_size * pips * pip_value

        return {
            'position_size_lots': position_size,
            'risk_amount': round(actual_risk, 2),
            'sl_distance_pips': round(pips, 1),
            'pip_value': pip_value,
            'risk_percent': round((actual_risk / self.account_balance) * 100, 2),
            'entry_price': entry_price,
            'stop_loss': stop_loss
        }

    def calculate_take_profit(self, entry_price, stop_loss, reward_risk_ratio=2.0):
        """
        Calculate take profit based on R:R ratio

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            reward_risk_ratio: Reward:Risk ratio (default 2:1)

        Returns:
            float: Take profit price
        """
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = sl_distance * reward_risk_ratio

        # Determine if long or short
        if entry_price > stop_loss:
            # Long position
            take_profit = entry_price + tp_distance
        else:
            # Short position
            take_profit = entry_price - tp_distance

        return round(take_profit, 5)

    def calculate_daily_loss_limit(self, trades_today):
        """
        Calculate remaining daily loss limit

        Args:
            trades_today: List of dict with 'pnl' key for each trade today

        Returns:
            dict: Daily loss tracking
        """
        max_loss_amount = self.account_balance * (self.max_daily_loss_percent / 100)

        # Calculate total PnL for today
        total_pnl = sum(trade.get('pnl', 0) for trade in trades_today)

        remaining_loss = max_loss_amount + total_pnl  # total_pnl is negative for losses

        return {
            'max_daily_loss': max_loss_amount,
            'current_pnl': total_pnl,
            'remaining_loss_limit': remaining_loss,
            'percent_used': round(((max_loss_amount - remaining_loss) / max_loss_amount) * 100, 2),
            'can_trade': remaining_loss > 0
        }

    def calculate_total_loss_limit(self, account_current_balance):
        """
        Calculate remaining total loss limit (FTMO max drawdown)

        Args:
            account_current_balance: Current account balance

        Returns:
            dict: Total loss tracking
        """
        max_loss_amount = self.account_balance * (self.max_total_loss_percent / 100)
        total_loss = self.account_balance - account_current_balance

        remaining_loss = max_loss_amount - total_loss

        return {
            'initial_balance': self.account_balance,
            'current_balance': account_current_balance,
            'max_total_loss': max_loss_amount,
            'current_loss': total_loss,
            'remaining_loss_limit': remaining_loss,
            'percent_used': round((total_loss / max_loss_amount) * 100, 2),
            'can_trade': remaining_loss > 0
        }

    def get_trade_recommendation(self, entry_price, stop_loss, take_profit, instrument='EURUSD'):
        """
        Get complete trade recommendation with risk metrics

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            instrument: Trading instrument

        Returns:
            dict: Complete trade recommendation
        """
        position_info = self.calculate_position_size(entry_price, stop_loss, instrument)

        # Calculate R:R ratio
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = abs(take_profit - entry_price)
        rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0

        # Calculate potential profit
        potential_profit = position_info['position_size_lots'] * (tp_distance * 10000) * position_info['pip_value']

        return {
            'instrument': instrument,
            'entry': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_info['position_size_lots'],
            'risk_amount': position_info['risk_amount'],
            'potential_profit': round(potential_profit, 2),
            'rr_ratio': round(rr_ratio, 2),
            'sl_pips': position_info['sl_distance_pips'],
            'tp_pips': round((tp_distance * 10000 if 'JPY' not in instrument else tp_distance * 100), 1),
            'risk_percent': position_info['risk_percent']
        }


if __name__ == "__main__":
    # Test risk calculator
    print("Testing Risk Calculator...")
    print(f"Account Size: ${ACCOUNT_SIZE:,}")
    print(f"Risk per Trade: {RISK_PER_TRADE}%\n")

    calculator = RiskCalculator()

    # Test EURUSD trade
    test_entry = 1.0850
    test_sl = 1.0820
    test_tp = calculator.calculate_take_profit(test_entry, test_sl, reward_risk_ratio=2.0)

    recommendation = calculator.get_trade_recommendation(
        entry_price=test_entry,
        stop_loss=test_sl,
        take_profit=test_tp,
        instrument='EURUSD'
    )

    print("=" * 60)
    print("TRADE RECOMMENDATION - EURUSD")
    print("=" * 60)
    print(f"Entry: {recommendation['entry']}")
    print(f"Stop Loss: {recommendation['stop_loss']} ({recommendation['sl_pips']} pips)")
    print(f"Take Profit: {recommendation['take_profit']} ({recommendation['tp_pips']} pips)")
    print(f"Position Size: {recommendation['position_size']} lots")
    print(f"Risk Amount: ${recommendation['risk_amount']:.2f} ({recommendation['risk_percent']}%)")
    print(f"Potential Profit: ${recommendation['potential_profit']:.2f}")
    print(f"R:R Ratio: 1:{recommendation['rr_ratio']}")
    print("=" * 60)
