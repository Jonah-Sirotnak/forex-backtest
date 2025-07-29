import streamlit as st
from data_loader import DataLoaderYF, DataLoaderTW
from indicators import IndicatorCalculator
from position_sizer import PositionSizer
from risk_manager import RiskManager
from backtester import Backtester
from stats import PerformanceStats
from plot import plot_trades
from trade_log import TradeLog
import pandas as pd

st.set_page_config(layout="wide")
st.title("📈 Forex Strategy Backtester")

run_backtest = st.sidebar.button("Run Backtest", type='secondary', icon='🚀', use_container_width=True)

# --- Sidebar: Mode Selection ---
st.sidebar.header("Strategy Settings")
mode = st.sidebar.selectbox(
    "Select Strategy",
    ["Choose a strategy", "YFinance (EMA)", "TradingView (EMA)", "TradingView (Keltner)"]
)

# --- Mode-specific Inputs ---
if mode == "YFinance (EMA)":
    capital = st.sidebar.number_input("Initial Capital", value=100000)
    symbol = st.sidebar.text_input("Symbol (e.g., EURUSD=X)", value="EURUSD=X")
    start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2019-01-01"))
    end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))
    interval = st.sidebar.selectbox("Interval", ["1h", "1d"], index=1)
    short_ema = st.sidebar.number_input("Short EMA", min_value=1, max_value=100, value=9)
    long_ema = st.sidebar.number_input("Long EMA", min_value=1, max_value=200, value=21)

elif mode == "TradingView (EMA)":
    capital = st.sidebar.number_input("Initial Capital", value=100000)
    short_ema = st.sidebar.number_input("Short EMA", min_value=1, max_value=100, value=9)
    long_ema = st.sidebar.number_input("Long EMA", min_value=1, max_value=200, value=21)

elif mode == "TradingView (Keltner)":
    capital = st.sidebar.number_input("Initial Capital", value=100000)
    length_ema = st.sidebar.number_input("Length EMA", min_value=1, max_value=100, value=15)
    length_atr = st.sidebar.number_input("Length ATR", min_value=1, max_value=100, value=14)
    volatility_factor = st.sidebar.slider("Volatility Factor (ATR Multiplier)", 0.1, 5.0, 1.0, 0.1)
    initial_risk = st.sidebar.slider("% Initial Risk", 0.0, 10.0, 1.0, 0.1) / 100
    risk_equity = st.sidebar.slider("% Risk Equity", 0.0, 10.0, 1.0, 0.1) / 100

# --- Common Settings ---
if mode != "Choose a strategy":
    stop_loss_type = st.sidebar.selectbox("Stop Loss Type", ["fixed", "trailing"], index=0)
    skid = st.sidebar.slider("SKID (slippage factor)", 0.0, 1.0, 1.0, 0.1)
    position_pct = st.sidebar.slider("Position Size %", 0.001, 1.0, 0.01, 0.001)
    stop_loss_pct = st.sidebar.slider("Stop Loss %", 0.0, 1.0, 0.25, 0.01)

# --- Run Backtest ---
if run_backtest and mode != "Choose a strategy":
    with st.spinner("Running backtest..."):

        # --- Load Data ---
        if mode == "YFinance (EMA)":
            loader = DataLoaderYF(symbol, str(start_date), str(end_date), interval)
        else:
            loader = DataLoaderTW("../data/tradingview_CMC_EURUSD.csv", time_col="time")

        df = loader.get_data()
        print(f"Data loaded: {len(df)} rows")

        # --- Apply Indicators ---
        if mode in ["YFinance (EMA)", "TradingView (EMA)"]:
            ind = IndicatorCalculator(short_period=short_ema, long_period=long_ema)
            df = ind.apply_ema_crossover(df)
        elif mode == "TradingView (Keltner)":
            # ind = IndicatorCalculator(kc_period=kc_period, kc_multiplier=kc_mult)
            # df = ind.apply_keltner_channel(df)
            pass

        sizer = PositionSizer(position_pct=position_pct)
        risk_manager = RiskManager(stop_loss_pct=stop_loss_pct, stop_loss_type=stop_loss_type)

        # --- Run Backtest ---
        bt = Backtester(df, initial_capital=capital, skid=skid, risk_manager=risk_manager, position_sizer=sizer)
        results = bt.run_backtest()

        # --- Show Results ---
        st.subheader("📊 Performance Summary")
        stats = PerformanceStats(results).compute()
        st.table(stats)

        st.subheader("📈 Trade Chart")
        plot_trades(results)

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
elif mode == "Choose a strategy":
    st.sidebar.warning("Please select a strategy and click 'Run Backtest' to see results.")
    if run_backtest:
        st.toast("Please select a strategy first before running the backtest.", icon="🚨")