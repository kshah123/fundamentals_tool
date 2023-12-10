import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from data import update_company

def cagr_calc(data, yrs:int, freq:str):
    if freq == "quarterly":
        return (data[0]/data[yrs*4])**(1/yrs)-1
    else:
        return (data[0]/data[yrs])**(1/yrs)-1


ticker = input("Enter ticker: ")
freq = "yearly"
stock = yf.Ticker(ticker)
path = './data/'+ ticker + "_" + freq +".xlsx"

# Refresh financial info
update_company(ticker, freq)

# Get balance sheet
balance_sheet = pd.read_excel(path, sheet_name="Balance Sheet", index_col=0)
# balance_sheet.set_index("Date")

# Get balance sheet
income_statement = pd.read_excel(path, sheet_name="Income Statement", index_col=0)
# balance_sheet.set_index("Date")

# Get balance sheet
cash_flow = pd.read_excel(path, sheet_name="Cash Flow", index_col=0)
# balance_sheet.set_index("Date")

# if freq == "yearly":
#     avg_keys = ['TotalDebt', 'TaxRateForCalcs', 'InvestedCapital', 'TotalAssets', 'CurrentLiabilities', 'OrdinarySharesNumber']
#     sum_keys = ['OperatingCashFlow', 'EBIT', 'NetIncome', 'FreeCashFlow', 'BasicEPS', 'DilutedEPS', 'EBITDA', 'OperatingRevenue', 'OperatingIncome']
    
#     balance_sheet_yavg = pd.DataFrame()
#     balance_sheet_ysum = pd.DataFrame()
#     cash_flow_yavg = pd.DataFrame()
#     cash_flow_ysum = pd.DataFrame()
#     income_statement_yavg = pd.DataFrame()
#     income_statement_ysum = pd.DataFrame()

#     for key in avg_keys:
#         if key in balance_sheet.keys():
#             balance_sheet_yavg[key] = balance_sheet[key]
#         elif key in cash_flow.keys():
#             cash_flow_yavg[key] = cash_flow[key]
#         elif key in income_statement.keys():
#             income_statement_yavg[key] = income_statement[key]

#     balance_sheet_yavg = balance_sheet_yavg.groupby(pd.PeriodIndex(balance_sheet_yavg.index, freq='Y'), axis=0).mean()
#     cash_flow_yavg = cash_flow_yavg.groupby(pd.PeriodIndex(cash_flow_yavg.index, freq='Y'), axis=0).mean()
#     income_statement_yavg = income_statement_yavg.groupby(pd.PeriodIndex(income_statement_yavg.index, freq='Y'), axis=0).mean()


#     for key in sum_keys:
#         if key in balance_sheet.keys():
#             balance_sheet_ysum[key] = balance_sheet[key]
#         elif key in cash_flow.keys():
#             cash_flow_ysum[key] = cash_flow[key]
#         elif key in income_statement.keys():
#             income_statement_ysum[key] = income_statement[key]
    
#     balance_sheet_ysum = balance_sheet_ysum.groupby(pd.PeriodIndex(balance_sheet_ysum.index, freq='Y'), axis=0).sum()
#     cash_flow_ysum = cash_flow_ysum.groupby(pd.PeriodIndex(cash_flow_ysum.index, freq='Y'), axis=0).sum()
#     income_statement_ysum = income_statement_ysum.groupby(pd.PeriodIndex(income_statement_ysum.index, freq='Y'), axis=0).sum()
    

# intermediate metrics for calcs
operating_cashflow = cash_flow['OperatingCashFlow']
total_debt = balance_sheet['TotalDebt']

ebit = income_statement['EBIT']
tax_rate = income_statement['TaxRateForCalcs']
nopat = (ebit - (1-tax_rate))

invested_capital = balance_sheet['InvestedCapital']

total_assets = balance_sheet['TotalAssets']
current_liabilities = balance_sheet['CurrentLiabilities']

net_income = income_statement['NetIncome']


# Desired metrics:

# Shares Outstanding
# Technically ordinary shares doesn't include preferred shares
shares_outstanding = balance_sheet['OrdinarySharesNumber']

# Cash/debt ratio
CD_ratio = operating_cashflow/total_debt

# ROIC + ROCE
roic = nopat/invested_capital
roce = nopat/(total_assets-current_liabilities)

# FCF + FCF/Share
free_cash_flow = cash_flow['FreeCashFlow']
fcfps = free_cash_flow/shares_outstanding

# EPS + EBITDA
eps_basic = income_statement['BasicEPS']
eps_diluted = income_statement['DilutedEPS']
ebitda = income_statement['EBITDA']

# Operating Revenue
operating_revenue = income_statement['OperatingRevenue']

