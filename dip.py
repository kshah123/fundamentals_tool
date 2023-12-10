# Start with list of companies
import numpy as np
import os
import yfinance as yf
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# For each company, calculate current price - 200d sma / 200d sma
tickers = [file.split(".xlsx")[0] for file in os.listdir("./data/")]

dip_dict = dict.fromkeys(tickers)

start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

for ticker in tickers:
    stock = yf.Ticker(ticker)
    price_hist = stock.history(start=start_date, end=end_date, interval='1d')
    sma200 = np.average(price_hist['Close'])

    dip_dict[ticker] = ((price_hist["Close"].tail(1) - sma200)/sma200)[0]

dip_dict = dict(sorted(dip_dict.items(), key=lambda item: item[1]))

fig = make_subplots(rows=1, cols=1,
                    subplot_titles=["200-day Surge/Dip"])

fig.add_trace(go.Bar(x=list(dip_dict.keys()), y=list(dip_dict.values())))

fig.show()