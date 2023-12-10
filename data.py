import numpy as np
import pandas as pd
import yfinance as yf
import os
import shutil

tickers_path = "./tickers.txt"

def read_tickers():    
    if os.path.isfile(tickers_path):
        tickers_file = open(tickers_path, 'r')
        ticker_list = [ticker.strip() for ticker in tickers_file.readlines()]
        return ticker_list
    return []

def write_tickers(ticker_list):
    tickers_file = open(tickers_path, 'w+')
    tickers_file.writelines([ticker + "\n" for ticker in ticker_list])

data_dir = "./data"

def update_company(ticker, freq):
    ticker_valid(ticker)

    stock = yf.Ticker(ticker)
    
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    data_path = os.path.join(data_dir, ticker + "_" + freq + ".xlsx")

    current_stored_tickers = read_tickers()
    if ticker not in current_stored_tickers:
        write_tickers([*current_stored_tickers, ticker])

    # If this is the first time pulling data for ticker
    if not os.path.exists(data_path):
        # Get statement and transpose
        balance_sheet = pd.DataFrame.transpose(stock.get_balance_sheet(freq=freq))
        
        # Get around using index by creating "Date" column - necessary for proper handling
        balance_sheet["Date"] = [date.strftime('%Y-%m-%d') for date in balance_sheet.index]

        income_stmt = pd.DataFrame.transpose(stock.get_income_stmt(freq=freq))        
        income_stmt["Date"] = [date.strftime('%Y-%m-%d') for date in income_stmt.index]

        cash_flow = pd.DataFrame.transpose(stock.get_cash_flow(freq=freq))        
        cash_flow["Date"] = [date.strftime('%Y-%m-%d') for date in cash_flow.index]

        # Write to separate sheets within 1 spreadsheet
        with pd.ExcelWriter(data_path, mode='w') as writer:  
            balance_sheet.to_excel(writer, sheet_name='Balance Sheet')
            income_stmt.to_excel(writer, sheet_name='Income Statement')
            cash_flow.to_excel(writer, sheet_name='Cash Flow')

        # Backup new ticker
        backup_data()

    else:
        # Check for new data
        _, new_data_bal = update_balance_sheet(ticker, freq)
        _, new_data_inc = update_income_stmt(ticker, freq)
        _, new_data_cash = update_cash_flow(ticker, freq)
        
        # If new data, update all companies
        if new_data_bal or new_data_inc or new_data_cash:
            print("New data found, pulling data for all stored tickers. This may take some time.")
            
            stored_tickers = [file.split(".xlsx")[0] for file in os.listdir("./data/")]
            
            for stored_ticker in stored_tickers:
                balance_sheet, _ = update_balance_sheet(stored_ticker, freq)
                income_stmt, _ = update_income_stmt(stored_ticker, freq)
                cash_flow, _ = update_cash_flow(stored_ticker, freq)
                
                data_path = os.path.join(data_dir, stored_ticker + "_" + freq + ".xlsx")
                with pd.ExcelWriter(data_path) as writer:  
                    balance_sheet.to_excel(writer, sheet_name='Balance Sheet')
                    income_stmt.to_excel(writer, sheet_name='Income Statement')
                    cash_flow.to_excel(writer, sheet_name='Cash Flow')

            # Backup new updated data
            backup_data()

            print("Done updating all tickers!")

def update_balance_sheet(ticker, freq):
    stock = yf.Ticker(ticker)
    data_path = os.path.join(data_dir, ticker + "_" + freq + ".xlsx")
    found_new_data = False

    # Pull stored data
    current_known_data = pd.read_excel(data_path, sheet_name="Balance Sheet")
    
    # Get new data, transpose, and add "Date" column
    new_data = pd.DataFrame.transpose(stock.get_balance_sheet(freq=freq))
    new_data["Date"] = [date.strftime('%Y-%m-%d') for date in new_data.index]

    # Check if there is any new data available
    for date in new_data["Date"]:
        if date not in np.array(current_known_data["Date"]):
            found_new_data = True

    # Check if any of the dates in stored data are not in new data
    # Done this way instead of the intuitive way to preserve file size
    # Otherwise each time this function is called, a new column is added
    for date in current_known_data["Date"]:
        if date not in np.array(new_data["Date"]):
            for key in new_data.keys():
                # Copy over stored data into (potentially) new data 
                new_data.loc[date, key] = current_known_data[date, key]

    # Sort by date and reset index to be in right order
    new_data.sort_values("Date", ascending=False ,inplace=True)
    new_data.reset_index()

    return new_data, found_new_data

