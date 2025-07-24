import pandas as pd
import numpy as np

class PerformanceStats:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.trades = df.dropna(subset=['Trade Exit Price'])

    def compute(self):
        trades = self.trades
        equity = self.df['Equity'].dropna()
        initial_capital = equity.iloc[0] if len(equity) > 0 else 0
        final_equity = equity.iloc[-1] if len(equity) > 0 else 0  
        total_pnl = final_equity - initial_capital
        print(equity.values[-1])

        num_trades = len(trades)
        wins = trades[trades['ProfitLoss'] > 0]

        win_rate = len(wins) / num_trades if num_trades > 0 else 0
        avg_pl = trades['ProfitLoss'].mean() if num_trades > 0 else 0

        returns = equity.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 1 else 0
        max_dd = (equity / equity.cummax() - 1).min()

        return {
            "Initial Capital": f"${initial_capital:,.2f}",
            "Final Equity": f"${final_equity:,.2f}",
            "Total PnL": f"${total_pnl:,.2f}",
            "Total Trades": num_trades,
            "Win Rate": f"{win_rate * 100:.2f}%",
            "Avg P/L per Trade": f"${avg_pl:,.2f}",
            "Sharpe Ratio": f"{sharpe_ratio:.4f}",
            "Max Drawdown": f"{max_dd * 100:.2f}%",
        }