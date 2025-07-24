import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def plot_trades(df):
    fig = go.Figure()

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    # EMA Short
    if 'EMA_Short' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA_Short'],
            mode='lines',
            line=dict(color='orange', width=1.5),
            name='EMA Short'
        ))

    # EMA Long
    if 'EMA_Long' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA_Long'],
            mode='lines',
            line=dict(color='blue', width=1.5),
            name='EMA Long'
        ))

    # Entry signals
    entries = df.dropna(subset=['Trade Entry Price'])
    fig.add_trace(go.Scatter(
        x=entries.index,
        y=entries['Trade Entry Price'],
        mode='markers',
        marker=dict(color='orange', size=14, symbol='triangle-up'),
        name='Buy Entries',
        legendgroup='buys'
    ))

    # Exit signals
    exits = df.dropna(subset=['Trade Exit Price'])
    fig.add_trace(go.Scatter(
        x=exits.index,
        y=exits['Trade Exit Price'],
        mode='markers',
        marker=dict(color='blue', size=14, symbol='triangle-down'),
        name='Sell Exits',
        legendgroup='sells'
    ))

    # Stop-loss exits
    stops = df[df['Exit Reason'] == 'Stop Loss']
    fig.add_trace(go.Scatter(
        x=stops.index,
        y=stops['Trade Exit Price'],
        mode='markers+text',
        marker=dict(color='red', size=10, symbol='x'),
        text=['SL'] * len(stops),
        textposition='top center',
        name='Stop Loss'
    ))

    # Clean up index
    df.index = pd.to_datetime(df.index, errors='coerce')
    df = df[df.index >= df.index[0]]
    df = df[~df.index.isna()]
    df = df.sort_index()

    x_range = [df.index.min(), df.index.max()]

    # Layout settings
    fig.update_layout(
        title="Backtest Trades",
        xaxis_title="Time",
        yaxis_title="Price",
        height=600,
        xaxis=dict(
            rangeslider_visible=True,
            range=x_range,
        )
    )

    st.plotly_chart(fig, use_container_width=True)
