from abc import ABCMeta, abstractmethod
from bitmex import T, O, H, L, C, V, BUY, SELL, TAKER_COST, MARKET_COST
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

NO_ENTRY = ""
STOP_LOSS = "損切"
CLOSE_EXIT = "利確"


class Strategy(metaclass=ABCMeta):
    def __init__(self, term):
        self.term = term

        self.position = 0
        self.entry_sides = []  # shoule be same length # 買い増しのときどうなるんだ？
        self.entry_prices = []  # shoule be same length
        self.exit_time = []  # shoule be same length
        self.exit_type = []  # shoule be same length
        self.exit_prices = []  # shoule be same length
        self.profit = []  # shoule be same length
        self.slippage = []  # shoule be same length

    def run_bot(self, ohlc_array, lot=1):
        idx = 0
        while True:
            '''
            t = ohlc_array[T]  # close time
            o = ohlc_array[O]
            h = ohlc_array[H]
            l = ohlc_array[L]
            c = ohlc_array[C]
            v = ohlc_array[V]
            '''

            if idx == 0:
                if self.term == 1:
                    raise EnvironmentError("You need to override self.term")
                idx = self.term  # TODO: idxがあっているかチェック
                continue
            # TODO: term数だけとれているかチェック
            # len = self.term + 1(過去term期間 + 最新足)
            term_ohlc = ohlc_array[:, (idx - self.term):idx]
            ohlc = ohlc_array[:, idx]

            if self.position != 0:
                stop_loss = self.stop_loss_signal(ohlc, term_ohlc)
                if stop_loss:
                    self.update_result(ohlc, STOP_LOSS)
                    idx += 1  # continueするのは微妙。
                    continue
                signal, doten = self.close_signal(ohlc, term_ohlc)
                if signal:
                    self.update_result(ohlc, CLOSE_EXIT)
                    if doten != NO_ENTRY:
                        self.entry_prices.append(ohlc[C])
                        self.entry_sides.append(doten)
                        self.position = lot
            else:
                side = self.entry_signal(ohlc, term_ohlc)
                if side != NO_ENTRY:
                    self.entry_prices.append(ohlc[C])
                    self.entry_sides.append(side)
                    self.position = lot

            idx += 1
            if idx >= ohlc_array.shape[1]:
                # ポジションを持ったままの場合、最後のエントリーを除外する
                if self.position > 0:
                    del self.entry_sides[-1]
                    del self.entry_prices[-1]
                break

    def update_result(self, ohlc, exit_type):
        entry_price = self.entry_prices[-1]
        entry_side = self.entry_sides[-1]
        exit_price = ohlc[C]
        self.exit_time.append(datetime.fromtimestamp(
            ohlc[T]).strftime('%Y/%m/%d %H:%M'))
        self.exit_type.append(exit_type)
        self.exit_prices.append(exit_price)

        profit = 0
        if entry_side == BUY:
            profit = self.position * (exit_price - entry_price)
        elif entry_side == SELL:
            profit = self.position * (entry_price - exit_price)
        self.profit.append(profit)
        cost = (entry_price + exit_price) * TAKER_COST
        self.slippage.append(cost)
        self.position = 0

    @abstractmethod
    def close_signal(self, ohlc, term_ohlc):
        if self.position == 0:
            raise EnvironmentError()
        return False, NO_ENTRY  # closeSignal, dotenSignal

    @abstractmethod
    def stop_loss_signal(self, ohlc, term_ohlc):
        return False

    @abstractmethod
    def entry_signal(self, ohlc, term_ohlc):
        return NO_ENTRY

    def result_df(self):
        df = pd.DataFrame({
            "exit_time": self.exit_time,
            "exit_type": self.exit_type,
            "entry_price": self.entry_prices,
            "exit_price": self.exit_prices,
            "entry_side": self.entry_sides,
            "profit": self.profit,  # 各トレードの損益
            "slippage": self.slippage
        })
        df["gross_profit"] = df["profit"].cumsum()  # 総損益
        df["drawdown"] = df["gross_profit"].cummax().subtract(
            df["gross_profit"])  # 最大ドローダウン
        return df

    def plot_gross_plofit(self):
        df = self.result_df()
        x_axis = pd.to_datetime(self.exit_time)
        plt.plot(x_axis, df["gross_profit"])
        plt.xlabel("Date")
        plt.ylabel("Balance")
        plt.xticks(rotation=50)
        plt.show()


if __name__ == '__main__':
    pass
