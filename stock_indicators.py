import pandas as pd
import numpy as np


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

    # calculates volume weighted moving average for an indicator (close by default)
    # and time interval (14 steps by default)
    def set_vwma(self, indicator="close", interval=14):
        vwma = []
        pv = []
        for i in range(len(self.df)):
            pv.append(self.df[indicator][i] * self.df["volume"][i])
            if i // interval == 0:
                if sum(self.df["volume"][:i + 1]) == 0:
                    vwma.append(self.df[indicator][i])
                else:
                    vwma.append(sum(pv) / sum(self.df["volume"][:i + 1]))
            else:
                if sum(self.df["volume"][i - interval:i + 1]) == 0:
                    vwma.append(self.df[indicator][i])
                else:
                    vwma.append(sum(pv[i - interval:i + 1]) / sum(self.df["volume"][i - interval:i + 1]))
        self.df["vwma_" + indicator + "_" + str(interval)] = vwma

    # calculates money flow index
    # time interval by default 14 steps
    def set_mfi(self, interval=14):
        high = self.df["high"].to_numpy()
        low = self.df["low"].to_numpy()
        close = self.df["close"].to_numpy()
        volume = self.df["volume"].to_numpy()

        typical_price = list(
            (close + high + low) / 3
        )

        raw_money_flow = [typical_price[0] * volume[0]]
        for j in range(1, len(close)):
            raw_money_flow.append(
                typical_price[j] * volume[j] if typical_price[j - 1] < typical_price[j] else typical_price[j] * volume[
                    j] * -1
            )

        money_flow_index = (interval - 1) * [0]
        for k in range(interval, len(close) + 1):
            pos_sum = sum(
                [pos_flow for pos_flow in raw_money_flow[k - interval:k] if pos_flow >= 0]
            )
            neg_sum = sum(
                [neg_flow for neg_flow in raw_money_flow[k - interval:k] if neg_flow < 0]
            ) * -1

            if pos_sum + neg_sum > 0:
                money_flow_index.append(100 * pos_sum / (pos_sum + neg_sum))
            else:
                money_flow_index.append(typical_price[k])

        self.df["mfi_" + str(interval)] = money_flow_index

    # calculates relative vigor index (+ relative vigor index signal)
    def set_rvgi(self, interval=10):
        close_open = list(self.df['close'] - self.df['open'])
        high_low = list(self.df['high'] - self.df['low'])
        numerator = np.array([])
        denominator = np.array([])
        for i in range(len(close_open)):
            if i >= 3:
                numerator = np.append(
                    numerator,
                    (close_open[i] + 2 * close_open[i - 1] + 2 * close_open[i - 2] + close_open[
                        i - 3]) / 6
                )
                denominator = np.append(
                    denominator,
                    (high_low[i] + 2 * high_low[i - 1] + 2 * high_low[i - 2] + high_low[i - 3]) / 6
                )
            elif i == 2:
                numerator = np.append(
                    numerator,
                    (close_open[i] + 2 * close_open[i - 1] + 2 * close_open[i - 2]) / 5
                )
                denominator = np.append(
                    denominator,
                    (high_low[i] + 2 * high_low[i - 1] + 2 * high_low[i - 2]) / 5
                )
            elif i == 1:
                numerator = np.append(
                    numerator,
                    (close_open[i] + 2 * close_open[i - 1]) / 3
                )
                denominator = np.append(
                    denominator,
                    (high_low[i] + 2 * high_low[i - 1]) / 3
                )
            elif i == 0:
                numerator = np.append(
                    numerator,
                    close_open[i]
                )
                denominator = np.append(
                    denominator,
                    high_low[i]
                )
        rvi = list(values_to_avg(numerator / denominator, interval))
        rvi_signal = []

        for i in range(len(rvi)):
            if i >= 3:
                rvi_signal.append(
                    (rvi[i] + 2 * rvi[i - 1] + 2 * rvi[i - 2] + rvi[i - 3]) / 6
                )
            elif i == 2:
                rvi_signal.append(
                    (rvi[i] + 2 * rvi[i - 1] + 2 * rvi[i - 2]) / 5
                )
            elif i == 1:
                rvi_signal.append(
                    (rvi[i] + 2 * rvi[i - 1]) / 3
                )
            elif i == 0:
                rvi_signal.append(
                    rvi[i]
                )
        self.df['rvgi'] = rvi
        self.df['rvgi_signal'] = rvi_signal
