# QuantEdge 📈  
### A Streamlit-Based Algorithmic Trading Strategy Backtester

QuantEdge is an interactive algorithmic trading strategy backtesting web application built with Python and Streamlit.

It allows users to select a stock, choose a historical date range, adjust strategy parameters, and test how a technical-analysis-based trading strategy would have performed in the past.

The application uses three popular technical indicators:

- Bollinger Bands
- On-Balance Volume (OBV)
- Relative Strength Index (RSI)

Instead of depending on only one indicator, QuantEdge uses a 2-out-of-3 voting system. A trade signal is generated only when at least two indicators agree. This makes the strategy more reliable than using a single indicator in isolation.

QuantEdge also includes user authentication, SQLite-based storage for previous analyses, interactive Plotly charts, performance metrics, trade logs, and an AI-generated analysis summary powered by Groq.

---

## Disclaimer

QuantEdge is built strictly for educational, learning, and research purposes.

It is not financial advice.

The results shown by this application are based on historical market data. Past performance does not guarantee future returns. This app should not be used as the only basis for buying, selling, or holding any stock or financial asset.

Always do your own research or consult a qualified financial advisor before making real investment decisions.

---

## Table of Contents

- Project Overview
- Why QuantEdge Was Built
- Features
- Tech Stack
- How the Application Works
- Project Structure
- Setup Instructions
- Environment Variables
- How to Run the Project
- How to Use the Application
- Input Parameters Explained
- Indicators Explained
- Strategy Logic
- Backtesting Flow
- Charts and Visualizations
- Performance Metrics
- Trade Log
- AI Summary
- Previous Analysis History
- Example Tickers
- Important Notes
- Limitations
- Future Improvements
- Educational Value
- Author

---

## Project Overview

QuantEdge is a complete beginner-friendly trading analysis dashboard.

The user enters a stock ticker, selects a historical date range, customizes technical indicator parameters, and runs the analysis. The app downloads historical stock data using Yahoo Finance, calculates indicators, generates buy/sell/hold signals, simulates trades, calculates performance metrics, and displays the result visually.

The final output includes:

- Current strategy signal
- Candlestick price chart
- Bollinger Bands chart
- OBV chart
- RSI chart
- Buy and sell signal chart
- Portfolio performance chart
- Profit/loss chart
- Trade log
- Key performance metrics
- AI-generated explanation
- Saved analysis history

The main goal of this project is to help users understand how technical indicators are used in algorithmic trading and how trading strategies can be tested using historical data.

---

## Why QuantEdge Was Built

Many beginners learn technical indicators like RSI, Bollinger Bands, and volume analysis separately, but they often struggle to understand how these indicators can be combined into an actual strategy.

QuantEdge solves this by providing a practical dashboard where users can:

- Select real stocks
- Test the strategy on real historical data
- See where the strategy would have bought and sold
- Understand whether the strategy made profit or loss
- Read beginner-friendly AI explanations
- Store and revisit previous analyses

This makes QuantEdge useful for students, beginner traders, developers, and anyone learning about algorithmic trading and financial dashboards.

---

## Features

### User Authentication

QuantEdge includes a login and signup system.

Users can create an account and then log in to access the main dashboard. This allows each user to maintain their own analysis history.

---

### Stock Backtesting

Users can enter a stock ticker and test the strategy over a selected historical period.

The application fetches historical stock data using Yahoo Finance through the `yfinance` Python library.

---

### Technical Indicators

QuantEdge calculates and visualizes:

- Bollinger Bands
- On-Balance Volume
- OBV EMA
- RSI

These indicators are used to generate trading signals.

---

### 2-of-3 Voting Strategy

The strategy does not blindly follow a single indicator.

A BUY or SELL signal is generated only when at least two out of the three indicators agree.

This creates a more balanced decision-making system.

---

### Interactive Charts

The app uses Plotly to display interactive charts.

Users can zoom, hover, and inspect values on the graphs.

Charts include:

- Candlestick chart
- Bollinger Bands chart
- OBV chart
- RSI chart
- Buy/sell signal chart
- Portfolio value chart
- Profit/loss per trade chart

---

### Performance Metrics

QuantEdge calculates several important performance metrics such as:

- Net return
- Annualised return
- Sharpe ratio
- Win rate
- Max drawdown
- Best trade
- Worst trade
- Total trades
- Winning trades
- Losing trades
- Win/loss ratio

These metrics help users evaluate whether the strategy performed well or poorly.

---

### AI-Generated Summary

QuantEdge uses Groq to generate a plain-English explanation of the backtest result.

This helps beginners understand the analysis without needing deep financial knowledge.

---

### Previous Analysis History

The app stores previous analyses in SQLite.

Users can go to the History page and view their past analyses without running the same backtest again.

---

### Duplicate Analysis Detection

If the user tries to run the exact same analysis again with the same ticker, date range, capital, and parameters, the app can detect that a similar analysis already exists.

This helps avoid unnecessary repeated calculations.

---

## Tech Stack

QuantEdge uses the following technologies:

- Python
- Streamlit
- yfinance
- Pandas
- NumPy
- Plotly
- SQLite
- Groq API
- python-dotenv

`python-dotenv` is used to load environment variables from a `.env` file.

This is mainly used for securely loading the Groq API key.

