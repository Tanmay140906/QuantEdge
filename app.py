# ── QuantEdge — Algorithmic Trading Strategy Web App ─────────────────────────
# Bollinger Bands + OBV + RSI  |  2-of-3 voting  |  Auth + SQLite history
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, json, statistics, warnings
from dotenv import load_dotenv
load_dotenv()
warnings.filterwarnings("ignore")

# Make sure sibling modules are importable
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from groq import Groq

from database import (init_db, save_analysis, duplicate_analysis,
                      get_user_analyses, get_analysis_by_id)
from auth import render_auth_page

init_db()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantEdge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    if not render_auth_page():
        st.stop()

user = st.session_state["user"]

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Sora',sans-serif;}
.stApp{background-color:#0d0f14;color:#e8eaf0;}
[data-testid="stSidebar"]{background-color:#13161e;border-right:1px solid #1e2130;}
.main-header{font-family:'Space Mono',monospace;font-size:2.4rem;font-weight:700;
  background:linear-gradient(90deg,#00d4aa,#0094ff);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-1px;line-height:1.1;}
.sub-header{font-size:.9rem;color:#6b7280;margin-top:4px;font-weight:300;}
.metric-card{background:#13161e;border:1px solid #1e2130;border-radius:12px;padding:0;
  text-align:center;height:100px;display:flex;flex-direction:column;justify-content:center;
  align-items:center;transition:border-color .2s;box-sizing:border-box;}
.metric-card:hover{border-color:rgba(0,212,170,.3);}
.metric-label{font-size:.68rem;color:#6b7280;text-transform:uppercase;letter-spacing:1px;
  font-weight:600;margin-bottom:6px;white-space:nowrap;}
.metric-value{font-family:'Space Mono',monospace;font-size:1.25rem;font-weight:700;
  color:#e8eaf0;white-space:nowrap;}
.metric-value.green{color:#00d4aa;} .metric-value.red{color:#ff5252;}
.metric-value.blue{color:#0094ff;}  .metric-value.amber{color:#fbbf24;}
.section-title{font-family:'Space Mono',monospace;font-size:.8rem;color:#00d4aa;
  text-transform:uppercase;letter-spacing:2px;margin:2rem 0 1rem;padding-bottom:8px;
  border-bottom:1px solid #1e2130;}
.trade-table{width:100%;border-collapse:collapse;}
.trade-table th{font-size:.72rem;text-transform:uppercase;letter-spacing:1px;color:#6b7280;
  padding:8px 12px;border-bottom:1px solid #1e2130;text-align:left;}
.trade-table td{font-family:'Space Mono',monospace;font-size:.85rem;padding:10px 12px;
  border-bottom:1px solid #13161e;color:#e8eaf0;}
.trade-table tr:last-child td{border-bottom:none;}
.badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.7rem;font-weight:600;}
.badge-green{background:rgba(0,212,170,.13);color:#00d4aa;}
.badge-red{background:rgba(255,82,82,.13);color:#ff5252;}
.badge-amber{background:rgba(251,191,36,.13);color:#fbbf24;}
.ai-box{background:linear-gradient(135deg,#13161e,#0d0f14);border:1px solid rgba(0,212,170,.2);
  border-radius:14px;padding:24px 28px;margin-top:1rem;position:relative;overflow:hidden;}
.ai-box::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;
  background:linear-gradient(180deg,#00d4aa,#0094ff);border-radius:4px 0 0 4px;}
.ai-label{font-size:.7rem;color:#00d4aa;text-transform:uppercase;letter-spacing:2px;
  font-weight:700;margin-bottom:12px;}
.ai-text{font-size:.97rem;color:#c9cdd8;line-height:1.75;}
.signal-banner{border-radius:12px;padding:20px 28px;display:flex;align-items:center;
  gap:16px;margin:1rem 0;}
.signal-buy{background:rgba(0,212,170,.08);border:1px solid rgba(0,212,170,.25);}
.signal-sell{background:rgba(255,82,82,.08);border:1px solid rgba(255,82,82,.25);}
.signal-hold{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.25);}
.signal-icon{font-size:2.2rem;}
.signal-title{font-family:'Space Mono',monospace;font-size:1.4rem;font-weight:700;}
.signal-buy .signal-title{color:#00d4aa;} .signal-sell .signal-title{color:#ff5252;}
.signal-hold .signal-title{color:#fbbf24;}
.signal-desc{font-size:.85rem;color:#6b7280;margin-top:2px;}
.sidebar-tip{background:rgba(0,212,170,.06);border:1px solid rgba(0,212,170,.15);
  border-radius:8px;padding:10px 12px;font-size:.75rem;color:#6b7280;
  line-height:1.6;margin-top:6px;margin-bottom:14px;}
.dup-banner{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.3);
  border-radius:12px;padding:18px 24px;margin:1rem 0;}
.stButton>button{background:linear-gradient(90deg,#00d4aa,#0094ff)!important;
  color:#0d0f14!important;font-family:'Space Mono',monospace!important;font-weight:700!important;
  border:none!important;border-radius:8px!important;padding:10px 28px!important;
  letter-spacing:.5px!important;transition:opacity .2s!important;}
.stButton>button:hover{opacity:.85!important;}
hr{border-color:#1e2130!important;}
::-webkit-scrollbar{width:6px;}::-webkit-scrollbar-track{background:#0d0f14;}
::-webkit-scrollbar-thumb{background:#1e2130;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── Plotly base ───────────────────────────────────────────────────────────────
CHART_BASE   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#13161e",
                    font=dict(family="Sora,sans-serif", color="#9ca3af", size=12),
                    margin=dict(l=10,r=10,t=44,b=10),
                    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2130"),
                    hovermode="x unified")
XAXIS_STYLE  = dict(gridcolor="#1e2130", showgrid=True, zeroline=False, linecolor="#1e2130")
YAXIS_STYLE  = dict(gridcolor="#1e2130", showgrid=True, zeroline=False, linecolor="#1e2130")

def _layout(**extra):
    l = dict(CHART_BASE)
    l["xaxis"] = dict(XAXIS_STYLE)
    l["yaxis"] = dict(YAXIS_STYLE)
    l.update(extra)
    return l


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
    c, v = df["Close"].values, df["Volume"].values
    o = [0]
    for i in range(1, len(c)):
        if c[i] > c[i-1]:   o.append(o[-1] + v[i])
        elif c[i] < c[i-1]: o.append(o[-1] - v[i])
        else:                o.append(o[-1])
    df["OBV"]     = o
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
    profits, port_values, buy_signals, sell_signals = [], [], [], []
    portfolio, position, n, buy_at = initial_capital, 0, 0.0, 0.0
    buy_col  = [np.nan]*len(df)
    sell_col = [np.nan]*len(df)
    pos_col  = [0]*len(df)
    date_col = "Date" if "Date" in df.columns else (df.index.name or "index")

    for i in range(len(df)-1):
        close    = float(df["Close"].iloc[i])
        ub, lb   = float(df["Ub"].iloc[i]), float(df["Lb"].iloc[i])
        obv_val  = float(df["OBV"].iloc[i])
        obv_ema  = float(df["OBV_EMA"].iloc[i])
        rsi_val  = float(df["RSI"].iloc[i])
        ob, os_  = float(df["Overbought"].iloc[i]), float(df["Oversold"].iloc[i])
        nxt_open = float(df["Open"].iloc[i+1])

        if any(np.isnan(v) for v in [ub, lb, obv_val, obv_ema, rsi_val]):
            pos_col[i] = position; continue

        sell_count = sum([close>ub, obv_val<obv_ema, rsi_val>ob])
        buy_count  = sum([close<lb, obv_val>obv_ema, rsi_val<os_])
        row_date   = df[date_col].iloc[i] if date_col in df.columns else df.index[i]

        if sell_count >= 2 and position == 1:
            profit = n*nxt_open - buy_at
            profits.append(profit); portfolio += profit; port_values.append(portfolio)
            sell_col[i] = nxt_open
            sell_signals.append({"date": str(row_date)[:10], "price": nxt_open,
                                  "profit": profit, "portfolio": portfolio})
            position = 0
        elif buy_count >= 2 and position == 0:
            n = portfolio/nxt_open; buy_at = n*nxt_open
            buy_col[i] = nxt_open
            buy_signals.append({"date": str(row_date)[:10], "price": nxt_open})
            position = 1
        pos_col[i] = position

    pos_col[-1] = position
    df["buy"] = buy_col; df["sell"] = sell_col; df["Position"] = pos_col
    if date_col in df.columns:
        df = df.set_index(date_col)
    return df, {"profits": profits, "port_values": port_values,
                "buy_signals": buy_signals, "sell_signals": sell_signals,
                "final_value": portfolio, "initial": initial_capital}

def compute_metrics(results, years):
    profits   = results["profits"]
    if not profits: return {}
    initial, final, pv = results["initial"], results["final_value"], results["port_values"]
    wins   = sum(1 for p in profits if p > 0)
    losses = sum(1 for p in profits if p <= 0)
    peak = -float("inf"); max_dd = 0.0
    for v in pv:
        if v > peak: peak = v
        if (v-peak) < max_dd: max_dd = v-peak
    pcts = [(p/initial)*100 for p in profits]
    avg_hold = years/len(profits)
    sharpe = (statistics.mean(pcts) - 4.88*avg_hold)/statistics.stdev(pcts) if len(pcts)>1 else 0.0
    return {
        "net_return":  final-initial,
        "ann_return":  (((final/initial)**(1/years))-1)*100,
        "sharpe":      sharpe,
        "max_dd":      max_dd,
        "win_rate":    min(wins/len(profits), 0.99),
        "win_loss":    wins/losses if losses else float("inf"),
        "n_trades":    len(profits),
        "wins":        wins, "losses": losses,
        "best_trade":  max(profits), "worst_trade": min(profits),
        "final_value": final,
    }

def get_current_signal(df):
    last = df.iloc[-1]
    try:
        sc = sum([float(last["Close"])>float(last["Ub"]),
                  float(last["OBV"])<float(last["OBV_EMA"]),
                  float(last["RSI"])>float(last["Overbought"])])
        bc = sum([float(last["Close"])<float(last["Lb"]),
                  float(last["OBV"])>float(last["OBV_EMA"]),
                  float(last["RSI"])<float(last["Oversold"])])
    except: return "HOLD","Insufficient data."
    if sc>=2: return "SELL",f"{sc}/3 indicators signal overbought — consider selling."
    if bc>=2: return "BUY", f"{bc}/3 indicators signal oversold — potential entry point."
    return "HOLD","No strong consensus — stay on the sidelines."


# ═════════════════════════════════════════════════════════════════════════════
# CHART FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def chart_candlestick(df, ticker):
    fig = go.Figure(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], increasing_line_color="#00d4aa",
        decreasing_line_color="#ff5252", name=ticker))
    fig.update_layout(**_layout(title=f"{ticker} — Candlestick", height=420))
    fig.update_xaxes(rangeslider_visible=False)
    return fig

def chart_bollinger(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Ub"],      name="Upper Band", line=dict(color="#7c3aed",width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["Lb"],      name="Lower Band", line=dict(color="#0094ff",width=1.5), fill="tonexty", fillcolor="rgba(0,148,255,0.07)"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Midband"], name="Midband",    line=dict(color="#fbbf24",width=2,dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"],   name="Close",      line=dict(color="#e8eaf0",width=1.5)))
    fig.update_layout(**_layout(title=f"{ticker} — Bollinger Bands", height=420))
    return fig

def chart_obv(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["OBV"],     name="OBV",         line=dict(color="#00d4aa",width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=df["OBV_EMA"], name="OBV EMA(20d)",line=dict(color="#ff5252",width=2)))
    fig.update_layout(**_layout(title="On-Balance Volume (OBV)", height=380))
    return fig

def chart_rsi(df):
    fig = go.Figure()
    idx = list(df.index)
    fig.add_trace(go.Scatter(x=idx+idx[::-1], y=[90]*len(idx)+[100]*len(idx),
        fill="toself", fillcolor="rgba(255,82,82,0.07)", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=idx+idx[::-1], y=[0]*len(idx)+[30]*len(idx),
        fill="toself", fillcolor="rgba(0,212,170,0.07)", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_shape(type="line",x0=idx[0],x1=idx[-1],y0=90,y1=90,
        line=dict(color="#ff5252",width=1,dash="dash"),xref="x",yref="y")
    fig.add_shape(type="line",x0=idx[0],x1=idx[-1],y0=30,y1=30,
        line=dict(color="#00d4aa",width=1,dash="dash"),xref="x",yref="y")
    fig.add_annotation(x=idx[-1],y=92,text="Overbought 90",showarrow=False,
        font=dict(color="#ff5252",size=11),xanchor="right")
    fig.add_annotation(x=idx[-1],y=28,text="Oversold 30",showarrow=False,
        font=dict(color="#00d4aa",size=11),xanchor="right")
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
        line=dict(color="#a78bfa",width=1.8), fill="tozeroy", fillcolor="rgba(167,139,250,0.05)"))
    lo = _layout(title="RSI (Relative Strength Index)", height=320)
    lo["yaxis"]["range"] = [0,100]
    fig.update_layout(**lo)
    return fig

def chart_signals(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close Price", line=dict(color="#4b5563",width=1.5)))
    bm, sm = df["buy"].notna(), df["sell"].notna()
    if bm.any():
        fig.add_trace(go.Scatter(x=df.index[bm], y=df["buy"][bm], mode="markers", name="Buy Signal",
            marker=dict(symbol="triangle-up",size=14,color="#00d4aa",line=dict(color="#0d0f14",width=1.5))))
    if sm.any():
        fig.add_trace(go.Scatter(x=df.index[sm], y=df["sell"][sm], mode="markers", name="Sell Signal",
            marker=dict(symbol="triangle-down",size=14,color="#ff5252",line=dict(color="#0d0f14",width=1.5))))
    fig.update_layout(**_layout(title=f"{ticker} — Buy / Sell Signals", height=440))
    return fig

def chart_portfolio(pv, initial):
    colors = ["#00d4aa" if v>=initial else "#ff5252" for v in pv]
    fig = go.Figure(go.Bar(x=list(range(1,len(pv)+1)), y=pv, marker_color=colors,
        text=[f"${v:,.0f}" for v in pv], textposition="outside",
        textfont=dict(size=11,color="#9ca3af")))
    fig.add_shape(type="line",x0=.5,x1=len(pv)+.5,y0=initial,y1=initial,
        line=dict(color="#fbbf24",width=1.5,dash="dot"),xref="x",yref="y")
    fig.add_annotation(x=len(pv),y=initial,text=f"Initial ${initial:,}",showarrow=False,
        font=dict(color="#fbbf24",size=11),yshift=10,xanchor="right")
    lo = _layout(title="Portfolio Value After Each Trade", height=360, showlegend=False)
    lo["xaxis"]["title"] = "Trade #"; lo["xaxis"]["tickmode"] = "linear"
    lo["yaxis"]["title"] = "Value USD($)"
    fig.update_layout(**lo)
    return fig

def chart_profit_per_trade(profits):
    colors = ["#00d4aa" if p>0 else "#ff5252" for p in profits]
    fig = go.Figure(go.Bar(x=list(range(1,len(profits)+1)), y=profits,
        marker_color=colors, text=[f"${p:+,.0f}" for p in profits],
        textposition="outside", textfont=dict(size=11,color="#9ca3af")))
    fig.add_shape(type="line",x0=.5,x1=len(profits)+.5,y0=0,y1=0,
        line=dict(color="#4b5563",width=1),xref="x",yref="y")
    lo = _layout(title="Profit / Loss Per Trade", height=360, showlegend=False)
    lo["xaxis"]["title"] = "Trade #"; lo["xaxis"]["tickmode"] = "linear"
    lo["yaxis"]["title"] = "Profit USD($)"
    fig.update_layout(**lo)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# GROQ AI SUMMARY
# ═════════════════════════════════════════════════════════════════════════════

def get_groq_summary(ticker, metrics, signal, start_date, end_date):
    api_key = os.environ.get("GROQ_API_KEY","")
    if not api_key:
        return "⚠️ GROQ_API_KEY not set in .env"
    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are a friendly financial analyst explaining stock analysis results to someone with NO finance background.
Results of a technical analysis backtest on {ticker} from {start_date} to {end_date}:
- Net profit: ${metrics['net_return']:,.2f} (started $10,000, ended ${metrics['final_value']:,.2f})
- Annualised return: {metrics['ann_return']:.2f}% (S&P 500 averages ~10%)
- Sharpe ratio: {metrics['sharpe']:.2f} (above 1.0 is good)
- Win rate: {metrics['win_rate']:.1%} ({metrics['wins']} wins out of {metrics['n_trades']} trades)
- Biggest profit: ${metrics['best_trade']:,.2f} | Biggest loss: ${metrics['worst_trade']:,.2f}
- Max drawdown: ${metrics['max_dd']:,.2f}
- Current signal: {signal}
Write 4-5 technical English sentences: overall performance, what the current signal means, one strength, one risk, a cautionary note and insights regarding this stock that no one usually gives. No jargon, no bullets."""
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            max_tokens=320, temperature=0.65)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate AI summary: {e}"


# ═════════════════════════════════════════════════════════════════════════════
# HELPER — render full analysis from stored data OR live session
# ═════════════════════════════════════════════════════════════════════════════

def metric_card(label, value, cls=""):
    return f"""<div class='metric-card'>
        <div class='metric-label'>{label}</div>
        <div class='metric-value {cls}'>{value}</div></div>"""

def render_analysis(df, results, metrics, signal, signal_desc,
                    ticker, initial_cap, ai_summary):
    """Shared renderer — used both for live analysis and history view."""

    # Signal banner
    sc   = {"BUY":"signal-buy","SELL":"signal-sell","HOLD":"signal-hold"}[signal]
    icon = {"BUY":"🟢","SELL":"🔴","HOLD":"🟡"}[signal]
    st.markdown(f"""<div class='signal-banner {sc}'>
        <div class='signal-icon'>{icon}</div>
        <div><div class='signal-title'>{signal} — {ticker}</div>
        <div class='signal-desc'>{signal_desc}</div></div></div>""",
        unsafe_allow_html=True)

    # Metrics 4+4+4
    st.markdown("<div class='section-title'>Performance Metrics</div>", unsafe_allow_html=True)
    r1 = st.columns(4)
    r1[0].markdown(metric_card("Net Return",   f"${metrics['net_return']:+,.0f}", "green" if metrics['net_return']>=0 else "red"), unsafe_allow_html=True)
    r1[1].markdown(metric_card("Ann. Return",  f"{metrics['ann_return']:.1f}%",   "green" if metrics['ann_return']>=0 else "red"), unsafe_allow_html=True)
    r1[2].markdown(metric_card("Sharpe Ratio", f"{metrics['sharpe']:.2f}",        "green" if metrics['sharpe']>=1 else "amber"),  unsafe_allow_html=True)
    r1[3].markdown(metric_card("Win Rate",     f"{metrics['win_rate']:.1%}", "blue"), unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    r2 = st.columns(4)
    r2[0].markdown(metric_card("Final Value",  f"${metrics['final_value']:,.0f}", "green"), unsafe_allow_html=True)
    r2[1].markdown(metric_card("Max Drawdown", f"${metrics['max_dd']:,.0f}",      "red"),   unsafe_allow_html=True)
    r2[2].markdown(metric_card("Best Trade",   f"${metrics['best_trade']:+,.0f}", "green"), unsafe_allow_html=True)
    r2[3].markdown(metric_card("Worst Trade",  f"${metrics['worst_trade']:+,.0f}","red"),   unsafe_allow_html=True)
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    r3 = st.columns(4)
    r3[0].markdown(metric_card("Total Trades",   str(metrics['n_trades'])), unsafe_allow_html=True)
    r3[1].markdown(metric_card("Winning Trades", str(metrics['wins']),   "green"), unsafe_allow_html=True)
    r3[2].markdown(metric_card("Losing Trades",  str(metrics['losses']), "red"),   unsafe_allow_html=True)
    wl = f"{metrics['win_loss']:.1f}×" if metrics['win_loss']!=float("inf") else "∞"
    r3[3].markdown(metric_card("Win / Loss Ratio", wl, "blue"), unsafe_allow_html=True)

    # Charts
    if df is not None:
        st.markdown("<div class='section-title'>Price & Indicators</div>", unsafe_allow_html=True)
        t1,t2,t3,t4 = st.tabs(["📊 Candlestick","📉 Bollinger Bands","📦 OBV","⚡ RSI"])
        with t1: st.plotly_chart(chart_candlestick(df, ticker), use_container_width=True)
        with t2:
            st.plotly_chart(chart_bollinger(df, ticker), use_container_width=True)
            st.markdown("<div style='font-size:.82rem;color:#4b5563;'><b style='color:#fbbf24'>Midband</b> = 30-day SMA &nbsp;|&nbsp; <b style='color:#7c3aed'>Upper</b> = overbought &nbsp;|&nbsp; <b style='color:#0094ff'>Lower</b> = oversold</div>", unsafe_allow_html=True)
        with t3:
            st.plotly_chart(chart_obv(df), use_container_width=True)
            st.markdown("<div style='font-size:.82rem;color:#4b5563;'><b style='color:#00d4aa'>OBV</b> above <b style='color:#ff5252'>EMA</b> = buying pressure (bullish).</div>", unsafe_allow_html=True)
        with t4:
            st.plotly_chart(chart_rsi(df), use_container_width=True)
            st.markdown("<div style='font-size:.82rem;color:#4b5563;'><b style='color:#ff5252'>Above 90</b> = overbought &nbsp;|&nbsp; <b style='color:#00d4aa'>Below 30</b> = oversold</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>Buy / Sell Signals</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_signals(df, ticker), use_container_width=True)
        st.caption("▲ Green = BUY signal   |   ▼ Red = SELL signal")

    # Portfolio charts
    if results and results.get("port_values"):
        st.markdown("<div class='section-title'>Portfolio Performance</div>", unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca: st.plotly_chart(chart_portfolio(results["port_values"], initial_cap), use_container_width=True)
        with cb: st.plotly_chart(chart_profit_per_trade(results["profits"]),           use_container_width=True)

    # Trade log
    st.markdown("<div class='section-title'>Trade Log</div>", unsafe_allow_html=True)
    buy_s  = results["buy_signals"]  if results else []
    sell_s = results["sell_signals"] if results else []
    if buy_s:
        rows_html = ""
        for i in range(max(len(buy_s), len(sell_s))):
            bd  = str(buy_s[i]["date"])[:10]  if i<len(buy_s)  else "—"
            bp  = f"${buy_s[i]['price']:.2f}" if i<len(buy_s)  else "—"
            sd  = str(sell_s[i]["date"])[:10] if i<len(sell_s) else "—"
            sp  = f"${sell_s[i]['price']:.2f}"if i<len(sell_s) else "—"
            prf = sell_s[i]["profit"]          if i<len(sell_s) else None
            ptf = sell_s[i]["portfolio"]       if i<len(sell_s) else None
            status = "Closed" if i<len(sell_s) else "Open"
            if prf is not None:
                ps,pc,sc2 = f"${prf:+,.2f}","badge-green" if prf>=0 else "badge-red","badge-green"
                ptfs = f"${ptf:,.2f}"
            else:
                ps,pc,sc2,ptfs = "—","badge-amber","badge-amber","—"
            rows_html += f"<tr><td>{i+1}</td><td>{bd}</td><td>{bp}</td><td>{sd}</td><td>{sp}</td><td><span class='badge {pc}'>{ps}</span></td><td>{ptfs}</td><td><span class='badge {sc2}'>{status}</span></td></tr>"
        st.markdown(f"""<div style='background:#13161e;border:1px solid #1e2130;border-radius:12px;padding:20px;overflow-x:auto;'>
            <table class='trade-table'><thead><tr><th>#</th><th>Buy Date</th><th>Buy Price</th>
            <th>Sell Date</th><th>Sell Price</th><th>Profit</th><th>Portfolio</th><th>Status</th></tr></thead>
            <tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)
    else:
        st.info("No completed trades in this period.")

    # AI Summary
    st.markdown("<div class='section-title'>AI Analysis Summary</div>", unsafe_allow_html=True)
    if ai_summary:
        st.markdown(f"""<div class='ai-box'><div class='ai-label'>✦ AI Insight — Groq · Llama 3.3 70B</div>
            <div class='ai-text'>{ai_summary}</div></div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style='padding:8px 0 4px;'>
        <div style='font-family:Space Mono,monospace;font-size:1.3rem;font-weight:700;
            background:linear-gradient(90deg,#00d4aa,#0094ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;'>QuantEdge</div>
        <div style='font-size:.72rem;color:#4b5563;margin-top:2px;'>
            Logged in as <b style='color:#00d4aa'>{user['username']}</b>
        </div>
    </div>""", unsafe_allow_html=True)

    # Navigation
    st.markdown("---")
    page = st.session_state.get("page","analysis")
    col_n1, col_n2 = st.columns(2)
    if col_n1.button("📊 Analysis", use_container_width=True):
        st.session_state["page"] = "analysis"
        st.session_state.pop("view_analysis_id", None)
        st.rerun()
    if col_n2.button("🕘 History", use_container_width=True):
        st.session_state["page"] = "history"
        st.session_state.pop("view_analysis_id", None)
        st.rerun()

    st.markdown("---")
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""<div style='font-size:.78rem;color:#9ca3af;line-height:1.75;'>
        <b style='color:#00d4aa'>QuantEdge</b> backtests a 3-indicator strategy on any stock.<br><br>
        <b>1.</b> Enter a ticker (e.g. <code>AAPL</code>, <code>RELIANCE.NS</code>)<br>
        <b>2.</b> Pick a date range<br>
        <b>3.</b> Tune parameters if needed<br>
        <b>4.</b> Hit <b style='color:#00d4aa'>Run Analysis</b><br><br>
        Results are saved automatically. View past runs in <b>History</b>.<br><br>
        <b style='color:#ff5252'>Not financial advice.</b>
        </div>""", unsafe_allow_html=True)

    if st.session_state.get("page","analysis") == "analysis":
        st.markdown("### ⚙️ Configuration")
        ticker = st.text_input("Stock Ticker", value="AAPL",
            placeholder="e.g. AAPL, TSLA, RELIANCE.NS",
            help="Yahoo Finance ticker. Indian stocks: add .NS").upper().strip()
        c1,c2 = st.columns(2)
        with c1: start_date = st.date_input("Start", value=pd.to_datetime("2018-01-01"))
        with c2: end_date   = st.date_input("End",   value=pd.to_datetime("2024-01-01"))

        st.markdown("### 🔧 Strategy Parameters")
        bb_window = st.slider("BB Window (days)", 10, 60, 30)
        st.markdown("<div class='sidebar-tip'><b>Bollinger lookback.</b> Shorter = more signals. Longer = smoother, fewer.</div>", unsafe_allow_html=True)
        bb_mult = st.slider("BB Multiplier", 1.0, 3.0, 1.5, 0.1)
        st.markdown("<div class='sidebar-tip'><b>Band width.</b> 1.5 = tighter, triggers sooner. 2.5 = only extreme moves.</div>", unsafe_allow_html=True)
        rsi_span = st.slider("RSI Span (days)", 8, 30, 16)
        st.markdown("<div class='sidebar-tip'><b>RSI smoothing.</b> Lower = reacts faster. Higher = more stable signal.</div>", unsafe_allow_html=True)
        rsi_ob = st.slider("RSI Overbought", 70, 95, 90)
        st.markdown("<div class='sidebar-tip'><b>Sell trigger.</b> RSI above this = stock overheated. 90 = strict, 70 = standard.</div>", unsafe_allow_html=True)
        rsi_os = st.slider("RSI Oversold", 10, 40, 30)
        st.markdown("<div class='sidebar-tip'><b>Buy trigger.</b> RSI below this = beaten down too much. 30 = standard.</div>", unsafe_allow_html=True)
        initial_cap = st.number_input("Initial Capital ($)", 1000, 1_000_000, 10000, 1000)
        st.markdown("<div class='sidebar-tip'><b>Starting capital.</b> Strategy goes all-in per trade.</div>", unsafe_allow_html=True)

        run_btn = st.button("▶  Run Analysis", use_container_width=True)
    else:
        run_btn = False
        ticker = ""; start_date = end_date = None
        bb_window = 30; bb_mult = 1.5; rsi_span = 16
        rsi_ob = 90; rsi_os = 30; initial_cap = 10000

    st.markdown("---")
    if st.button("🚪 Log Out", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE ROUTING
# ═════════════════════════════════════════════════════════════════════════════

current_page = st.session_state.get("page","analysis")

# ─────────────────────────────────────────────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────────────────────────────────────────────
if current_page == "history":

    # ── Detail view ───────────────────────────────────────────────────────────
    if "view_analysis_id" in st.session_state:
        aid = st.session_state["view_analysis_id"]
        row = get_analysis_by_id(aid, user["id"])

        if st.button("← Back to History"):
            del st.session_state["view_analysis_id"]
            st.rerun()

        if not row:
            st.error("Analysis not found.")
            st.stop()

        m  = json.loads(row["metrics_json"])
        tl = json.loads(row["trades_json"])

        st.markdown(f"""
        <div style='padding:1.5rem 0 .5rem;'>
            <div class='main-header'>{row['ticker']}</div>
            <div class='sub-header'>{row['start_date']} → {row['end_date']} &nbsp;|&nbsp;
            BB:{row['bb_window']}d·{row['bb_mult']}× &nbsp;|&nbsp;
            RSI:{row['rsi_span']}d &nbsp;|&nbsp; Capital:${row['initial_cap']:,.0f} &nbsp;|&nbsp;
            Saved {row['created_at'][:10]}</div>
        </div>""", unsafe_allow_html=True)

        render_analysis(
            df=None,
            results=tl,
            metrics=m,
            signal=row["signal"],
            signal_desc="Historical signal at time of analysis",
            ticker=row["ticker"],
            initial_cap=row["initial_cap"],
            ai_summary=row["ai_summary"],
        )
        st.stop()

    # ── Cards view ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='padding:1.5rem 0 .5rem;'>
        <div class='main-header'>History</div>
        <div class='sub-header'>All your previous analyses — click any card to view in full</div>
    </div>""", unsafe_allow_html=True)

    analyses = get_user_analyses(user["id"])

    if not analyses:
        st.markdown("""
        <div style='background:#13161e;border:1px dashed #1e2130;border-radius:14px;
            padding:56px 48px;text-align:center;margin-top:2rem;'>
            <div style='font-size:3rem;margin-bottom:16px;'>📂</div>
            <div style='font-family:Space Mono,monospace;font-size:1rem;color:#e8eaf0;margin-bottom:8px;'>
                No analyses yet</div>
            <div style='font-size:.88rem;color:#4b5563;'>
                Run your first analysis on the Analysis page.</div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # Signal colour map
    sig_colors = {"BUY":"#00d4aa","SELL":"#ff5252","HOLD":"#fbbf24"}
    sig_icons  = {"BUY":"🟢","SELL":"🔴","HOLD":"🟡"}

    # 3-column grid
    cols_per_row = 3
    for row_start in range(0, len(analyses), cols_per_row):
        cols = st.columns(cols_per_row)
        for ci, analysis in enumerate(analyses[row_start:row_start+cols_per_row]):
            m   = json.loads(analysis["metrics_json"])
            sc  = sig_colors.get(analysis["signal"],"#fbbf24")
            ico = sig_icons.get(analysis["signal"],"🟡")
            nr  = m.get("net_return",0)
            ar  = m.get("ann_return",0)
            wr  = m.get("win_rate",0)
            nt  = m.get("n_trades",0)
            nr_color = "#00d4aa" if nr>=0 else "#ff5252"
            ar_color = "#00d4aa" if ar>=0 else "#ff5252"
            created  = analysis["created_at"][:10]

            with cols[ci]:
                st.markdown(f"""
                <div style='background:#13161e;border:1px solid #1e2130;border-radius:14px;
                    padding:20px 22px;margin-bottom:4px;transition:border-color .2s;
                    border-left:4px solid {sc};'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;'>
                        <div>
                            <div style='font-family:Space Mono,monospace;font-size:1.2rem;
                                font-weight:700;color:#e8eaf0;'>{analysis['ticker']}</div>
                            <div style='font-size:.72rem;color:#4b5563;margin-top:2px;'>
                                {analysis['start_date']} → {analysis['end_date']}</div>
                        </div>
                        <div style='font-size:1.4rem;'>{ico}</div>
                    </div>
                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;'>
                        <div style='background:#0d0f14;border-radius:8px;padding:8px;text-align:center;'>
                            <div style='font-size:.65rem;color:#6b7280;text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px;'>Net Return</div>
                            <div style='font-family:Space Mono,monospace;font-size:.95rem;font-weight:700;color:{nr_color};'>${nr:+,.0f}</div>
                        </div>
                        <div style='background:#0d0f14;border-radius:8px;padding:8px;text-align:center;'>
                            <div style='font-size:.65rem;color:#6b7280;text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px;'>Ann. Return</div>
                            <div style='font-family:Space Mono,monospace;font-size:.95rem;font-weight:700;color:{ar_color};'>{ar:.1f}%</div>
                        </div>
                        <div style='background:#0d0f14;border-radius:8px;padding:8px;text-align:center;'>
                            <div style='font-size:.65rem;color:#6b7280;text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px;'>Win Rate</div>
                            <div style='font-family:Space Mono,monospace;font-size:.95rem;font-weight:700;color:#0094ff;'>{wr:.0%}</div>
                        </div>
                        <div style='background:#0d0f14;border-radius:8px;padding:8px;text-align:center;'>
                            <div style='font-size:.65rem;color:#6b7280;text-transform:uppercase;letter-spacing:.8px;margin-bottom:2px;'>Trades</div>
                            <div style='font-family:Space Mono,monospace;font-size:.95rem;font-weight:700;color:#e8eaf0;'>{nt}</div>
                        </div>
                    </div>
                    <div style='font-size:.72rem;color:#4b5563;margin-bottom:12px;'>
                        BB:{analysis['bb_window']}d · {analysis['bb_mult']}× &nbsp;|&nbsp;
                        RSI:{analysis['rsi_span']}d &nbsp;|&nbsp;
                        ${analysis['initial_cap']:,.0f} capital &nbsp;|&nbsp;
                        Saved {created}
                    </div>
                </div>""", unsafe_allow_html=True)

                if st.button(f"View Full Analysis →", key=f"view_{analysis['id']}",
                             use_container_width=True):
                    st.session_state["view_analysis_id"] = analysis["id"]
                    st.rerun()

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS PAGE
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:2rem 0 1rem;'>
    <div class='main-header'>QuantEdge</div>
    <div class='sub-header'>Bollinger Bands · On-Balance Volume · RSI &nbsp;|&nbsp; 2-of-3 consensus engine</div>
</div>""", unsafe_allow_html=True)

# Landing screen
if not run_btn and "df_result" not in st.session_state:
    st.markdown("""
    <div style='background:#13161e;border:1px dashed #1e2130;border-radius:14px;
        padding:56px 48px;text-align:center;margin-top:2rem;'>
        <div style='font-size:3rem;margin-bottom:16px;'>📊</div>
        <div style='font-family:Space Mono,monospace;font-size:1.1rem;color:#e8eaf0;margin-bottom:12px;'>
            Configure & Run Analysis</div>
        <div style='font-size:.9rem;color:#4b5563;max-width:460px;margin:0 auto;line-height:1.75;'>
            Enter a stock ticker, pick a date range, and hit
            <b style='color:#00d4aa'>▶ Run Analysis</b> in the sidebar.<br><br>
            QuantEdge downloads price data, computes three technical indicators
            (Bollinger Bands, OBV, RSI), and runs a backtest using a 2-of-3 consensus rule.
            Results are saved to your account automatically.
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Run analysis ──────────────────────────────────────────────────────────────
if run_btn:
    # ── Duplicate check ───────────────────────────────────────────────────────
    dup = duplicate_analysis(user["id"], ticker, start_date, end_date,
                             bb_window, bb_mult, rsi_span, rsi_ob, rsi_os, initial_cap)
    if dup:
        m_dup = json.loads(dup["metrics_json"])
        st.markdown(f"""
        <div class='dup-banner'>
            <div style='font-family:Space Mono,monospace;font-size:1rem;font-weight:700;
                color:#fbbf24;margin-bottom:8px;'>⚠️ Duplicate Analysis Detected</div>
            <div style='font-size:.88rem;color:#9ca3af;line-height:1.7;'>
                You already ran this exact analysis on <b style='color:#e8eaf0'>{ticker}</b>
                ({start_date} → {end_date}) with identical parameters on
                <b style='color:#e8eaf0'>{dup['created_at'][:10]}</b>.<br>
                It returned a net return of
                <b style='color:#00d4aa'>${m_dup['net_return']:+,.0f}</b> with a
                <b style='color:#00d4aa'>{m_dup['ann_return']:.1f}%</b> annualised return.
            </div>
        </div>""", unsafe_allow_html=True)

        col_dup1, col_dup2, col_dup3 = st.columns([2,2,3])
        view_old = col_dup1.button("📂 View Previous Analyses")
        force_new = col_dup2.button("🔄 Run Again Anyway")

        if view_old:
            st.session_state["page"] = "history"
            st.rerun()
        if not force_new:
            st.stop()

    # ── Actual run ────────────────────────────────────────────────────────────
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

            # Generate AI summary
            ai_summary = get_groq_summary(ticker, metrics,
                f"{signal} — {signal_desc}", str(start_date), str(end_date))

            # Save to DB
            trade_log = {"profits":     results["profits"],
                         "port_values": results["port_values"],
                         "buy_signals": results["buy_signals"],
                         "sell_signals":results["sell_signals"],
                         "final_value": results["final_value"],
                         "initial":     results["initial"]}
            save_analysis(user["id"], ticker, start_date, end_date,
                          bb_window, bb_mult, rsi_span, rsi_ob, rsi_os,
                          initial_cap, signal, metrics, trade_log, ai_summary)

            st.session_state.update({
                "df_result":   df, "results": results, "metrics": metrics,
                "signal":      signal, "signal_desc": signal_desc,
                "ticker":      ticker, "start_date": str(start_date),
                "end_date":    str(end_date), "years": years,
                "initial_cap": initial_cap, "ai_summary": ai_summary,
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
initial_cap = st.session_state.get("initial_cap", 10000)
ai_summary  = st.session_state.get("ai_summary","")

if not metrics:
    st.warning("No trades executed. Try a longer date range or looser thresholds.")
    st.stop()

render_analysis(df, results, metrics, signal, signal_desc,
                ticker, initial_cap, ai_summary)

st.markdown("""
<div style='font-size:.72rem;color:#374151;margin-top:32px;text-align:center;
    padding-top:16px;border-top:1px solid #1e2130;'>
    QuantEdge is for educational purposes only. Not financial advice.
    Past performance does not guarantee future results.
</div>""", unsafe_allow_html=True)