import pandas as pd
import numpy as np

class IndicatorCalculator:
    def __init__(self, short_period=9, long_period=21):
        self.short_period = short_period
        self.long_period = long_period

    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """
        Manually calculates the Exponential Moving Average (EMA).
        Uses the recursive formula:
            EMA_t = alpha * price_t + (1 - alpha) * EMA_{t-1}
        Where:
            alpha = 2 / (period + 1)
        """
        ema = np.zeros(len(series))
        alpha = 2 / (period + 1)

        ema[0] = series.iloc[0]
        for i in range(1, len(series)):
            ema[i] = alpha * series.iloc[i] + (1 - alpha) * ema[i - 1]

        ema_series = pd.Series(ema, index=series.index)
        ema_series[:period-1] = None
        return ema_series

    def apply_ema_crossover(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df['EMA_Short'] = self.calculate_ema(df['Close'], self.short_period)
        df['EMA_Long'] = self.calculate_ema(df['Close'], self.long_period)

        df['Signal'] = 0
        idx = df.index[self.short_period:]

        buy_signal = (
            (df['EMA_Short'] > df['EMA_Long']) &
            (df['EMA_Short'].shift(1) <= df['EMA_Long'].shift(1))
        )

        sell_signal = (
            (df['EMA_Short'] < df['EMA_Long']) &
            (df['EMA_Short'].shift(1) >= df['EMA_Long'].shift(1))
        )

        df.loc[idx, 'Signal'] = np.where(buy_signal.loc[idx], 1,
                                np.where(sell_signal.loc[idx], -1, 0))

        df.loc[df.index[:self.long_period - 1], 'Signal'] = 0

        return df
