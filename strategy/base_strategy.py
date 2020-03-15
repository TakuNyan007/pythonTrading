from abc import ABCMeta, abstractmethod
from bitmex import T, O, H, L, C, V, BUY, SELL, TAKER_COST, MARKET_COST

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
                idx == self.term + 1  # TODO: idxがあっているかチェック
                continue
            # TODO: term数だけとれているかチェック
            # len = self.term + 1(過去term期間 + 最新足)
            term_ohlc = ohlc_array[:, (idx - self.term):idx]
            ohlc = term_ohlc[:, -1]

            if self.position != 0:
                stop_loss = self.stop_loss_signal(term_ohlc)
                if stop_loss:
                    pass
                # 利確シグナル、ドテンシグナル
                signal, doten = self.close_signal(term_ohlc)
                if signal:
                    entry_price = self.entry_prices[-1]
                    exit_price = ohlc[C]
                    self.exit_time.append(ohlc[T])
                    self.exit_type.append(CLOSE_EXIT)
                    self.exit_prices.append(exit_price)
                    profit = self.position * (exit_price - entry_price)
                    self.profit = [profit]
                    cost = (entry_price + exit_price) * TAKER_COST
                    self.slippage.append(cost)
                    self.position = 0
                    if doten != NO_ENTRY:
                        self.entry_prices.append(exit_price)
                        self.entry_sides.append(doten)
                        self.position = lot
            else:
                side = self.entry_signal(term_ohlc)
                if side != NO_ENTRY:
                    self.entry_prices.append(ohlc[C])
                    self.entry_sides.append(side)
                    self.position = lot

            idx += 1
            if idx > len(ohlc_array.shape[1]):
                break

    @abstractmethod
    def close_signal(self, term_ohlc):
        if self.position == 0:
            raise EnvironmentError()
        return False, NO_ENTRY  # closeSignal, dotenSignal

    @abstractmethod
    def stop_loss_signal(self, term_ohlc):
        return False

    @abstractmethod
    def entry_signal(self, term_ohlc):
        return NO_ENTRY


if __name__ == '__main__':
    pass
