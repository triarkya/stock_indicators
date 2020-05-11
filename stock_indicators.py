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

    # calculates average true range
    # time interval by default 14 steps
    def set_atr(self, interval=14):
        high = self.df["high"].tolist()
        low = self.df["low"].tolist()
        close = self.df["close"].tolist()
        true_range = [0.0]
        for i in range(1, len(self.df)):
            true_range.append(max([high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1])]))
        self.df["tr_" + str(interval)] = true_range
        self.df["atr_" + str(interval)] = list(values_to_avg(true_range, interval))

    # calculates the percentage of average true range compared to close price
    # time interval by default 14 steps
    def set_atr_perc(self, interval=14):
        if "atr_" + str(interval) not in self.df.columns:
            self.set_atr(interval)
        self.df["%atr_" + str(interval)] = self.df["atr_" + str(interval)] / self.df["close"]

    # calculates moving average for an indicator (close by default)
    # and time interval (14 steps by default)
    def set_ma(self, indicator="close", interval=14):
        self.df["ma_" + indicator + "_" + str(interval)] = list(
            values_to_avg(self.df[indicator], interval)
        )

    # calculates exponential moving average for an indicator (close by default)
    # and time interval (10 steps by default)
    def calc_ema(self, indicator="close", interval=10):
        ema = [self.df[indicator][0]]
        multiplier = 2 / (interval + 1)
        for i in range(1, len(self.df)):
            ema.append(self.df[indicator][i] * multiplier + ema[i-1] * (1 - multiplier))
        return ema

    # save calculated ema in dataframe
    def set_ema(self, indicator="close", interval=10):
        self.df["ema_" + indicator + "_" + str(interval)] = self.calc_ema(indicator, interval)

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

    # calculates moving average convergence divergence
    # by default using ema_close_12 and ema_close_26
    def set_macd(self):
        macd = np.array(self.calc_ema("close", 12)) - np.array(self.calc_ema("close", 26))
        self.df["macd"] = macd
        macd_signal = self.calc_ema("macd", 9)
        self.df["macds"] = macd_signal
        self.df["macdh"] = self.df["macd"] - self.df["macds"]

    # calculates average directional index
    # time interval by default 14 steps
    def set_adx(self, interval=14):
        if "atr_" + str(interval) not in self.df.columns:
            self.set_atr(interval)
        atr = self.df["atr_" + str(interval)].tolist()
        pdm = [0.0]
        ndm = [0.0]
        pdm_smooth = [0.0]
        ndm_smooth = [0.0]
        pdi = [0.0]
        ndi = [0.0]
        dx = [0.0]
        adx = [0.0]
        multiplier = 2 / (interval + 1)
        for i in range(1, len(self.df)):
            move_high = self.df["high"][i] - self.df["high"][i-1]
            move_low = self.df["low"][i-1] - self.df["low"][i]
            pdm.append(move_high if 0 < move_high > move_low else 0)
            ndm.append(move_low if 0 < move_low > move_high else 0)
            pdm_smooth.append(pdm[i] * multiplier + pdm_smooth[i - 1] * (1 - multiplier))
            ndm_smooth.append(ndm[i] * multiplier + ndm_smooth[i - 1] * (1 - multiplier))
            pdi.append(100 * pdm_smooth[i] / atr[i])
            ndi.append(100 * ndm_smooth[i] / atr[i])
            dx.append(100 * abs(pdi[i] - ndi[i]) / abs(pdi[i] + ndi[i]))
            adx.append(dx[i] * multiplier + adx[i - 1] * (1 - multiplier))
        self.df["adx_" + str(interval)] = adx
        self.df["pdi_" + str(interval)] = pdi
        self.df["ndi_" + str(interval)] = ndi

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
    # time interval by default 10 steps
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
        self.df['rvgi_' + str(interval)] = rvi
        self.df['rvgi_signal_' + str(interval)] = rvi_signal

    def set_supertrend(self, factor=2, interval=10):
        if "atr_" + str(interval) not in self.df.columns:
            self.set_atr(interval)
        high = self.df["high"].tolist()
        low = self.df["low"].tolist()
        close = self.df["close"].tolist()
        atr = self.df["atr_" + str(interval)].tolist()

        basic_upperband = ((np.array(high) + np.array(low)) / factor) + factor * np.array(atr)
        basic_lowerband = ((np.array(high) + np.array(low)) / factor) - factor * np.array(atr)

        final_upperband = [0.0]
        final_lowerband = [basic_lowerband[0]]
        for i in range(1, len(basic_upperband)):
            if basic_upperband[i] < final_upperband[i - 1] or close[i - 1] > final_upperband[i - 1]:
                final_upperband.append(basic_upperband[i])
            else:
                final_upperband.append(final_upperband[i - 1])
            if basic_lowerband[i] > final_lowerband[i - 1] or close[i - 1] < final_lowerband[i - 1]:
                final_lowerband.append(basic_lowerband[i])
            else:
                final_lowerband.append(final_lowerband[i - 1])

        supertrend = [final_upperband[0] if close[0] < final_upperband[0] else final_lowerband[0]]
        for j in range(1, len(close)):
            try:
                if supertrend[j - 1] == final_upperband[j - 1]:
                    if close[j] <= final_upperband[j]:
                        supertrend.append(final_upperband[j])
                    elif close[j] > final_upperband[j]:
                        supertrend.append(final_lowerband[j])
                elif supertrend[j - 1] == final_lowerband[j - 1]:
                    if close[j] >= final_lowerband[j]:
                        supertrend.append(final_lowerband[j])
                    elif close[j] < final_lowerband[j]:
                        supertrend.append(final_upperband[j])
            except IndexError:
                print("IndexError " + str(j))
        self.df['supertrend'] = supertrend
