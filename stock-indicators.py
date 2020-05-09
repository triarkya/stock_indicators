import pandas as pd


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

    