# Operating Margins
operating_income = income_statement['OperatingIncome']
operating_margins = operating_income/operating_revenue

# Dividends
dividends = stock.dividends

# Net Profit Margin
net_profit_margin = net_income/operating_revenue

titles =["Shares Outstanding", "Cash-Debt Ratio", "ROIC", "ROCE", "FCF", 
         "FCF/Share", "EPS Basic", "EPS Diluted", "EBITDA", "Operating Revenue", 
         "Operating Income", "Operating Margin", "Dividends", "Net Profit Margin"]

vals = [shares_outstanding, CD_ratio, roic, roce, free_cash_flow, fcfps,
        eps_basic, eps_diluted, ebitda, operating_revenue, operating_income, 
        operating_margins, dividends, net_profit_margin]

if freq == "quarterly":
    n_years = (len(balance_sheet)-1)/4
else:
    n_years = len(balance_sheet)-1

cagr_years = [1,3,5,10]
cagr_dict = {}

current_yrs = 0
for cagr_year in cagr_years:
    if cagr_year <= n_years:
        cagr_dict[cagr_year] = {}
        for title, val in zip(titles, vals):
            cagr_dict[cagr_year][title] = cagr_calc(val, cagr_year, freq) 
    else:
        break

# cagr1 = dict.fromkeys(titles)
# cagr3 = dict.fromkeys(titles)

# cagr1["Shares Outstanding"] = cagr_calc(shares_outstanding, 1)
# cagr1["Cash-Debt Ratio"] = cagr_calc(CD_ratio, 1)
# cagr1["ROCE"] = cagr_calc(roce, 1)
# cagr1["ROIC"] = cagr_calc(roic, 1)
# cagr1["FCF"] = cagr_calc(free_cash_flow, 1)
# cagr1["FCF/Share"] = cagr_calc(fcfps, 1)
# cagr1["EPS Basic"] = cagr_calc(eps_basic, 1)
# cagr1["EPS Diluted"] = cagr_calc(eps_diluted, 1)
# cagr1["EBITDA"] = cagr_calc(ebitda, 1)
# cagr1["Operating Revenue"] = cagr_calc(operating_revenue, 1)
# cagr1["Operating Income"] = cagr_calc(operating_income, 1)
# cagr1["Operating Margin"] = cagr_calc(operating_margins, 1)
# cagr1["Dividends"] = cagr_calc(dividends, 1)
# cagr1["Net Profit Margin"] = cagr_calc(net_profit_margin, 1)

# cagr3["Shares Outstanding"] = cagr_calc(shares_outstanding, 3)
# cagr3["Cash-Debt Ratio"] = cagr_calc(CD_ratio, 3)
# cagr3["ROCE"] = cagr_calc(roce, 3)
# cagr3["ROIC"] = cagr_calc(roic, 3)
# cagr3["FCF"] = cagr_calc(free_cash_flow, 3)
# cagr3["FCF/Share"] = cagr_calc(fcfps, 3)
# cagr3["EPS Basic"] = cagr_calc(eps_basic, 3)
# cagr3["EPS Diluted"] = cagr_calc(eps_diluted, 3)
# cagr3["EBITDA"] = cagr_calc(ebitda, 3)
# cagr3["Operating Revenue"] = cagr_calc(operating_revenue, 3)
# cagr3["Operating Income"] = cagr_calc(operating_income, 3)
# cagr3["Operating Margin"] = cagr_calc(operating_margins, 3)
# cagr3["Dividends"] = cagr_calc(dividends, 3)
# cagr3["Net Profit Margin"] = cagr_calc(net_profit_margin, 3)

fig = make_subplots(rows=5, cols=3,
                    subplot_titles=titles)

