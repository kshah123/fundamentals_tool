import os
files = os.listdir("./data/")
tickers = [ticker.split(".xlsx")[0] for ticker in files]
print(tickers)
for ticker in tickers:
    if ticker not in tickers_test:
        print("UH OH")