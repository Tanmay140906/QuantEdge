# QuantEdge 📈

QuantEdge is a Streamlit-based algorithmic trading strategy web app that backtests a multi-indicator technical analysis strategy using **Bollinger Bands**, **On-Balance Volume (OBV)**, and **Relative Strength Index (RSI)**.

The app downloads historical stock data from Yahoo Finance, computes the indicators, runs a simple 2-of-3 voting strategy, visualizes the trades, calculates performance metrics, and generates a plain-English AI summary using Groq.

> **Disclaimer:** This project is for educational and research purposes only. It is not financial advice. Past performance does not guarantee future returns.

---

## Features

- Interactive Streamlit dashboard
- Historical stock data using `yfinance`
- Bollinger Bands, OBV, OBV EMA, and RSI indicator calculation
- 2-of-3 consensus-based buy/sell strategy
- Buy and sell signal visualization
- Portfolio value and profit/loss charts
- Trade log with open and closed trades
- Performance metrics including:
  - Net return
  - Annualised return
  - Sharpe ratio
  - Win rate
  - Max drawdown
  - Best and worst trade
  - Win/loss ratio
- AI-generated analysis summary powered by Groq Llama 3.3 70B
- Custom dark UI with Plotly charts

---

## Tech Stack

- **Python**
- **Streamlit** for the web interface
- **yfinance** for stock market data
- **Pandas** and **NumPy** for data processing
- **Plotly** for interactive charts
- **Groq API** for AI-generated summary
- **python-dotenv** for environment variable management

---

## Strategy Overview

QuantEdge uses a **2-of-3 voting system**. A trade signal is generated only when at least two of the three indicators agree.

### Indicators Used

#### 1. Bollinger Bands

Bollinger Bands are used to detect whether the stock price is stretched too far above or below its recent average.

- If the closing price goes above the upper band, the stock may be overbought.
- If the closing price goes below the lower band, the stock may be oversold.

In this app:

- Midband = rolling average of closing price
- Upper Band = Midband + multiplier × standard deviation
- Lower Band = Midband - multiplier × standard deviation

Default configuration:

```text
Window: 30 days
Multiplier: 1.5
```

#### 2. On-Balance Volume

OBV tracks buying and selling pressure using price movement and volume.

- If the closing price rises, volume is added to OBV.
- If the closing price falls, volume is subtracted from OBV.
- If OBV is above its EMA, it is treated as bullish.
- If OBV is below its EMA, it is treated as bearish.

Default configuration:

```text
OBV EMA span: 20 days
```

#### 3. RSI

RSI measures price momentum.

- RSI above the overbought threshold suggests the stock may be overheated.
- RSI below the oversold threshold suggests the stock may be beaten down and may reverse.

Default configuration:

```text
RSI span: 16 days
Overbought threshold: 90
Oversold threshold: 30
```

---

## Buy/Sell Logic

### Buy Signal

A buy signal is generated when at least **2 out of 3** conditions are true:

```text
1. Close price is below the lower Bollinger Band
2. OBV is above OBV EMA
3. RSI is below the oversold threshold
```

When a buy signal appears, the strategy invests the full available portfolio value into the stock at the next day's open price.

### Sell Signal

A sell signal is generated when at least **2 out of 3** conditions are true:

```text
1. Close price is above the upper Bollinger Band
2. OBV is below OBV EMA
3. RSI is above the overbought threshold
```

When a sell signal appears, the strategy exits the full position at the next day's open price.

### Hold Signal

If fewer than two indicators agree, the app shows a `HOLD` signal. This means there is no strong consensus among the indicators.

---

## How the Backtest Works

1. The user enters a stock ticker and date range.
2. The app downloads daily historical data from Yahoo Finance.
3. It calculates Bollinger Bands, OBV, OBV EMA, and RSI.
4. It scans through the historical data one day at a time.
5. If 2 or more indicators give a buy signal and there is no open position, the strategy buys.
6. If 2 or more indicators give a sell signal and there is an open position, the strategy sells.
7. Every completed trade is stored with buy price, sell price, profit/loss, and portfolio value.
8. The app calculates final metrics and displays charts, trade logs, and AI analysis.

---

## Project Structure

A simple project structure can look like this:

