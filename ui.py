import streamlit as st
# from data_loader import DataLoaderYF
from data_loader import DataLoaderTW
from indicators import IndicatorCalculator
from backtester import Backtester
from stats import PerformanceStats
from plot import plot_trades
from trade_log import TradeLog
import pandas as pd

st.set_page_config(layout="wide")

st.title("📈 Forex Strategy Backtester")
run_backtest = st.sidebar.button("Run Backtest", type='secondary', icon='🚀', use_container_width=True)

# Sidebar config
st.sidebar.header("Strategy Settings")
symbol = st.sidebar.text_input("Symbol (e.g., EURUSD=X)", value="EURUSD=X")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2019-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))
interval = st.sidebar.selectbox("Interval", ["1h", "1d"], index=1)

short_ema = st.sidebar.number_input("Short EMA", min_value=1, max_value=100, value=9)
long_ema = st.sidebar.number_input("Long EMA", min_value=1, max_value=200, value=21)
skid = st.sidebar.slider("SKID (slippage factor)", 0.0, 1.0, 1.0, 0.1)
capital = st.sidebar.number_input("Initial Capital", value=100000)
position_pct = st.sidebar.slider("Position Size %", 0.001, 1.0, 0.01, 0.001)
stop_loss_pct = st.sidebar.slider("Stop Loss %", 0.0, 1.0, 0.25, 0.01)


if run_backtest:
    with st.spinner("Running backtest..."):

        # Load + preprocess
        # loader = DataLoaderYF(symbol, str(start_date), str(end_date), interval)
        loader = DataLoaderTW("../data/tradingview_CMC_EURUSD.csv", time_col="time")
        df = loader.get_data()
        print(f"Data loaded: {len(df)} rows")
        ind = IndicatorCalculator(short_ema, long_ema)
        df = ind.apply_ema_crossover(df)

        sizer = PositionSizer(initial_capital=capital, position_pct=position_pct, skid=skid)
        df = sizer.apply(df)

        bt = Backtester(df, initial_capital=capital, skid=skid, stop_loss_pct=stop_loss_pct)
        results = bt.run_backtest()

        stats = PerformanceStats(results).compute()

        # Show stats
        st.subheader("📊 Performance Summary")
        st.table(stats)

        # Show chart
        st.subheader("📈 Trade Chart")
        plot_trades(results)

        # Show trade log
        st.subheader("📒 Trade Log")
        
        trade_log_df = TradeLog(results, capital, position_pct).generate()

        st.dataframe(trade_log_df.style.format({
            'Trade Entry Price': '{:.5f}',
            'Trade Exit Price': '{:.5f}',
            'Trade Return': '{:.2%}',
            'ProfitLoss': '${:,.2f}',
            'R Multiple': '{:.2f}',
            'Equity': '${:,.2f}'
        }, na_rep='-'))