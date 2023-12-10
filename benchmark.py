import numpy as np
import bs4 as bs
import requests
from data import ticker_valid


def get_sp500_tickers(sector = None):
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip()
        if ticker_valid(ticker, error_out=False) and (sector is None or (row.findAll('td')[2].text == sector)) :
            tickers.append(ticker)

    return tickers

def get_sp500_sector_tickers(ticker):
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    ticker_sector_dict = {row.findAll('td')[0].text.strip():row.findAll('td')[2].text for row in table.findAll('tr')[1:]}

    sector = ticker_sector_dict[ticker]

    sector_tickers = [ticker  for ticker in ticker_sector_dict.keys() if (ticker_valid(ticker, error_out=False) and ticker_sector_dict[ticker] == sector)]
    return sector_tickers

# print(get_sp500_tickers(sector="Information Technology"))
print(get_sp500_sector_tickers('AAPL'))