```text
quantedge/
│
├── app.py
├── README.md
├── requirements.txt
└── .env
```

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd quantedge
```

### 2. Create a Virtual Environment

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit
yfinance
numpy
pandas
plotly
groq
python-dotenv
```

Then install them:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

The AI summary feature uses the Groq API. To enable it, create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

If this key is not provided, the app will still run, but the AI summary section will show a warning instead of generating an analysis.

For Streamlit Cloud deployment, you can also add the key inside Streamlit secrets:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

---

## How to Run the App

Run the Streamlit app using:

```bash
streamlit run app.py
```

After running the command, Streamlit will open the app in your browser.

Usually, it will be available at:

```text
http://localhost:8501
```

---

## How to Use QuantEdge

1. Open the app in your browser.
2. Enter a valid Yahoo Finance stock ticker.
   - Example: `AAPL`, `TSLA`, `MSFT`
   - For Indian stocks, use `.NS`
   - Example: `RELIANCE.NS`, `INFY.NS`, `TCS.NS`
3. Select a start date and end date.
4. Adjust strategy parameters if required:
   - Bollinger Band window
   - Bollinger Band multiplier
   - RSI span
   - RSI overbought threshold
   - RSI oversold threshold
   - Initial capital
5. Click **Run Analysis**.
6. View the generated results:
   - Current signal
   - Performance metrics
   - Candlestick chart
   - Bollinger Band chart
   - OBV chart
   - RSI chart
   - Buy/sell signal chart
   - Portfolio performance charts
   - Trade log
   - AI-generated summary

---

## Example Tickers

| Market | Example Tickers |
|---|---|
| US Stocks | `AAPL`, `MSFT`, `TSLA`, `NVDA`, `GOOGL` |
| Indian Stocks | `RELIANCE.NS`, `INFY.NS`, `TCS.NS`, `HDFCBANK.NS` |
| ETFs | `SPY`, `QQQ`, `VOO` |

---

## Important Notes

- The app depends on Yahoo Finance data, so results depend on data availability and ticker correctness.
- Very short date ranges may not work because the indicators need enough historical data.
- The strategy uses next-day open price for trade execution.
- The backtest assumes full capital deployment on every buy signal.
- Transaction charges, taxes, slippage, brokerage, and liquidity constraints are not included.
- The strategy does not guarantee profitability.
- The AI summary is only an explanation of the backtest result, not investment advice.

---

## Performance Metrics Explained

| Metric | Meaning |
|---|---|
| Net Return | Final portfolio value minus initial capital |
| Annualised Return | Estimated yearly return over the selected period |
| Sharpe Ratio | Risk-adjusted return measure |
| Win Rate | Percentage of profitable trades |
| Max Drawdown | Largest fall from a previous portfolio peak |
| Best Trade | Highest profit from a single trade |
| Worst Trade | Biggest loss from a single trade |
| Win/Loss Ratio | Number of winning trades divided by losing trades |

---

## Limitations

This project is a clean educational backtesting dashboard, but it is not a production-grade trading system.

Current limitations include:

- No transaction cost modeling
- No slippage modeling
- No stop-loss or take-profit system
- No position sizing logic beyond all-in allocation
- No live trading execution
- No portfolio-level multi-stock backtesting
- No walk-forward validation
- No benchmark comparison chart
- No risk management module

---

## Possible Future Improvements

- Add transaction charges and slippage
- Add benchmark comparison against S&P 500 or NIFTY 50
- Add CAGR, volatility, Sortino ratio, and Calmar ratio
- Add stop-loss and take-profit options
- Add multi-stock portfolio backtesting
- Add downloadable trade report as CSV
- Add strategy parameter optimization
- Add live market mode
- Add authentication for saved user analyses
- Add database support to store previous backtests

---

## Educational Purpose

QuantEdge is designed to help users understand how technical indicators can be combined into a simple trading strategy. It is useful for learning:

- Technical analysis basics
- Backtesting workflow
- Financial dashboard development
- Streamlit UI building
- Interactive Plotly charting
- Basic trading signal design
- AI-assisted result explanation

---

## Disclaimer

This software is provided for learning, experimentation, and research only.

It should not be used as the sole basis for buying, selling, or holding any financial asset. Always do your own research and consult a qualified financial advisor before making investment decisions.
