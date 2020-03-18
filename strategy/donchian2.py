from strategy.base_strategy import Strategy, NO_ENTRY
from bitmex import T, O, H, L, C, V, BUY, SELL
from strategy.utils.indicator import atr
import numpy as np


class Donchian(Strategy):

    def __init__(self, term, atr_term):
        super().__init__(term)
        self.atr_term = atr_term

    def close_signal(self, ohlc, term_ohlc):
        if self.position == 0:
            raise EnvironmentError(
                "Method close_signal is called when you have no position.")
        entry_side = self.entry_sides[-1]
        highest = np.max(term_ohlc[H])  # term期間の最大値
        lowest = np.min(term_ohlc[L])  # term期間の最小値
        if entry_side == BUY:
            if ohlc[L] < lowest:
                return True, SELL
        if entry_side == SELL:
            if ohlc[H] > highest:
                return True, BUY
        return False, NO_ENTRY  # closeSignal, dotenSignal

    def stop_loss_signal(self, ohlc, term_ohlc):
        atrr = atr(term_ohlc[-self.atr_term:], term=self.atr_term)[-1]
        entry_side = self.entry_sides[-1]

        if entry_side == BUY and ohlc[C] < (self.entry_prices[-1] - atrr):
            return True
        if entry_side == SELL and ohlc[C] > (self.entry_prices[-1] + atrr):
            return True
        return False

    def entry_signal(self, ohlc, term_ohlc):
        highest = np.max(term_ohlc[H])  # term期間の最大値
        lowest = np.min(term_ohlc[L])  # term期間の最小値
        if ohlc[C] > highest:
            return BUY
        if ohlc[C] < lowest:
            return SELL
        return NO_ENTRY


if __name__ == '__main__':
    pass
