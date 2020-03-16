from strategy.models import ohlc
from strategy.base_strategy import Strategy, BUY, SELL, NO_ENTRY
from strategy.utils.indicator import atr
PARAM_INCREASE_RATE = 0.0005
PARAM_REALBODY_RATE = 0.5


class Donchian(Strategy):

    def __init__(self, client, logger, term, atr_term):
        super().__init__(client, logger)
        self.signal = 0
        self.term = term
        self.atr_term = atr_term

    def entrySignal(self, data, l_ohlc_list):
        last_term_list = l_ohlc_list[-self.term:]
        highest = max(i.high for i in last_term_list)
        lowest = min(i.low for i in last_term_list)
        if data.close > highest:
            return BUY
        if data.close < lowest:
            return SELL
        return NO_ENTRY

    def closeSignal(self, data, l_ohlc_list):
        last_term_list = l_ohlc_list[-self.term:]
        #atr_range = atr(ohlc_list=l_ohlc_list, term=self.atr_term)
        highest = max(i.high for i in last_term_list)
        lowest = min(i.low for i in last_term_list)
        last_side = self.entry_sides[-1]
        if last_side == BUY:
            if data.low < lowest:
                return True, True
        if last_side == SELL:
            if data.high > highest:
                return True, True
        return False, False

    def is_perfect_order(self):
        pass


if __name__ == '__main__':
    pass
