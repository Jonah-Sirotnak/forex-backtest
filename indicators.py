import pandas as pd

class IndicatorCalculator:
    def __init__(self, short_period=9, long_period=21):
        self.short_period = short_period
        self.long_period = long_period

    def apply_ema_crossover(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Calculate EMAs
        df['EMA_Short'] = df['Close'].iloc[self.short_period:].ewm(span=self.short_period, adjust=False).mean()
        df['EMA_Long'] = df['Close'].iloc[self.long_period:].ewm(span=self.long_period, adjust=False).mean()

        # Generate signals
        df['Signal'] = 0
        df['Signal'][self.short_period:] = (
            (df['EMA_Short'][self.short_period:] > df['EMA_Long'][self.short_period:]) &
            (df['EMA_Short'].shift(1)[self.short_period:] <= df['EMA_Long'].shift(1)[self.short_period:])
        ).astype(int)

        df['Signal'][self.short_period:] -= (
            (df['EMA_Short'][self.short_period:] < df['EMA_Long'][self.short_period:]) &
            (df['EMA_Short'].shift(1)[self.short_period:] >= df['EMA_Long'].shift(1)[self.short_period:])
        ).astype(int)

        return df
