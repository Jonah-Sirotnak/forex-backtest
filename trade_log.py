import pandas as pd

class TradeLog:
    def __init__(self, df: pd.DataFrame, capital: float, position_pct: float):
        self.df = df
        self.capital = capital
        self.position_pct = position_pct

    def generate(self) -> pd.DataFrame:
        df = self.df.copy()
        trades = df.dropna(subset=['Trade Exit Price']).copy()

        trades['Exit Time'] = trades.index
        trades['Entry Time'] = None
        trades['Entry Index'] = None
        trades['Exit Index'] = None
        trades['Trade Entry Price'] = None
        trades['Position Size'] = None

        for i in range(len(trades)):
            exit_time = trades.index[i]

            # Find last known entry before this exit
            entry_row = df.loc[:exit_time].dropna(subset=['Trade Entry Price']).tail(1)
            if not entry_row.empty:
                entry_time = entry_row.index[0]
                entry_index = df.index.get_loc(entry_time)
                exit_index = df.index.get_loc(exit_time)

                trades.at[exit_time, 'Entry Time'] = entry_time
                trades.at[exit_time, 'Entry Index'] = entry_index
                trades.at[exit_time, 'Exit Index'] = exit_index

                entry_price = entry_row['Trade Entry Price'].values[0]
                trades.at[exit_time, 'Trade Entry Price'] = entry_price
                trades.at[exit_time, 'Position Size'] = entry_row['Position Size'].values[0]

                lows_during_trade = df.iloc[entry_index:exit_index+1]['Low']
                min_low = lows_during_trade.min()
                drawdown_pct = ((min_low - entry_price) / entry_price) * 100
                trades.at[exit_time, 'Max Drawdown (%)'] = drawdown_pct

        # Duration and R multiple
        trades['Duration (days)'] = trades['Exit Index'] - trades['Entry Index']
        risk_per_trade = self.capital * self.position_pct
        trades['R Multiple'] = trades['ProfitLoss'] / risk_per_trade

        return trades[[
            'Entry Time',
            'Exit Time',
            'Trade Entry Price',
            'Trade Exit Price',
            'Trade Return',
            'ProfitLoss',
            'R Multiple',
            'Position Size',
            'Equity',
            'Max Drawdown (%)',
            'Duration (days)'
        ]]