---

## How the Application Works

At a high level, QuantEdge follows this flow:

1. User signs up or logs in.
2. User goes to the Analysis page.
3. User enters a stock ticker.
4. User selects a start date and end date.
5. User adjusts technical indicator parameters if needed.
6. User enters initial capital.
7. App downloads historical stock data.
8. App calculates Bollinger Bands, OBV, OBV EMA, and RSI.
9. App applies the 2-of-3 trading strategy.
10. App simulates buy and sell trades.
11. App calculates performance metrics.
12. App displays charts, trade log, and summary.
13. App stores the result in SQLite.
14. User can revisit the result from the History page.

---

## Project Structure

The project structure looks like this:

```text
QuantEdge/
│
├── app.py
├── auth.py
├── database.py
├── run.py
├── quantedge.db
├── requirements.txt
├── README.md
└── .env
```


### Setup Instructions

## 1. Prerequisites

Before setting up the project, make sure you have the following installed:

- Python 3.10 or above
- Git
- pip
- A code editor such as VS Code
- Internet connection for downloading stock data from Yahoo Finance

You can check your Python version using:

```bash
python --version
```

or:

```bash
python3 --version
```

You can check Git using:

```bash
git --version
```

---

## 2. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/Tanmay140906/QuantEdge.git
```

Move inside the project folder:

```bash
cd QuantEdge
```

---

## 3. Create a Virtual Environment

A virtual environment keeps the project dependencies separate from your system Python packages.

### For Windows

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

### For macOS/Linux

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

After activation, your terminal should show something like:

```text
(venv)
```

---

## 4. Install Dependencies

Install all required Python packages using:

```bash
pip install -r requirements.txt
```

If you face any issue with `requirements.txt`, install the main dependencies manually:

```bash
pip install streamlit yfinance pandas numpy plotly groq python-dotenv
```

---

## 5. Create the Environment File

QuantEdge uses the Groq API for generating the AI analysis summary.

Create a file named `.env` in the root folder of the project.

Inside `.env`, add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace `your_groq_api_key_here` with your actual Groq API key.

The Groq API key is optional for the main backtesting features. If you do not add it, the app can still run, but the AI summary section may not work.

---

## 6. Run the Application

Run the Streamlit app using:

```bash
streamlit run app.py
```

If the project includes `run.py`, you may also run:

```bash
python run.py
```

After running the command, Streamlit will start a local server.

Usually, the app will open automatically in your browser.

If it does not open automatically, go to:

```text
http://localhost:8501
```

---

## 7. Create an Account

When the application opens, you will see the authentication screen.

If you are using the app for the first time:

1. Click or switch to the **Sign Up** section.
2. Enter your username.
3. Enter your email.
4. Enter your password.
5. Confirm your password.
6. Create your account.

After signing up, log in using your username and password.

---

## 8. Run Your First Analysis

After login, go to the **Analysis** page.

Enter the required details:

- Stock ticker
- Start date
- End date
- Bollinger Band window
- Bollinger Band multiplier
- RSI span
- RSI overbought threshold
- RSI oversold threshold
- Initial capital

Example tickers:

```text
AAPL
MSFT
TSLA
NVDA
RELIANCE.NS
TCS.NS
INFY.NS
```

For Indian stocks, use `.NS` at the end of the ticker.

Example:

```text
RELIANCE.NS
HDFCBANK.NS
TCS.NS
```

Click **Run Analysis** to start the backtest.

---

## 9. View the Results

After running the analysis, the app will show:

- Current signal: BUY, SELL, or HOLD
- Performance metrics
- Candlestick chart
- Bollinger Bands chart
- OBV chart
- RSI chart
- Buy/sell signal chart
- Portfolio value chart
- Profit/loss chart
- Trade log
- AI-generated summary, if Groq API is configured

---

## 10. View Previous Analyses

Go to the **History** page to see previously saved analyses.

The app stores previous analyses using SQLite, so you can revisit old results without running the same analysis again.

Each saved analysis may include:

- Stock ticker
- Date range
- Initial capital
- Strategy parameters
- Performance metrics
- Saved timestamp

---

## 11. Common Issues and Fixes

### Streamlit command not found

Install Streamlit:

```bash
pip install streamlit
```

Then run again:

```bash
streamlit run app.py
```

---

### ModuleNotFoundError

If you get an error like:

```text
ModuleNotFoundError: No module named 'yfinance'
```

Install dependencies again:

```bash
pip install -r requirements.txt
```

Or install the missing package manually:

```bash
pip install yfinance
```

---

### Groq API summary not working

Check that your `.env` file exists in the root project folder and contains:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Also make sure the package is installed:

```bash
pip install groq python-dotenv
```

---

### No stock data found

This usually happens because:

- The ticker is incorrect
- Yahoo Finance does not support the ticker
- The selected date range has no available data
- Your internet connection is not working

Try using a common ticker such as:

```text
AAPL
MSFT
RELIANCE.NS
```

---

### Very few or no trades generated

This can happen when:

- The selected date range is too short
- The strategy conditions are too strict
- The Bollinger Bands are too wide
- RSI thresholds are too extreme
- The stock did not trigger enough buy/sell conditions

Try increasing the date range or adjusting the strategy parameters.