fig.add_trace(go.Bar(x=np.array(shares_outstanding.keys()), y = np.array(shares_outstanding)), row=1, col=1)
# PLACE HOLDER FOR SPY PLOTS
# fig.add_trace(go.Bar(x=np.array(shares_outstanding.keys()), y = .9*np.array(shares_outstanding)), row=1, col=1)
fig.add_trace(go.Bar(x=np.array(CD_ratio.keys()), y = np.array(CD_ratio)), row=1, col=2)
fig.add_trace(go.Bar(x=np.array(roic.keys()), y = np.array(roic)), row=1, col=3)
fig.add_trace(go.Bar(x=np.array(roce.keys()), y = np.array(roce)), row=2, col=1)
fig.add_trace(go.Bar(x=np.array(free_cash_flow.keys()), y = np.array(free_cash_flow)), row=2, col=2)
fig.add_trace(go.Bar(x=np.array(fcfps.keys()), y = np.array(fcfps)), row=2, col=3)
fig.add_trace(go.Bar(x=np.array(eps_basic.keys()), y = np.array(eps_basic)), row=3, col=1)
fig.add_trace(go.Bar(x=np.array(eps_diluted.keys()), y = np.array(eps_diluted)), row=3, col=2)
fig.add_trace(go.Bar(x=np.array(ebitda.keys()), y = np.array(ebitda)), row=3, col=3)
fig.add_trace(go.Bar(x=np.array(operating_revenue.keys()), y = np.array(operating_revenue)), row=4, col=1)
fig.add_trace(go.Bar(x=np.array(operating_income.keys()), y = np.array(operating_income)), row=4, col=2)
fig.add_trace(go.Bar(x=np.array(operating_margins.keys()), y = np.array(operating_margins)), row=4, col=3)
fig.add_trace(go.Bar(x=np.array(dividends.keys()), y = np.array(dividends)), row=5, col=1)
fig.add_trace(go.Bar(x=np.array(net_profit_margin.keys()), y = np.array(net_profit_margin)), row=5, col=2)

for cagr_year in cagr_dict.keys():
    if cagr_year == 1:
        fig['layout']['xaxis']['title'] = str(cagr_year)+"y CAGR: "+str(round(cagr_dict[cagr_year]["Shares Outstanding"]*100,2)) + "%"
        fig['layout']['xaxis2']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Cash-Debt Ratio"]*100,2)) + "%"
        fig['layout']['xaxis3']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["ROIC"]*100,2)) + "%"
        fig['layout']['xaxis4']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["ROCE"]*100,2)) + "%"
        fig['layout']['xaxis5']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["FCF"]*100,2)) + "%"
        fig['layout']['xaxis6']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["FCF/Share"]*100,2)) + "%"
        fig['layout']['xaxis7']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["EPS Basic"]*100,2)) + "%"
        fig['layout']['xaxis8']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["EPS Diluted"]*100,2)) + "%"
        fig['layout']['xaxis9']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["EBITDA"]*100,2))  + "%"
        fig['layout']['xaxis10']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Operating Revenue"]*100,2)) + "%"
        fig['layout']['xaxis11']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Operating Income"]*100,2)) + "%"
        fig['layout']['xaxis12']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Operating Margin"]*100,2)) + "%"
        fig['layout']['xaxis13']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Dividends"]*100,2)) + "%"
        fig['layout']['xaxis14']['title'] = str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Net Profit Margin"]*100,2)) + "%"
    else:
        fig['layout']['xaxis']['title'] = fig['layout']['xaxis']['title']['text'] + " | " + str(cagr_year)+"y CAGR: "+str(round(cagr_dict[cagr_year]["Shares Outstanding"]*100,2)) + "%"
        fig['layout']['xaxis2']['title'] = fig['layout']['xaxis2']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Cash-Debt Ratio"]*100,2)) + "%"
        fig['layout']['xaxis3']['title'] = fig['layout']['xaxis3']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["ROIC"]*100,2)) + "%"
        fig['layout']['xaxis4']['title'] = fig['layout']['xaxis4']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["ROCE"]*100,2)) + "%"
        fig['layout']['xaxis5']['title'] = fig['layout']['xaxis5']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["FCF"]*100,2)) + "%"
        fig['layout']['xaxis6']['title'] = fig['layout']['xaxis6']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["FCF/Share"]*100,2)) + "%"
        fig['layout']['xaxis7']['title'] = fig['layout']['xaxis7']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["EPS Basic"]*100,2)) + "%"
        fig['layout']['xaxis8']['title'] = fig['layout']['xaxis8']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["EPS Diluted"]*100,2)) + "%"
        fig['layout']['xaxis9']['title'] = fig['layout']['xaxis9']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["EBITDA"]*100,2))  + "%"
        fig['layout']['xaxis10']['title'] = fig['layout']['xaxis10']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Operating Revenue"]*100,2)) + "%"
        fig['layout']['xaxis11']['title'] = fig['layout']['xaxis11']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Operating Income"]*100,2)) + "%"
        fig['layout']['xaxis12']['title'] = fig['layout']['xaxis12']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Operating Margin"]*100,2)) + "%"
        fig['layout']['xaxis13']['title'] = fig['layout']['xaxis13']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Dividends"]*100,2)) + "%"
        fig['layout']['xaxis14']['title'] = fig['layout']['xaxis14']['title']['text'] + " | " + str(cagr_year)+"y CAGR: " + str(round(cagr_dict[cagr_year]["Net Profit Margin"]*100,2)) + "%"


fig.update_layout(height=2000, showlegend=False, title_text = ticker + " Financials")#, barmode = "group")
fig.show()

