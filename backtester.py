import pandas as pd
from risk_manager import RiskManager
from position_sizer import PositionSizer

class Backtester:
    """
    Trading strategy backtester with risk management and position sizing.
    """
    def __init__(self, df: pd.DataFrame, initial_capital=100000, skid=1.0, risk_manager: RiskManager=None, position_sizer: PositionSizer=None):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.skid = skid
        self.risk_manager = risk_manager
        self.position_sizer = position_sizer

    def run_backtest(self):
        """
        Execute the backtest simulation with entry/exit logic and risk management.
        """
        df = self.df
        
        # Initialize tracking columns
        df['Trade Entry Price'] = None
        df['Trade Exit Price'] = None
        df['Exit Reason'] = None
        df['Trade Return'] = 0.0
        df['ProfitLoss'] = 0.0
        df['Equity'] = self.initial_capital
        df['Equity'] = df['Equity'].astype(float)

        # Track portfolio state
        equity = self.initial_capital
        in_position = False
        entry_index = None
        entry_price = None
        position_size = None
        stop_price = None

        for i in range(len(df) - 1):
            signal = df.iloc[i]['Signal']

            # Entry Logic: Look for buy signals when flat
            if not in_position and signal == 1:
                # Calculate entry price with slippage
                next_open = df.iloc[i + 1]['Open']
                next_high = df.iloc[i + 1]['High']
                entry_price = next_open + self.skid * abs(next_high - next_open)

                # Calculate position size and stop loss
                capital = df.iloc[i]['Equity']
                allocated = self.position_sizer.calculate(entry_price, capital)
                position_size = allocated / entry_price
                stop_price = self.risk_manager.get_stop_price(entry_price)

                # Record entry details
                entry_index = i + 1
                df.at[df.index[entry_index], 'Trade Entry Price'] = entry_price
                df.at[df.index[entry_index], 'Trade Direction'] = "Buy"
                df.at[df.index[entry_index], 'Position Size'] = position_size

                in_position = True

            # Exit Logic: Handle stop losses and exit signals when in position
            elif in_position and signal == -1:
                current_low = df.iloc[i]['Low']
                current_high = df.iloc[i]['High']
                
                # Update trailing stop if applicable
                if self.risk_manager.get_stop_loss_type() == 'trailing':
                    stop_price = self.risk_manager.update_trailing_stop(stop_price, current_high)

                # Check for stop-loss hit
                if self.risk_manager.check_stop(current_low, stop_price):
                    exit_price = stop_price
                    trade_return = (exit_price - entry_price) / entry_price
                    profit = trade_return * position_size * entry_price
                    equity += profit
                    
                    # Record stop loss exit
                    df.at[df.index[i], 'Trade Exit Price'] = exit_price
                    df.at[df.index[i], 'Trade Return'] = trade_return
                    df.at[df.index[i], 'ProfitLoss'] = profit
                    df.at[df.index[i], 'Equity'] = equity
                    df.at[df.index[i], 'Exit Reason'] = 'Stop Loss'
                    
                    # Reset position state
                    in_position = False
                    entry_index = None
                    entry_price = None
                    position_size = None
                    stop_price = None
                    continue

                # Exit on signal
                if signal == -1:
                    # Calculate exit price with slippage
                    next_open = df.iloc[i + 1]['Open']
                    next_low = df.iloc[i + 1]['Low']
                    exit_price = next_open - self.skid * abs(next_open - next_low)
                    trade_return = (exit_price - entry_price) / entry_price
                    profit = trade_return * position_size * entry_price
                    equity += profit

                    # Record signal exit
                    exit_index = i + 1
                    df.at[df.index[exit_index], 'Trade Exit Price'] = exit_price
                    df.at[df.index[exit_index], 'Trade Return'] = trade_return
                    df.at[df.index[exit_index], 'ProfitLoss'] = profit
                    df.at[df.index[exit_index], 'Equity'] = equity
                    df.at[df.index[exit_index], 'Exit Reason'] = 'Signal'
                    
                    # Reset position state
                    in_position = False
                    entry_index = None
                    entry_price = None
                    position_size = None
                    stop_price = None
            else:
                # Update equity when no action taken
                df.at[df.index[i], 'Equity'] = equity

        # Ensure final equity is recorded
        df.at[df.index[-1], 'Equity'] = equity
        self.df = df
        return df
