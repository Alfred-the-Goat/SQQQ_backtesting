import yfinance as yf
import numpy as np
import pandas as pd

# Download SQQQ data for the past 10 years
sqqq = yf.download('SQQQ', period='10y')

# Calculate returns for a short position (-1 times the returns of SQQQ)
sqqq['Short Returns'] = -sqqq['Close'].pct_change()

# Calculate cumulative returns for the short position
sqqq['Cumulative Short'] = (1 + sqqq['Short Returns']).cumprod()
# print(sqqq.head())
# print(sqqq.loc[sqqq.index[5], 'Close'])
print(sqqq.info())

# Calculate drawdowns
sqqq['Cumulative Max'] = sqqq['Cumulative Short'].cummax()
sqqq['Drawdown'] = (sqqq['Cumulative Short'] / sqqq['Cumulative Max']) - 1

# Find maximum drawdown and corresponding dates
max_drawdown = sqqq['Drawdown'].min()
end_date = sqqq['Drawdown'].idxmin()
start_date = sqqq['Cumulative Short'].loc[:end_date].idxmax()

print(f"Maximum Drawdown for Short SQQQ: {max_drawdown:.2%}")
print(f"Start Date of Max Drawdown: {start_date}")
print(f"End Date of Max Drawdown: {end_date}")

# Calculate worst-case drawdown for each possible entry
worst_drawdowns = []
sqqq = sqqq.dropna()

for i in range(len(sqqq) - 1):
    entry_price = sqqq['Close'].iloc[i].item()
    max_price_after_entry = sqqq['Close'].iloc[i+1:].max().item()
    drawdown = (entry_price - max_price_after_entry) / entry_price
    worst_drawdowns.append((sqqq.index[i], drawdown))

if worst_drawdowns:
    worst_entry_date, worst_case_drawdown = min(worst_drawdowns, key=lambda x: x[1])
    print(f"Worst-Case Entry Date: {worst_entry_date}")
    print(f"Worst-Case Drawdown: {worst_case_drawdown:.2%}")
else:
    print("No valid worst-case drawdown calculated.")

# Simulate different rebalancing strategies
def simulate_rebalance(freq):
    data = sqqq.copy()
    data['Rebalanced Short'] = 1.0
    if freq == 1:
        cum_return = (1 + data['Short Returns']).cumprod()
        return cum_return
    else:
        for i in range(1, len(data)-freq, freq):
            data.loc[data.index[i + freq], 'Short Returns'] = -(data.loc[data.index[i+freq], 'Close'] - data.loc[data.index[i], 'Close'])/data.loc[data.index[i], 'Close']
        cum_return = (1 + data['Short Returns']).cumprod()
        return cum_return
    # print(cum_return)

    # for i in range(1, len(data)):
    #     if i % freq == 0:
    #         # Rebalance by taking profits and resetting the short position
    #         data.at[data.index[i], 'Rebalanced Short'] = data['Rebalanced Short'].iloc[i-1] * (1 + data['Short Returns'].iloc[i])
    #     else:
    #         # No rebalancing, just track the returns
    #         data.at[data.index[i], 'Rebalanced Short'] = data['Rebalanced Short'].iloc[i-1] * (1 + data['Short Returns'].iloc[i])

    # final_return = data['Rebalanced Short'].iloc[-1] - 1
    # return final_return

frequencies = [1, 2, 5, 20, 60, 252]  # Daily, DTPR, Weekly, Monthly, Quarterly, Yearly
results = {freq: simulate_rebalance(freq) for freq in frequencies}

for freq, ret in results.items():
    # print(type(ret))
    ret = float(ret[-1])
    print(f"Final Return with {freq}-day Rebalancing: {ret:.2%}")
