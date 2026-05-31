# -*- coding: utf-8 -*-
"""TriSignal — Multi-indicator Algorithmic Trading Strategy
   Indicators: Bollinger Bands | OBV | RSI
   Asset: AAPL (2016–2023) | Benchmark: SPY
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import statistics
import plotly.graph_objects as go
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

plt.style.use('fivethirtyeight')


# ── 1. Download Data ──────────────────────────────────────────────────────────
asset = 'AAPL'
data = yf.download(asset, interval='1d', start='2016-10-01', end='2023-10-04')
df = data.copy()
print(df)


# ── 2. Candlestick Chart ──────────────────────────────────────────────────────
figure = go.Figure(
    data=[
        go.Candlestick(
            x=df.index,
            low=df['Low'],
            high=df['High'],
            close=df['Close'],
            open=df['Open'],
            increasing_line_color='green',
            decreasing_line_color='red'
        )
    ]
)
figure.update_layout(
    title='Apple Price',
    yaxis_title='Apple Stock Price($)',
    xaxis_title='Date'
)
figure.show()


# ── 3. Closing Price Plot ─────────────────────────────────────────────────────
plt.figure(figsize=(14, 5))
plt.plot(df['Close'], color='magenta', label='Closing price')
plt.xlabel('Date')
plt.ylabel('Close price USD($)')
plt.xticks(rotation=45)
plt.title("Closing price V/s Date")
plt.show()


# ── 4. Bollinger Bands ────────────────────────────────────────────────────────
# Midband = 30-day Simple Moving Average of Close price
df['Midband'] = df['Close'].rolling(window=30).mean()

# Standard deviation over 30 days
df['st_d'] = df['Close'].rolling(window=30).std()

# Upper band = Midband + 1.5 * std  →  overbought zone
df['Ub'] = df['Midband'] + 1.5 * df['st_d']

# Lower band = Midband - 1.5 * std  →  oversold zone
df['Lb'] = df['Midband'] - 1.5 * df['st_d']

print(df)

plt.figure(figsize=(14, 5))
plt.fill_between(df.index, df['Ub'], df['Lb'], color='lightsteelblue')
plt.plot(df['Midband'], color='crimson',   lw=3, label='Midband')
plt.plot(df['Ub'],      color='darkorchid', lw=3, label='UpperBand')
plt.plot(df['Lb'],      color='lime',       lw=3, label='LowerBand')
plt.plot(df['Close'],   color='magenta',         label='Closing price', alpha=0.5)
plt.title("Visual representation of Bands")
plt.legend(loc='lower right')
plt.xlabel('Date')
plt.ylabel('Close price USD($)')
plt.show()


# ── 5. On-Balance Volume (OBV) ────────────────────────────────────────────────
def obv(data):
    """
    Cumulative volume indicator.
    Adds volume on up-days, subtracts on down-days.
    Rising OBV = buying pressure. Falling OBV = selling pressure.
    """
    OBV = [0]
    for i in range(1, len(data['Close'])):
        if data['Close'].iloc[i] > data['Close'].iloc[i - 1]:
            OBV.append(OBV[-1] + data['Volume'].iloc[i])
        elif data['Close'].iloc[i] < data['Close'].iloc[i - 1]:
            OBV.append(OBV[-1] - data['Volume'].iloc[i])
        else:
            OBV.append(OBV[-1])

    data['OBV'] = OBV
    # 20-day EMA of OBV — signals bullish/bearish crossover
    data['OBV_EMA'] = data['OBV'].ewm(span=20).mean()
    return data


obv(df)

plt.figure(figsize=(12, 6))
plt.plot(df['OBV'],     label='OBV',     color='lawngreen')
plt.plot(df['OBV_EMA'], label='OBV_EMA', color='midnightblue')
plt.legend(loc='lower left')
plt.title("OBV and its 20-day EMA")
plt.show()


# ── 6. RSI (Relative Strength Index) ─────────────────────────────────────────
def RSI(data):
    """
    Momentum indicator (0–100).
    Above 90 → overbought (potential sell).
    Below 30 → oversold  (potential buy).
    Uses 16-day EMA of gains and losses.
    """
    data['price change'] = data['Close'].pct_change()
    gain = data['price change'].apply(lambda x: x   if x > 0 else 0)
    loss = data['price change'].apply(lambda x: abs(x) if x < 0 else 0)

    avg_gain = gain.ewm(span=16).mean()
    avg_loss = loss.ewm(span=16).mean()

    RS  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + RS))

    data['RSI']        = rsi
    data['Overbought'] = 90   # upper threshold
    data['Oversold']   = 30   # lower threshold
    return data


RSI(df)

plt.figure(figsize=(12, 6))
plt.axhline(30, linestyle='--', color='blue',   label='Oversold (30)')
plt.axhline(90, linestyle='--', color='yellow', label='Overbought (90)')
plt.plot(df['RSI'], label='RSI', color='mediumspringgreen')
plt.title('RSI')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.xticks(rotation=45)
plt.legend(loc='upper left')
plt.show()


# ── 7. Buy / Sell Signal Function ─────────────────────────────────────────────
def buy_sell(signal):
    """
    2-of-3 indicator voting system.

    BUY  when 2+ indicators agree the stock is OVERSOLD  (position is flat).
    SELL when 2+ indicators agree the stock is OVERBOUGHT (position is held).

    Trades execute at the OPEN price of the next day (realistic simulation).
    Initial portfolio: $10,000 — fully invested per trade (all-in).

    Returns: (buy_prices, sell_prices, profits_per_trade, portfolio_values)
    """
    portfolio = 10000
    port_value = []
    buy        = []
    sell       = []
    pos        = []
    profits    = []
    position   = 0
    n          = 0       # number of shares held
    buy_at     = 0.0     # total cost of entry

    for i in range(len(signal) - 1):   # -1 guard: we access i+1 for next-day open

        close   = signal['Close'].iloc[i]
        ub      = signal['Ub'].iloc[i]
        lb      = signal['Lb'].iloc[i]
        obv_val = signal['OBV'].iloc[i]
        obv_ema = signal['OBV_EMA'].iloc[i]
        rsi_val = signal['RSI'].iloc[i]
        ob      = signal['Overbought'].iloc[i]
        os_     = signal['Oversold'].iloc[i]
        next_open = signal['Open'].iloc[i + 1]

        # ── SELL conditions (overbought signals) ──
        bb_overbought  = close   > ub
        obv_bearish    = obv_val < obv_ema
        rsi_overbought = rsi_val > ob
        sell_count     = sum([bb_overbought, obv_bearish, rsi_overbought])

        # ── BUY conditions (oversold signals) ──
        bb_oversold   = close   < lb
        obv_bullish   = obv_val > obv_ema
        rsi_oversold  = rsi_val < os_
        buy_count     = sum([bb_oversold, obv_bullish, rsi_oversold])

        if sell_count >= 2 and position == 1:
            # Sell: execute at next-day open
            sell.append(next_open)
            buy.append(np.nan)
            trade_profit = n * next_open - buy_at
            profits.append(trade_profit)
            portfolio += trade_profit
            port_value.append(portfolio)
            position = 0

        elif buy_count >= 2 and position == 0:
            # Buy: execute at next-day open, go all-in
            n      = portfolio / next_open
            buy_at = n * next_open
            buy.append(next_open)
            sell.append(np.nan)
            position = 1

        else:
            buy.append(np.nan)
            sell.append(np.nan)

        pos.append(position)

    # Handle the last row (no i+1 available — just hold position)
    buy.append(np.nan)
    sell.append(np.nan)
    pos.append(position)

    signal['Position'] = pos
    return (buy, sell, profits, port_value)


# ── FIX: Call buy_sell ONCE and cache the result ──────────────────────────────
aapl_results   = buy_sell(df)
df['buy']      = aapl_results[0]
df['sell']     = aapl_results[1]
our_profit     = aapl_results[2]
port_value     = aapl_results[3]
final_port_value = port_value[-1]


# ── 8. Buy/Sell Signal Chart ──────────────────────────────────────────────────
plt.figure(figsize=(12, 6))
plt.plot(df['Close'],  label='Close price',       color='aqua')
plt.plot(df['buy'],    label='Buy signal price',  color='green', marker='^', alpha=1)
plt.plot(df['sell'],   label='Sell signal price', color='red',   marker='v', alpha=1)
plt.xlabel('Date')
plt.ylabel('Closed price USD($)')
plt.legend(loc='upper left')
plt.xticks(rotation=45)
plt.title("Buy / Sell Signals on AAPL")
plt.show()


# ── 9. Trade Profits ──────────────────────────────────────────────────────────
df['Daily_Returns'] = df['Close'].pct_change(1)

print("The profits of our trades are:\n")
for i, p in enumerate(our_profit):
    print(f"  Trade {i + 1}: ${p:.2f}")

print(f"\nNet Returns (total profit): ${sum(our_profit):.2f} USD")
print(f"Final Portfolio Value:      ${final_port_value:.2f} USD")


# ── 10. Trade Log CSV ─────────────────────────────────────────────────────────
buypts    = []
sellpts   = []
positions = []
date_buy  = []
date_sell = []

for i in range(len(df['buy'])):
    if not pd.isna(df['buy'].iloc[i]):
        buypts.append(df['buy'].iloc[i])
        date_buy.append(df.index[i])
    if not pd.isna(df['sell'].iloc[i]):
        sellpts.append(df['sell'].iloc[i])
        date_sell.append(df.index[i])
        positions.append("Closed")

# Last trade still open
sellpts.append(np.nan)
date_sell.append(np.nan)
port_value_log = port_value + [final_port_value]
positions.append("Open")

new_df = pd.DataFrame({
    'Buy_Price':        buypts,
    'Buying Date':      date_buy,
    'Sell_Price':       sellpts,
    'Selling Date':     date_sell,
    'Portfolio Values': port_value_log,
    'Position':         positions
})

print("\nTrade Log:")
print(new_df)

file_name = "Buy_sell.csv"
new_df.to_csv(file_name, index=False)
print(f"\nTrade log saved to {file_name}")


# ── 11. Win / Loss Stats ──────────────────────────────────────────────────────
wins = sum(1 for p in our_profit if p > 0)
loss = sum(1 for p in our_profit if p <= 0)

win_rate  = wins / len(our_profit)
win_loss  = wins / loss if loss > 0 else float('inf')

print(f"\nWin rate:      {win_rate:.2%}")
print(f"Win/loss ratio: {win_loss:.1f}")

print("\nLoss-making trades:")
loss_vals = [p for p in our_profit if p < 0]
for p in loss_vals:
    print(f"  ${p:.2f}")
print(f"Largest loss:  ${min(loss_vals, default=0):.2f}")

print("\nProfit-making trades:")
win_vals = [p for p in our_profit if p > 0]
for p in win_vals:
    print(f"  ${p:.2f}")
print(f"Largest profit: ${max(win_vals, default=0):.2f}")

print(f"\nTotal executed trades: {len(our_profit)}")


# ── 12. Maximum Drawdown ──────────────────────────────────────────────────────
peak_value       = -float('inf')
maximum_drawdown = 0.0

for val in port_value:
    if val > peak_value:
        peak_value = val
    else:
        drawdown = val - peak_value
        if drawdown < maximum_drawdown:
            maximum_drawdown = drawdown

print(f"Maximum Drawdown: ${maximum_drawdown:.2f}")


# ── 13. Annualised Returns ────────────────────────────────────────────────────
ann_re = (((final_port_value / 10000) ** (1 / 7)) - 1) * 100
print(f"Annualised Returns: {ann_re:.2f}%")


# ── 14. Sharpe Ratio──────────────────────────────────────────────
# FIX: Standard Sharpe uses PERCENTAGE returns, not raw dollar profits.
# We compute per-trade % return = profit / capital_at_entry (which is always $10,000).
# Risk-free rate is annualised → convert to per-trade using average holding period.
# Average holding ~250 trading days ≈ 1 year → divide annual rate by 1.
# (With only 9 trades over 7 years, ~0.78 years average hold per trade.)

risk_free_rate_annual = 4.88   # US 10-year bond yield (%)

# Per-trade % returns (profit divided by $10,000 starting capital each trade)
per_trade_pct_returns = [(p / 10000) * 100 for p in our_profit]

# Average holding period in years (total years / number of trades)
avg_hold_years = 7 / len(our_profit)

# Scale risk-free rate to match the holding period of each trade
risk_free_per_trade = risk_free_rate_annual * avg_hold_years

sharpe_ratio = (
    (statistics.mean(per_trade_pct_returns) - risk_free_per_trade)
    / statistics.stdev(per_trade_pct_returns)
)

print(f"Sharpe Ratio (corrected, % returns): {sharpe_ratio:.4f}")


# ── 15. Portfolio & Returns Charts ───────────────────────────────────────────
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(port_value, color='blue', lw=3)
plt.title("Portfolio Value Over Trades")
plt.xlabel("Trade #")
plt.ylabel("Portfolio Value USD($)")

plt.subplot(1, 2, 2)
plt.plot(our_profit, color='blue', lw=3)
plt.title("Profit Per Trade")
plt.xlabel("Trade #")
plt.ylabel("Trade Profit USD($)")

plt.tight_layout()
plt.show()

# ── 16. Download SPY Data ─────────────────────────────────────────────────────
data2 = yf.download('SPY', interval='1d', start='2016-10-01', end='2023-10-04')
df2   = data2.copy()

# ── 17. Compute Indicators for SPY ───────────────────────────────────────────
df2['Midband'] = df2['Close'].rolling(window=30).mean()
df2['st_d']    = df2['Close'].rolling(window=30).std()
df2['Ub']      = df2['Midband'] + 1.5 * df2['st_d']
df2['Lb']      = df2['Midband'] - 1.5 * df2['st_d']

obv(df2)
RSI(df2)

# ── FIX: Call buy_sell ONCE for SPY and cache the result ─────────────────────
spy_results    = buy_sell(df2)
df2['buy']     = spy_results[0]
df2['sell']    = spy_results[1]
bench_profit   = spy_results[2]
bench_port_value = spy_results[3]

# ── 18. SPY Buy/Sell Chart ────────────────────────────────────────────────────
plt.figure(figsize=(12, 6))
plt.plot(df2['Close'], label='Close price',       color='aqua')
plt.plot(df2['buy'],   label='Buy signal price',  color='green', marker='^', alpha=1)
plt.plot(df2['sell'],  label='Sell signal price', color='red',   marker='v', alpha=1)
plt.xlabel('Date')
plt.ylabel('Closed price USD($)')
plt.legend(loc='upper left')
plt.xticks(rotation=45)
plt.title("Buy / Sell Signals on SPY (Benchmark)")
plt.show()

# ── 19. Benchmark Metrics ─────────────────────────────────────────────────────
bench_net_return = bench_port_value[-1] - 10000
print(f"Net Benchmark Returns (SPY): ${bench_net_return:.2f} USD")

# Sharpe for benchmark — same corrected method
bench_pct_returns  = [(p / 10000) * 100 for p in bench_profit]
avg_hold_bench     = 7 / len(bench_profit) if bench_profit else 1
rf_bench_per_trade = risk_free_rate_annual * avg_hold_bench

sharpe_ratio_bench = (
    (statistics.mean(bench_pct_returns) - rf_bench_per_trade)
    / statistics.stdev(bench_pct_returns)
)

print(f"Benchmark Sharpe Ratio (corrected): {sharpe_ratio_bench:.4f}")


# ── 20. Final Summary ─────────────────────────────────────────────────────────
print("\n" + "="*55)
print("          TRISIGNAL — STRATEGY SUMMARY")
print("="*55)
print(f"  Asset:                AAPL (2016–2023)")
print(f"  Initial Capital:      $10,000.00")
print(f"  Final Portfolio:      ${final_port_value:,.2f}")
print(f"  Net Return:           ${sum(our_profit):,.2f}")
print(f"  Annualised Return:    {ann_re:.2f}%")
print(f"  Sharpe Ratio:         {sharpe_ratio:.4f}")
print(f"  Max Drawdown:         ${maximum_drawdown:.2f}")
print(f"  Executed Trades:      {len(our_profit)}")
print(f"  Win Rate:             {win_rate:.2%}")
print(f"  Win/Loss Ratio:       {win_loss:.1f}")
print(f"  Benchmark (SPY):      ${bench_net_return:,.2f}")
print("="*55)