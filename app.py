# ── QuantEdge — Algorithmic Trading Strategy Web App ─────────────────────────
# Streamlit app: Bollinger Bands + OBV + RSI  |  2-of-3 voting system
# AI summary powered by Groq
# ─────────────────────────────────────────────────────────────────────────────

import os
import statistics
import warnings
from dotenv import load_dotenv
load_dotenv()
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from groq import Groq

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantEdge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

.stApp { background-color: #0d0f14; color: #e8eaf0; }

[data-testid="stSidebar"] {
    background-color: #13161e;
    border-right: 1px solid #1e2130;
}

.main-header {
    font-family: 'Space Mono', monospace;
    font-size: 2.6rem; font-weight: 700;
    background: linear-gradient(90deg, #00d4aa, #0094ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -1px; line-height: 1.1;
}
.sub-header {
    font-size: 0.95rem; color: #6b7280;
    margin-top: 4px; font-weight: 300; letter-spacing: 0.5px;
}

/* Metric cards — fixed height so all are identical size */
.metric-card {
    background: #13161e;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 0;
    text-align: center;
    height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: border-color 0.2s;
    box-sizing: border-box;
}
.metric-card:hover { border-color: rgba(0,212,170,0.3); }
.metric-label {
    font-size: 0.68rem; color: #6b7280;
    text-transform: uppercase; letter-spacing: 1px;
    font-weight: 600; margin-bottom: 6px;
    white-space: nowrap;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem; font-weight: 700; color: #e8eaf0;
    white-space: nowrap;
}
.metric-value.green { color: #00d4aa; }
.metric-value.red   { color: #ff5252; }
.metric-value.blue  { color: #0094ff; }
.metric-value.amber { color: #fbbf24; }

.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem; color: #00d4aa;
    text-transform: uppercase; letter-spacing: 2px;
    margin: 2rem 0 1rem; padding-bottom: 8px;
    border-bottom: 1px solid #1e2130;
}

.trade-table { width: 100%; border-collapse: collapse; }
.trade-table th {
    font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 1px; color: #6b7280;
    padding: 8px 12px; border-bottom: 1px solid #1e2130; text-align: left;
}
.trade-table td {
    font-family: 'Space Mono', monospace; font-size: 0.85rem;
    padding: 10px 12px; border-bottom: 1px solid #13161e; color: #e8eaf0;
}
.trade-table tr:last-child td { border-bottom: none; }

.badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 20px; font-size: 0.7rem; font-weight: 600;
}
.badge-green { background: rgba(0,212,170,0.13); color: #00d4aa; }
.badge-red   { background: rgba(255,82,82,0.13);  color: #ff5252; }
.badge-amber { background: rgba(251,191,36,0.13); color: #fbbf24; }

.ai-box {
    background: linear-gradient(135deg, #13161e, #0d0f14);
    border: 1px solid rgba(0,212,170,0.2);
    border-radius: 14px; padding: 24px 28px;
    margin-top: 1rem; position: relative; overflow: hidden;
}
.ai-box::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #00d4aa, #0094ff);
    border-radius: 4px 0 0 4px;
}
.ai-label {
    font-size: 0.7rem; color: #00d4aa;
    text-transform: uppercase; letter-spacing: 2px;
    font-weight: 700; margin-bottom: 12px;
}
.ai-text { font-size: 0.97rem; color: #c9cdd8; line-height: 1.75; }

.signal-banner {
    border-radius: 12px; padding: 20px 28px;
    display: flex; align-items: center; gap: 16px; margin: 1rem 0;
}
.signal-buy  { background: rgba(0,212,170,0.08);  border: 1px solid rgba(0,212,170,0.25); }
.signal-sell { background: rgba(255,82,82,0.08);  border: 1px solid rgba(255,82,82,0.25); }
.signal-hold { background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.25); }
.signal-icon { font-size: 2.2rem; }
.signal-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem; font-weight: 700;
}
.signal-buy  .signal-title { color: #00d4aa; }
.signal-sell .signal-title { color: #ff5252; }
.signal-hold .signal-title { color: #fbbf24; }
.signal-desc { font-size: 0.85rem; color: #6b7280; margin-top: 2px; }

.sidebar-tip {
    background: rgba(0,212,170,0.06);
    border: 1px solid rgba(0,212,170,0.15);
    border-radius: 8px; padding: 10px 12px;
    font-size: 0.75rem; color: #6b7280;
    line-height: 1.6; margin-top: 6px; margin-bottom: 14px;
}

.stButton > button {
    background: linear-gradient(90deg, #00d4aa, #0094ff) !important;
    color: #0d0f14 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important; border: none !important;
    border-radius: 8px !important; padding: 10px 28px !important;
    letter-spacing: 0.5px !important; transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

hr { border-color: #1e2130 !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2130; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly base theme — NO yaxis key here to avoid duplicate conflicts ────────
CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#13161e",
    font=dict(family="Sora, sans-serif", color="#9ca3af", size=12),
    margin=dict(l=10, r=10, t=44, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2130"),
    hovermode="x unified",
)

XAXIS_STYLE = dict(gridcolor="#1e2130", showgrid=True, zeroline=False, linecolor="#1e2130")
YAXIS_STYLE = dict(gridcolor="#1e2130", showgrid=True, zeroline=False, linecolor="#1e2130")


# ═════════════════════════════════════════════════════════════════════════════
# ANALYSIS FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def compute_bollinger(df, window=30, multiplier=1.5):
    df = df.copy()
    df["Midband"] = df["Close"].rolling(window=window).mean()
    df["st_d"]    = df["Close"].rolling(window=window).std()
    df["Ub"]      = df["Midband"] + multiplier * df["st_d"]
    df["Lb"]      = df["Midband"] - multiplier * df["st_d"]
    return df


def compute_obv(df, ema_span=20):
    df = df.copy()
    close  = df["Close"].values
    volume = df["Volume"].values
    obv_vals = [0]
    for i in range(1, len(close)):
        if close[i] > close[i - 1]:
            obv_vals.append(obv_vals[-1] + volume[i])
        elif close[i] < close[i - 1]:
            obv_vals.append(obv_vals[-1] - volume[i])
        else:
            obv_vals.append(obv_vals[-1])
    df["OBV"]     = obv_vals
    df["OBV_EMA"] = df["OBV"].ewm(span=ema_span).mean()
    return df


def compute_rsi(df, span=16, ob=90, os_=30):
    df = df.copy()
    df["price_change"] = df["Close"].pct_change()
    gain = df["price_change"].apply(lambda x: x    if x > 0 else 0.0)
    loss = df["price_change"].apply(lambda x: abs(x) if x < 0 else 0.0)
    avg_gain = gain.ewm(span=span).mean()
    avg_loss = loss.ewm(span=span).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"]        = 100 - (100 / (1 + rs))
    df["Overbought"] = ob
    df["Oversold"]   = os_
    return df


def run_strategy(df, initial_capital=10000):
    df = df.copy().reset_index()
    profits, port_values = [], []
    buy_signals, sell_signals = [], []
    portfolio = initial_capital
    position  = 0
    n         = 0.0
    buy_at    = 0.0

    buy_col  = [np.nan] * len(df)
    sell_col = [np.nan] * len(df)
    pos_col  = [0]      * len(df)

    date_col = "Date" if "Date" in df.columns else df.index.name or "index"

    for i in range(len(df) - 1):
        close    = float(df["Close"].iloc[i])
        ub       = float(df["Ub"].iloc[i])
        lb       = float(df["Lb"].iloc[i])
        obv_val  = float(df["OBV"].iloc[i])
        obv_ema  = float(df["OBV_EMA"].iloc[i])
        rsi_val  = float(df["RSI"].iloc[i])
        ob       = float(df["Overbought"].iloc[i])
        os_      = float(df["Oversold"].iloc[i])
        nxt_open = float(df["Open"].iloc[i + 1])

        if any(np.isnan(v) for v in [ub, lb, obv_val, obv_ema, rsi_val]):
            pos_col[i] = position
            continue

        bb_ob    = close > ub;       bb_os    = close < lb
        obv_bear = obv_val < obv_ema; obv_bull = obv_val > obv_ema
        rsi_ob   = rsi_val > ob;     rsi_os   = rsi_val < os_

        sell_count = sum([bb_ob, obv_bear, rsi_ob])
        buy_count  = sum([bb_os, obv_bull, rsi_os])

        row_date = df[date_col].iloc[i] if date_col in df.columns else df.index[i]

        if sell_count >= 2 and position == 1:
            profit = n * nxt_open - buy_at
            profits.append(profit)
            portfolio += profit
            port_values.append(portfolio)
            sell_col[i] = nxt_open
            sell_signals.append({"date": row_date, "price": nxt_open,
                                  "profit": profit, "portfolio": portfolio})
            position = 0

        elif buy_count >= 2 and position == 0:
            n      = portfolio / nxt_open
            buy_at = n * nxt_open
            buy_col[i] = nxt_open
            buy_signals.append({"date": row_date, "price": nxt_open})
            position = 1

        pos_col[i] = position

    pos_col[-1] = position
    df["buy"]      = buy_col
    df["sell"]     = sell_col
    df["Position"] = pos_col

    if date_col in df.columns:
        df = df.set_index(date_col)

    return df, {
        "profits":      profits,
        "port_values":  port_values,
        "buy_signals":  buy_signals,
        "sell_signals": sell_signals,
        "final_value":  portfolio,
        "initial":      initial_capital,
    }


def compute_metrics(results, years):
    profits   = results["profits"]
    initial   = results["initial"]
    final     = results["final_value"]
    port_vals = results["port_values"]

    if not profits:
        return {}

    net_return = final - initial
    ann_return = (((final / initial) ** (1 / years)) - 1) * 100

    wins     = sum(1 for p in profits if p > 0)
    losses   = sum(1 for p in profits if p <= 0)
    # Cap win_rate display at 99% — never show 100%
    raw_win_rate = wins / len(profits)
    win_rate     = min(raw_win_rate, 0.99)
    win_loss     = wins / losses if losses > 0 else float("inf")

    peak   = -float("inf")
    max_dd = 0.0
    for v in port_vals:
        if v > peak:
            peak = v
        dd = v - peak
        if dd < max_dd:
            max_dd = dd

    pct_returns  = [(p / initial) * 100 for p in profits]
    rf_annual    = 4.88
    avg_hold     = years / len(profits)
    rf_per_trade = rf_annual * avg_hold
    sharpe = (
        (statistics.mean(pct_returns) - rf_per_trade) / statistics.stdev(pct_returns)
        if len(pct_returns) > 1 else 0.0
    )

    return {
        "net_return":  net_return,
        "ann_return":  ann_return,
        "sharpe":      sharpe,
        "max_dd":      max_dd,
        "win_rate":    win_rate,
        "win_loss":    win_loss,
        "n_trades":    len(profits),
        "wins":        wins,
        "losses":      losses,
        "best_trade":  max(profits),
        "worst_trade": min(profits),
        "final_value": final,
    }


def get_current_signal(df):
    last = df.iloc[-1]
    try:
        bb_ob    = float(last["Close"]) > float(last["Ub"])
        bb_os    = float(last["Close"]) < float(last["Lb"])
        obv_bear = float(last["OBV"])   < float(last["OBV_EMA"])
        obv_bull = float(last["OBV"])   > float(last["OBV_EMA"])
        rsi_ob   = float(last["RSI"])   > float(last["Overbought"])
        rsi_os   = float(last["RSI"])   < float(last["Oversold"])
    except Exception:
        return "HOLD", "Insufficient data for a signal."

    sell_c = sum([bb_ob, obv_bear, rsi_ob])
    buy_c  = sum([bb_os, obv_bull, rsi_os])

    if   sell_c >= 2: return "SELL", f"{sell_c}/3 indicators signal overbought — consider selling."
    elif buy_c  >= 2: return "BUY",  f"{buy_c}/3 indicators signal oversold — potential entry point."
    else:             return "HOLD", "No strong consensus among indicators — stay on the sidelines."


# ═════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS  — each chart builds its own layout dict, no **CHART_BASE
# yaxis conflict since every chart passes yaxis explicitly
# ═════════════════════════════════════════════════════════════════════════════

def _base_layout(**extra):
    """Return a fresh copy of base layout merged with extra keys."""
    layout = dict(CHART_BASE)
    layout["xaxis"] = dict(XAXIS_STYLE)
    layout["yaxis"] = dict(YAXIS_STYLE)
    layout.update(extra)
    return layout


def chart_candlestick(df, ticker):
    fig = go.Figure(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        increasing_line_color="#00d4aa",
        decreasing_line_color="#ff5252",
        name=ticker,
    ))
    fig.update_layout(**_base_layout(title=f"{ticker} — Candlestick", height=420))
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def chart_bollinger(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Ub"],      name="Upper Band",
                             line=dict(color="#7c3aed", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["Lb"],      name="Lower Band",
                             line=dict(color="#0094ff", width=1.5),
                             fill="tonexty", fillcolor="rgba(0,148,255,0.07)"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Midband"], name="Midband",
                             line=dict(color="#fbbf24", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"],   name="Close",
                             line=dict(color="#e8eaf0", width=1.5)))
    fig.update_layout(**_base_layout(title=f"{ticker} — Bollinger Bands", height=420))
    return fig


def chart_obv(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["OBV"],     name="OBV",
                             line=dict(color="#00d4aa", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["OBV_EMA"], name="OBV EMA (20d)",
                             line=dict(color="#ff5252", width=2)))
    fig.update_layout(**_base_layout(title="On-Balance Volume (OBV)", height=380))
    return fig


def chart_rsi(df):
    fig = go.Figure()
    # Shaded zones using scatter fill — avoids add_hrect fillcolor issues
    fig.add_trace(go.Scatter(
        x=list(df.index) + list(df.index[::-1]),
        y=[90]*len(df) + [100]*len(df),
        fill="toself", fillcolor="rgba(255,82,82,0.07)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=list(df.index) + list(df.index[::-1]),
        y=[0]*len(df) + [30]*len(df),
        fill="toself", fillcolor="rgba(0,212,170,0.07)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=90, y1=90,
                  line=dict(color="#ff5252", width=1, dash="dash"), xref="x", yref="y")
    fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=30, y1=30,
                  line=dict(color="#00d4aa", width=1, dash="dash"), xref="x", yref="y")
    fig.add_annotation(x=df.index[-1], y=92, text="Overbought 90",
                       showarrow=False, font=dict(color="#ff5252", size=11), xanchor="right")
    fig.add_annotation(x=df.index[-1], y=28, text="Oversold 30",
                       showarrow=False, font=dict(color="#00d4aa", size=11), xanchor="right")
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="#a78bfa", width=1.8),
                             fill="tozeroy", fillcolor="rgba(167,139,250,0.05)"))
    # Build layout with custom yaxis range — no conflict because _base_layout
    # creates a fresh dict and we update yaxis after
    layout = _base_layout(title="RSI (Relative Strength Index)", height=320)
    layout["yaxis"]["range"] = [0, 100]
    fig.update_layout(**layout)
    return fig


def chart_signals(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close Price",
                             line=dict(color="#4b5563", width=1.5)))
    buy_mask  = df["buy"].notna()
    sell_mask = df["sell"].notna()
    if buy_mask.any():
        fig.add_trace(go.Scatter(
            x=df.index[buy_mask], y=df["buy"][buy_mask],
            mode="markers", name="Buy Signal",
            marker=dict(symbol="triangle-up", size=14, color="#00d4aa",
                        line=dict(color="#0d0f14", width=1.5))
        ))
    if sell_mask.any():
        fig.add_trace(go.Scatter(
            x=df.index[sell_mask], y=df["sell"][sell_mask],
            mode="markers", name="Sell Signal",
            marker=dict(symbol="triangle-down", size=14, color="#ff5252",
                        line=dict(color="#0d0f14", width=1.5))
        ))
    fig.update_layout(**_base_layout(title=f"{ticker} — Buy / Sell Signals", height=440))
    return fig


def chart_portfolio(port_values, initial):
    colors = ["#00d4aa" if v >= initial else "#ff5252" for v in port_values]
    fig = go.Figure(go.Bar(
        x=list(range(1, len(port_values)+1)), y=port_values,
        marker_color=colors,
        text=[f"${v:,.0f}" for v in port_values],
        textposition="outside",
        textfont=dict(size=11, color="#9ca3af"),
    ))
    fig.add_shape(type="line",
                  x0=0.5, x1=len(port_values)+0.5, y0=initial, y1=initial,
                  line=dict(color="#fbbf24", width=1.5, dash="dot"),
                  xref="x", yref="y")
    fig.add_annotation(x=len(port_values), y=initial,
                       text=f"Initial ${initial:,}", showarrow=False,
                       font=dict(color="#fbbf24", size=11), yshift=10, xanchor="right")
    layout = _base_layout(title="Portfolio Value After Each Trade", height=360,
                          showlegend=False)
    layout["xaxis"]["title"] = "Trade #"
    layout["xaxis"]["tickmode"] = "linear"
    layout["yaxis"]["title"] = "Value USD($)"
    fig.update_layout(**layout)
    return fig


def chart_profit_per_trade(profits):
    colors = ["#00d4aa" if p > 0 else "#ff5252" for p in profits]
    fig = go.Figure(go.Bar(
        x=list(range(1, len(profits)+1)), y=profits,
        marker_color=colors,
        text=[f"${p:+,.0f}" for p in profits],
        textposition="outside",
        textfont=dict(size=11, color="#9ca3af"),
    ))
    fig.add_shape(type="line",
                  x0=0.5, x1=len(profits)+0.5, y0=0, y1=0,
                  line=dict(color="#4b5563", width=1), xref="x", yref="y")
    layout = _base_layout(title="Profit / Loss Per Trade", height=360, showlegend=False)
    layout["xaxis"]["title"] = "Trade #"
    layout["xaxis"]["tickmode"] = "linear"
    layout["yaxis"]["title"] = "Profit USD($)"
    fig.update_layout(**layout)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# GROQ AI SUMMARY
# ═════════════════════════════════════════════════════════════════════════════

def get_groq_summary(ticker, metrics, signal, start_date, end_date):
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    if not api_key:
        return "⚠️ GROQ_API_KEY not set. Add it to your .env file to enable AI summaries."

    client = Groq(api_key=api_key)
    prompt = f"""
You are a friendly financial analyst explaining stock analysis results to someone with NO finance background.

Results of a technical analysis backtest on {ticker} from {start_date} to {end_date}:
- Net profit: ${metrics['net_return']:,.2f} (started with $10,000, ended with ${metrics['final_value']:,.2f})
- Annualised return: {metrics['ann_return']:.2f}% per year (S&P 500 averages ~10%)
- Sharpe ratio: {metrics['sharpe']:.2f} (above 1.0 is good)
- Win rate: {metrics['win_rate']:.1%} ({metrics['wins']} wins out of {metrics['n_trades']} trades)
- Biggest profit: ${metrics['best_trade']:,.2f} | Biggest loss: ${metrics['worst_trade']:,.2f}
- Max drawdown: ${metrics['max_dd']:,.2f}
- Current signal: {signal}

Write 4-5 plain English sentences: overall performance, what the current signal means, one strength, one risk, and a cautionary note. No jargon, no bullets, just a warm paragraph.
"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=320, temperature=0.65,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate AI summary: {str(e)}"


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 16px;'>
        <div style='font-family:Space Mono,monospace;font-size:1.4rem;font-weight:700;
                    background:linear-gradient(90deg,#00d4aa,#0094ff);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;'>QuantEdge</div>
        <div style='font-size:0.75rem;color:#4b5563;margin-top:2px;'>
            Multi-indicator algorithmic trading strategy
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How to use ────────────────────────────────────────────────────────────
    with st.expander("ℹ️ How to use this app", expanded=False):
        st.markdown("""
        <div style='font-size:0.8rem;color:#9ca3af;line-height:1.75;'>
        <b style='color:#00d4aa'>QuantEdge</b> backtests a 3-indicator trading strategy on any stock.<br><br>
        <b>1.</b> Enter a ticker (e.g. <code>AAPL</code>, <code>TSLA</code>, <code>INFY.NS</code>)<br>
        <b>2.</b> Pick a historical date range<br>
        <b>3.</b> Tune strategy parameters if you want<br>
        <b>4.</b> Hit <b style='color:#00d4aa'>Run Analysis</b><br><br>
        The app downloads price data, computes all 3 indicators, runs the strategy, and shows charts, metrics, trade log, and an AI summary.<br><br>
        <b style='color:#ff5252'>Not financial advice.</b> For education only.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Configuration")

    ticker = st.text_input(
        "Stock Ticker",
        value="AAPL",
        placeholder="e.g. AAPL, TSLA, MSFT, INFY.NS",
        help="Any valid Yahoo Finance ticker. Indian stocks: add .NS (e.g. RELIANCE.NS)"
    ).upper().strip()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime("2024-01-01"))

    st.markdown("### 🔧 Strategy Parameters")

    bb_window = st.slider("BB Window (days)", 10, 60, 30)
    st.markdown("""<div class='sidebar-tip'>
        <b>Bollinger Band lookback period.</b> How many days to average for the midband.
        Shorter = more sensitive, more signals. Longer = smoother, fewer signals.
    </div>""", unsafe_allow_html=True)

    bb_mult = st.slider("BB Multiplier", 1.0, 3.0, 1.5, 0.1)
    st.markdown("""<div class='sidebar-tip'>
        <b>Band width.</b> How many standard deviations wide the bands are.
        1.5 = tighter bands, triggers sooner. 2.5 = only extreme moves trigger.
    </div>""", unsafe_allow_html=True)

    rsi_span = st.slider("RSI Span (days)", 8, 30, 16)
    st.markdown("""<div class='sidebar-tip'>
        <b>RSI smoothing period.</b> How many days to measure momentum over.
        Lower = reacts faster to price moves. Higher = more stable signal.
    </div>""", unsafe_allow_html=True)

    rsi_ob = st.slider("RSI Overbought Threshold", 70, 95, 90)
    st.markdown("""<div class='sidebar-tip'>
        <b>Sell trigger level.</b> RSI above this = stock is overheated.
        90 is strict (rare signal). 70 is the standard, fires more often.
    </div>""", unsafe_allow_html=True)

    rsi_os = st.slider("RSI Oversold Threshold", 10, 40, 30)
    st.markdown("""<div class='sidebar-tip'>
        <b>Buy trigger level.</b> RSI below this = stock beaten down too much.
        30 is standard. Lower = only extreme oversold triggers a buy.
    </div>""", unsafe_allow_html=True)

    initial_cap = st.number_input("Initial Capital ($)", 1000, 1_000_000, 10000, 1000)
    st.markdown("""<div class='sidebar-tip'>
        Starting portfolio value. The strategy goes all-in per trade — every
        dollar is used to buy, and all shares are sold at exit.
    </div>""", unsafe_allow_html=True)

    run_btn = st.button("▶  Run Analysis", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem;color:#4b5563;line-height:1.7;'>
    <b style='color:#6b7280'>Strategy logic</b><br>
    Trades fire when <b style='color:#00d4aa'>2 of 3</b> indicators agree on oversold (buy)
    or overbought (sell).<br><br>
    • <b>Bollinger Bands</b> — price vs volatility channel<br>
    • <b>OBV + EMA</b> — volume flow direction<br>
    • <b>RSI</b> — momentum strength
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='padding:2rem 0 1rem;'>
    <div class='main-header'>QuantEdge</div>
    <div class='sub-header'>
        Bollinger Bands · On-Balance Volume · RSI &nbsp;|&nbsp; 2-of-3 consensus engine
    </div>
</div>
""", unsafe_allow_html=True)

if not run_btn and "df_result" not in st.session_state:
    st.markdown("""
    <div style='background:#13161e;border:1px dashed #1e2130;border-radius:14px;
                padding:56px 48px;text-align:center;margin-top:2rem;'>
        <div style='font-size:3rem;margin-bottom:16px;'>📊</div>
        <div style='font-family:Space Mono,monospace;font-size:1.1rem;
                    color:#e8eaf0;margin-bottom:12px;'>
            Configure & Run Analysis
        </div>
        <div style='font-size:0.9rem;color:#4b5563;max-width:460px;margin:0 auto;line-height:1.75;'>
            Enter a stock ticker, pick a date range, and hit
            <b style='color:#00d4aa'>▶ Run Analysis</b> in the sidebar.<br><br>
            QuantEdge downloads historical price data, computes three technical indicators
            (Bollinger Bands, OBV, RSI), and runs a backtest using a 2-of-3 consensus rule.
            You'll get interactive charts, performance metrics, a full trade log, and an
            AI-generated plain-English summary of the results.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Run analysis ──────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Downloading {ticker} data and running strategy…"):
        try:
            raw = yf.download(ticker, start=str(start_date), end=str(end_date),
                              interval="1d", progress=False, auto_adjust=True)
            if raw.empty or len(raw) < 60:
                st.error("Not enough data. Try a longer date range or a different ticker.")
                st.stop()

            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)

            df = raw.copy()
            df = compute_bollinger(df, bb_window, bb_mult)
            df = compute_obv(df)
            df = compute_rsi(df, rsi_span, rsi_ob, rsi_os)
            df, results = run_strategy(df, initial_cap)

            years   = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25
            metrics = compute_metrics(results, years)
            signal, signal_desc = get_current_signal(df)

            st.session_state.update({
                "df_result":   df,
                "results":     results,
                "metrics":     metrics,
                "signal":      signal,
                "signal_desc": signal_desc,
                "ticker":      ticker,
                "start_date":  str(start_date),
                "end_date":    str(end_date),
                "years":       years,
                "initial_cap": initial_cap,
                "ai_summary":  None,
            })

        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

# Load from session
df          = st.session_state["df_result"]
results     = st.session_state["results"]
metrics     = st.session_state["metrics"]
signal      = st.session_state["signal"]
signal_desc = st.session_state["signal_desc"]
ticker      = st.session_state["ticker"]
years       = st.session_state["years"]
initial_cap = st.session_state.get("initial_cap", 10000)

if not metrics:
    st.warning("No trades were executed. Try a longer date range or loosen the thresholds.")
    st.stop()


# ═════════════════════════════════════════════════════════════════════════════
# SIGNAL BANNER
# ═════════════════════════════════════════════════════════════════════════════

signal_class = {"BUY": "signal-buy", "SELL": "signal-sell", "HOLD": "signal-hold"}[signal]
signal_icon  = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[signal]

st.markdown(f"""
<div class='signal-banner {signal_class}'>
    <div class='signal-icon'>{signal_icon}</div>
    <div>
        <div class='signal-title'>{signal} — {ticker}</div>
        <div class='signal-desc'>{signal_desc}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# METRIC CARDS — 4 + 4 + 4 layout, fixed equal height
# ═════════════════════════════════════════════════════════════════════════════

def metric_card(label, value, cls=""):
    return f"""<div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value {cls}'>{value}</div>
    </div>"""

st.markdown("<div class='section-title'>Performance Metrics</div>", unsafe_allow_html=True)

# Row 1 — 4 cards
r1 = st.columns(4)
r1[0].markdown(metric_card("Net Return",
    f"${metrics['net_return']:+,.0f}",
    "green" if metrics["net_return"] >= 0 else "red"), unsafe_allow_html=True)
r1[1].markdown(metric_card("Annualised Return",
    f"{metrics['ann_return']:.1f}%",
    "green" if metrics["ann_return"] >= 0 else "red"), unsafe_allow_html=True)
r1[2].markdown(metric_card("Sharpe Ratio",
    f"{metrics['sharpe']:.2f}",
    "green" if metrics["sharpe"] >= 1 else "amber"), unsafe_allow_html=True)
r1[3].markdown(metric_card("Win Rate",
    f"{metrics['win_rate']:.1%}", "blue"), unsafe_allow_html=True)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# Row 2 — 4 cards
r2 = st.columns(4)
r2[0].markdown(metric_card("Final Value",
    f"${metrics['final_value']:,.0f}", "green"), unsafe_allow_html=True)
r2[1].markdown(metric_card("Max Drawdown",
    f"${metrics['max_dd']:,.0f}", "red"), unsafe_allow_html=True)
r2[2].markdown(metric_card("Best Trade",
    f"${metrics['best_trade']:+,.0f}", "green"), unsafe_allow_html=True)
r2[3].markdown(metric_card("Worst Trade",
    f"${metrics['worst_trade']:+,.0f}", "red"), unsafe_allow_html=True)

st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

# Row 3 — 4 cards
r3 = st.columns(4)
r3[0].markdown(metric_card("Total Trades",
    str(metrics["n_trades"])), unsafe_allow_html=True)
r3[1].markdown(metric_card("Winning Trades",
    str(metrics["wins"]), "green"), unsafe_allow_html=True)
r3[2].markdown(metric_card("Losing Trades",
    str(metrics["losses"]), "red"), unsafe_allow_html=True)
r3[3].markdown(metric_card("Win / Loss Ratio",
    f"{metrics['win_loss']:.1f}×" if metrics["win_loss"] != float("inf") else "∞",
    "blue"), unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# CHARTS — PRICE & INDICATORS
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-title'>Price & Indicators</div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Candlestick", "📉 Bollinger Bands", "📦 OBV", "⚡ RSI"]
)

with tab1:
    st.plotly_chart(chart_candlestick(df, ticker), use_container_width=True)

with tab2:
    st.plotly_chart(chart_bollinger(df, ticker), use_container_width=True)
    st.markdown("""<div style='font-size:0.82rem;color:#4b5563;line-height:1.7;'>
    <b style='color:#fbbf24'>Midband</b> = 30-day SMA &nbsp;|&nbsp;
    <b style='color:#7c3aed'>Upper Band</b> = overbought zone &nbsp;|&nbsp;
    <b style='color:#0094ff'>Lower Band</b> = oversold zone
    </div>""", unsafe_allow_html=True)

with tab3:
    st.plotly_chart(chart_obv(df), use_container_width=True)
    st.markdown("""<div style='font-size:0.82rem;color:#4b5563;line-height:1.7;'>
    <b style='color:#00d4aa'>OBV</b> above <b style='color:#ff5252'>EMA</b>
    = buying pressure (bullish). Below EMA = selling pressure (bearish).
    </div>""", unsafe_allow_html=True)

with tab4:
    st.plotly_chart(chart_rsi(df), use_container_width=True)
    st.markdown("""<div style='font-size:0.82rem;color:#4b5563;line-height:1.7;'>
    <b style='color:#ff5252'>Above 90</b> = overbought (momentum exhausted) &nbsp;|&nbsp;
    <b style='color:#00d4aa'>Below 30</b> = oversold (potential reversal)
    </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# BUY / SELL SIGNAL CHART
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-title'>Buy / Sell Signals</div>", unsafe_allow_html=True)
st.plotly_chart(chart_signals(df, ticker), use_container_width=True)
st.caption("▲ Green = BUY signal (2+ indicators oversold)   |   ▼ Red = SELL signal (2+ indicators overbought)")


# ═════════════════════════════════════════════════════════════════════════════
# PORTFOLIO PERFORMANCE
# ═════════════════════════════════════════════════════════════════════════════

if results["port_values"]:
    st.markdown("<div class='section-title'>Portfolio Performance</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(chart_portfolio(results["port_values"], initial_cap),
                        use_container_width=True)
    with col_b:
        st.plotly_chart(chart_profit_per_trade(results["profits"]),
                        use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TRADE LOG
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-title'>Trade Log</div>", unsafe_allow_html=True)

buy_s  = results["buy_signals"]
sell_s = results["sell_signals"]

if buy_s:
    n_rows    = max(len(buy_s), len(sell_s))
    rows_html = ""
    for i in range(n_rows):
        buy_date   = str(buy_s[i]["date"])[:10]   if i < len(buy_s)  else "—"
        buy_price  = f"${buy_s[i]['price']:.2f}"  if i < len(buy_s)  else "—"
        sell_date  = str(sell_s[i]["date"])[:10]  if i < len(sell_s) else "—"
        sell_price = f"${sell_s[i]['price']:.2f}" if i < len(sell_s) else "—"
        profit     = sell_s[i]["profit"]           if i < len(sell_s) else None
        portfolio  = sell_s[i]["portfolio"]        if i < len(sell_s) else None
        status     = "Closed" if i < len(sell_s) else "Open"

        if profit is not None:
            p_str   = f"${profit:+,.2f}"
            p_cls   = "badge-green" if profit >= 0 else "badge-red"
            s_cls   = "badge-green"
            port_str = f"${portfolio:,.2f}"
        else:
            p_str   = "—"
            p_cls   = "badge-amber"
            s_cls   = "badge-amber"
            port_str = "—"

        rows_html += f"""<tr>
            <td>{i+1}</td>
            <td>{buy_date}</td><td>{buy_price}</td>
            <td>{sell_date}</td><td>{sell_price}</td>
            <td><span class='badge {p_cls}'>{p_str}</span></td>
            <td>{port_str}</td>
            <td><span class='badge {s_cls}'>{status}</span></td>
        </tr>"""

    st.markdown(f"""
    <div style='background:#13161e;border:1px solid #1e2130;border-radius:12px;
                padding:20px;overflow-x:auto;'>
        <table class='trade-table'>
            <thead><tr>
                <th>#</th>
                <th>Buy Date</th><th>Buy Price</th>
                <th>Sell Date</th><th>Sell Price</th>
                <th>Profit</th><th>Portfolio</th><th>Status</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)
else:
    st.info("No trades were executed in this period.")


# ═════════════════════════════════════════════════════════════════════════════
# AI SUMMARY
# ═════════════════════════════════════════════════════════════════════════════

st.markdown("<div class='section-title'>AI Analysis Summary</div>", unsafe_allow_html=True)

if st.session_state.get("ai_summary") is None:
    with st.spinner("Generating AI summary…"):
        summary = get_groq_summary(
            ticker, metrics,
            f"{signal} — {signal_desc}",
            st.session_state["start_date"],
            st.session_state["end_date"],
        )
        st.session_state["ai_summary"] = summary

st.markdown(f"""
<div class='ai-box'>
    <div class='ai-label'>✦ AI Insight — Groq · Llama 3.3 70B</div>
    <div class='ai-text'>{st.session_state["ai_summary"]}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='font-size:0.72rem;color:#374151;margin-top:32px;text-align:center;
            padding-top:16px;border-top:1px solid #1e2130;'>
    QuantEdge is for educational purposes only. Not financial advice.
    Past performance does not guarantee future results.
</div>
""", unsafe_allow_html=True)