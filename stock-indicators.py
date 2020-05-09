import pandas as pd


# calculates the average of values for a specififc subinterval from a list of numeric values
# returns generator object (cast to list etc.)
def values_to_avg(values, interval):
    for i in range(1, len(values) + 1):
        if len(values[:i]) < interval:
            yield sum(values[:i]) / len(values[:i])
        else:
            yield sum(values[i - interval:i]) / len(values[i - interval:i])


class StockDf:
    def __init__(self, open_price, high_price, low_price, close_price, volume):
        self.df = pd.DataFrame()
        self.df["open"] = open_price
        self.df["high"] = high_price
        self.df["low"] = low_price
        self.df["close"] = close_price
        self.df["volume"] = volume

    # calculates the average of open, high, low and close
    def set_middle(self):
        self.df["middle"] = (self.df["open"] + self.df["high"] + self.df["low"] + self.df["close"]) / 4

    # calculates moving average for an indicator (close by default)
    # and time interval (14 steps by default)
    def set_ma(self, indicator="close", interval=14):
        self.df["ma_" + indicator + "_" + str(interval)] = list(
            values_to_avg(self.df[indicator], interval)
        )
