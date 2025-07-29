import yfinance as yf
import pandas as pd

class DataLoaderYF:
    """
    Yahoo Finance data loader
    """
    def __init__(self, symbol="EURUSD=X", start="2019-01-01", end="2024-12-31", interval="1d"):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.interval = interval
        self.data = None

    def _fetch_data(self):
        """
        Fetch and clean data from Yahoo Finance.
        """
        try:
            # Download data from Yahoo Finance
            df = yf.download(self.symbol, start=self.start, end=self.end, interval=self.interval, progress=False)

            if df.empty:
                raise ValueError(f"No data returned for {self.symbol} between {self.start} and {self.end}")

            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
            df.index.name = 'Date'

            # Handle MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            self.data = df
            return self.data

        except Exception as e:
            print(f"[DataLoader] Error fetching data: {e}")
            return pd.DataFrame()

    def get_data(self):
        """
        Get data with lazy loading (fetch only if not cached).
        """
        if self.data is None:
            return self._fetch_data()
        return self.data

import pandas as pd

class DataLoaderTW:
    """
    TradingView CSV data loader for local files.
    """
    def __init__(self, filepath, time_col="time"):
        self.filepath = filepath
        self.time_col = time_col
        self.data = None

    def _load_csv(self):
        """
        Load and process CSV data from TradingView export.
        """
        df = pd.read_csv(self.filepath)

        # Convert UNIX timestamp to datetime
        df[self.time_col] = pd.to_datetime(df[self.time_col], unit='s')

        # Add 7 hours to simulate UTC+7 (Vietnam time)
        df[self.time_col] = df[self.time_col] + pd.Timedelta(hours=7)

        # Standardize column names to match Yahoo Finance format
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)

        # Set datetime as index
        df.set_index(self.time_col, inplace=True)

        # df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        df.index.name = 'Date'

        self.data = df
        return self.data

    def get_data(self):
        """
        Get data with lazy loading (load only if not cached).
        """
        if self.data is None:
            return self._load_csv()
        return self.data
