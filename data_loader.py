import yfinance as yf
import pandas as pd

class DataLoaderYF:
    def __init__(self, symbol="EURUSD=X", start="2019-01-01", end="2024-12-31", interval="1d"):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.interval = interval
        self.data = None

    def _fetch_data(self):
        try:
            df = yf.download(self.symbol, start=self.start, end=self.end, interval=self.interval, progress=False)

            if df.empty:
                raise ValueError(f"No data returned for {self.symbol} between {self.start} and {self.end}")

            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
            df.index.name = 'Date'

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            self.data = df
            return self.data

        except Exception as e:
            print(f"[DataLoader] Error fetching data: {e}")
            return pd.DataFrame()

    def get_data(self):
        if self.data is None:
            return self._fetch_data()
        return self.data

import pandas as pd

class DataLoaderTW:
    def __init__(self, filepath, time_col="time"):
        self.filepath = filepath
        self.time_col = time_col
        self.data = None

    def _load_csv(self):
        df = pd.read_csv(self.filepath)

        # Convert 'time' column from UNIX timestamp to datetime
        df[self.time_col] = pd.to_datetime(df[self.time_col], unit='s')

        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)

        df.set_index(self.time_col, inplace=True)

        # df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        df.index.name = 'Date'

        self.data = df
        return self.data

    def get_data(self):
        if self.data is None:
            return self._load_csv()
        return self.data
