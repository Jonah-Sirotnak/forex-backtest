import pandas as pd

class Backtester:
    def __init__(self, df: pd.DataFrame, initial_capital=100000, skid=1.0, stop_loss_pct=0.25, position_size=0.01):
        self.df = df.copy()
        self.initial_capital = initial_capital
        self.skid = skid
        self.stop_loss_pct = stop_loss_pct
        self.position_size = position_size

    def run_backtest(self):
        df = self.df
        df['Trade Entry Price'] = None
        df['Trade Exit Price'] = None
        df['Exit Reason'] = None
        df['Trade Return'] = 0.0
        df['ProfitLoss'] = 0.0
        df['Equity'] = self.initial_capital

        equity = self.initial_capital
        in_position = False
        entry_index = None
        last_exit_index = None
        entry_price = None
        position_size = None
        stop_price = None
        last_equity = None

        for i in range(len(df) - 1):
            signal = df.iloc[i]['Signal']

            # If not in position and we have a buy signal
            if not in_position and signal == 1:
                next_open = df.iloc[i + 1]['Open']
                next_high = df.iloc[i + 1]['High']
                entry_price = next_open + self.skid * abs(next_high - next_open)

                capital = df.iloc[i]['Equity']
                allocated = capital * self.position_size
                position_size = allocated / entry_price
                stop_price = entry_price * (1 - self.stop_loss_pct)

                entry_index = i + 1
                df.at[df.index[entry_index], 'Trade Entry Price'] = entry_price
                df.at[df.index[entry_index], 'Trade Direction'] = "Buy"
                df.at[df.index[entry_index], 'Position Size'] = position_size

                in_position = True

            elif in_position:
                current_low = df.iloc[i]['Low']
                
                # Check for stop-loss
                if current_low <= stop_price:
                    exit_price = stop_price
                    trade_return = (exit_price - entry_price) / entry_price
                    profit = trade_return * position_size * entry_price
                    equity += profit
                    last_equity = equity
                    
                    df.at[df.index[i], 'Trade Exit Price'] = exit_price
                    df.at[df.index[i], 'Trade Return'] = trade_return
                    df.at[df.index[i], 'ProfitLoss'] = profit
                    df.at[df.index[i], 'Equity'] = equity
                    df.at[df.index[i], 'Exit Reason'] = 'Stop Loss'
                    
                    last_exit_index = i
                    in_position = False
                    entry_index = None
                    entry_price = None
                    position_size = None
                    stop_price = None
                    continue

                # Check for exit signal    
                if signal == -1:
                    next_open = df.iloc[i + 1]['Open']
                    next_low = df.iloc[i + 1]['Low']
                    exit_price = next_open - self.skid * abs(next_open - next_low)
                    trade_return = (exit_price - entry_price) / entry_price
                    profit = trade_return * position_size * entry_price
                    equity += profit
                    last_equity = equity

                    exit_index = i + 1
                    last_exit_index = exit_index
                    df.at[df.index[exit_index], 'Trade Exit Price'] = exit_price
                    df.at[df.index[exit_index], 'Trade Return'] = trade_return
                    df.at[df.index[exit_index], 'ProfitLoss'] = profit
                    df.at[df.index[exit_index], 'Equity'] = equity
                    df.at[df.index[exit_index], 'Exit Reason'] = 'Signal'
                    in_position = False
                    entry_index = None
                    entry_price = None
                    position_size = None
                    stop_price = None

            else:
                df.at[df.index[i], 'Equity'] = equity

        df['Equity'].iloc[last_exit_index:] = last_equity if last_exit_index is not None else equity
        self.df = df
        return df
