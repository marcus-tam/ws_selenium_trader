import datetime as dt
import matplotlib.pyplot as plt
import pandas_datareader as web
from pprint import PrettyPrinter
import yfinance as yf

plt.style.use("dark_background")
pp = PrettyPrinter(indent=4)

ma_1 = 20

start = dt.datetime.now() - dt.timedelta(days=365*2)
end = dt.datetime.now()

data = yf.Ticker('MSFT')
# pp.pprint(data.history(start=start, end=end))
data = data.history(start=start, end=end) 

data[f"SMA"] = data["Close"].rolling(window=ma_1).mean()
data[f"stddev"] = data["Close"].rolling(window=ma_1).std()

data[f'BB_upper'] = data[f"SMA"] + 2 * data[f"stddev"]
data[f'BB_lower'] = data[f"SMA"] - 2 * data[f"stddev"]

# data = data.iloc[ma_2:]

# plt.plot(data['Close'], label = "Share Price", color="lightgray")
# plt.plot(data['BB_upper'], label = f"BB_upper", color="orange")
# plt.plot(data['BB_lower'], label = f"BB_lower", color="purple")


# buy_signals = []
# sell_signals = []
# trigger = 0

# for x in range(len(data)):
#     if data[f"SMA_{ma_1}"].iloc[x] > data[f'SMA_{ma_2}'].iloc[x] and trigger != 1:
#         buy_signals.append(data['Close'].iloc[x])
#         sell_signals.append(float('nan'))
#         trigger = 1
#     elif data[f"SMA_{ma_1}"].iloc[x] < data[f'SMA_{ma_2}'].iloc[x] and trigger != -1:
#         buy_signals.append(float('nan'))
#         sell_signals.append(data['Close'].iloc[x])
#         trigger = -1
#     else:
#         buy_signals.append(float('nan'))
#         sell_signals.append(float('nan'))


# data['Buy Signals'] = buy_signals
# data['Sell Signals'] = sell_signals

# print(data)

# plt.plot(data['Close'], label = "Share Price", alpha=0.5)
# plt.plot(data[f"SMA_{ma_1}"], label = f"SMA_{ma_1}", color="orange", linestyle="--")
# plt.plot(data[f"SMA_{ma_2}"], label = f"SMA_{ma_2}", color="pink", linestyle="--")
# plt.scatter(data.index, data['Buy Signals'], label="Buy Signal", marker="^", color="#00ff00", lw = 3)
# plt.scatter(data.index, data['Sell Signals'], label="Sell Signal", marker="v", color="#ff0000", lw = 3)
plt.legend(loc="upper left")
plt.show()