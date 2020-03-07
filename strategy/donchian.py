from strategy.models import ohlc
from strategy.base_strategy import Strategy, BUY, SELL, NO_ENTRY

PARAM_INCREASE_RATE = 0.0005
PARAM_REALBODY_RATE = 0.5


class Donchian(Strategy):

    def __init__(self, client, logger, term):
        super().__init__(client, logger)
        self.signal = 0
        self.term = term
        self.last_side = NO_ENTRY

    def entrySignal(self, data, l_ohlc_list):
        highest = max(i.high for i in l_ohlc_list)
        lowest = min(i.low for i in l_ohlc_list)
        if data.high > highest:
            self.last_side = BUY
            return BUY
        if data.low < lowest:
            self.last_side = SELL
            return SELL
        return NO_ENTRY

    def closeSignal(self, data, l_ohlc_list):
        highest = max(i.high for i in l_ohlc_list)
        lowest = min(i.low for i in l_ohlc_list)
        if self.last_side == BUY:
            if data.low < lowest:
                self.last_side = SELL
                return True, True
        if self.last_side == SELL:
            if data.high > highest:
                self.last_side = BUY
                return True, True
        return False, False


if __name__ == '__main__':
    pass