def update_income_stmt(ticker, freq):
    stock = yf.Ticker(ticker)
    data_path = os.path.join(data_dir, ticker + "_" + freq + ".xlsx")
    found_new_data = False

    # Pull stored data
    current_known_data = pd.read_excel(data_path, sheet_name="Income Statement")
    
    # Get new data, transpose, and add "Date" column
    new_data = pd.DataFrame.transpose(stock.get_income_stmt(freq=freq))
    new_data["Date"] = [date.strftime('%Y-%m-%d') for date in new_data.index]

    # Check if there is any new data available
    for date in new_data["Date"]:
        if date not in np.array(current_known_data["Date"]):
            found_new_data = True

    # Check if any of the dates in stored data are not in new data
    # Done this way instead of the intuitive way to preserve file size
    # Otherwise each time this function is called, a new column is added
    for date in current_known_data["Date"]:
        if date not in np.array(new_data["Date"]):
            for key in new_data.keys():
                # Copy over stored data into (potentially) new data 
                new_data.loc[date, key] = current_known_data[date, key]

    # Sort by date and reset index to be in right order
    new_data.sort_values("Date", ascending=False ,inplace=True)
    new_data.reset_index()

    return new_data, found_new_data

def update_cash_flow(ticker, freq):
    stock = yf.Ticker(ticker)
    data_path = os.path.join(data_dir, ticker + "_" + freq + ".xlsx")
    found_new_data = False

    # Pull stored data
    current_known_data = pd.read_excel(data_path, sheet_name="Cash Flow")
    
    # Get new data, transpose, and add "Date" column
    new_data = pd.DataFrame.transpose(stock.get_cash_flow(freq=freq))
    new_data["Date"] = [date.strftime('%Y-%m-%d') for date in new_data.index]
    
    # Check if there is any new data available
    for date in new_data["Date"]:
        if date not in np.array(current_known_data["Date"]):
            found_new_data = True

    # Check if any of the dates in stored data are not in new data
    # Done this way instead of the intuitive way to preserve file size
    # Otherwise each time this function is called, a new column is added
    for date in current_known_data["Date"]:
        if date not in np.array(new_data["Date"]):
            for key in new_data.keys():
                # Copy over stored data into (potentially) new data 
                new_data.loc[date, key] = current_known_data[date, key]

    # Sort by date and reset index to be in right order
    new_data.sort_values("Date", ascending=False ,inplace=True)
    new_data.reset_index()

    return new_data, found_new_data


def backup_data(backup_path = "./backup_data/"):
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)

    shutil.copytree("./data", backup_path)

def ticker_valid(ticker, error_out = True):
    stock = yf.Ticker(ticker)
    if not isinstance(stock.dividends, pd.Series):
        if error_out:
            raise ValueError(f"Cannot get info of {ticker}, it probably does not exist")
        else:
            print(f"Cannot get info of {ticker}, it probably does not exist")
            return False
    return True
    

if __name__ == "__main__":
    tickers = ['AAPL', 'MSFT', 'V', 'MA', 'SPGI', 'FICO', 'O', 'VICI', 'LRCX', 
            'CP', 'INTU', 'AMZN', 'ASML', 'TMO', 'NVDA', 'MCO', 'NFLX', 'GOOGL',
            'META', 'TSLA', 'COST']
    
    for ticker in tickers:
        update_company(ticker, 'yearly')

    backup_data()
