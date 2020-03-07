from strategy.models import ohlc
from strategy.base_strategy import Strategy, BUY, SELL, NO_ENTRY

PARAM_INCREASE_RATE = 0.0005
PARAM_REALBODY_RATE = 0.5


class Sanpei(Strategy):
    signal: int

    def __init__(self, client, logger):
        super().__init__(client, logger)
        self.signal = 0

    def check_candle(self, data: ohlc.Ohlc):
        realbody_rate = 0 if data.high - \
            data.low == 0 else abs(data.close - data.open)/(data.high - data.low)
        increase_rate = abs(data.close / data.open - 1)

        if increase_rate < PARAM_INCREASE_RATE:
            return False
        elif realbody_rate < PARAM_REALBODY_RATE:
            return False
        else:
            return True

    def check_ascend(self, data: ohlc.Ohlc, last_data: ohlc.Ohlc):
        if data.open > last_data.open and data.close > last_data.close:
            return 1
        elif data.open < last_data.open and data.close < last_data.close:
            return -1
        else:
            return 0

    def entrySignal(self, data, l_ohlc_list):
        if not self.check_candle(data):
            self.signal = 0
            return NO_ENTRY

        ascend_param = self.check_ascend(data, l_ohlc_list[-1])
        if ascend_param == 0:
            self.signal = 0
            return NO_ENTRY

        self.signal += ascend_param

        if self.signal == 3:
            print("3本連続陽線です。買いシグナル点灯しました。")
            return BUY

        if self.signal == -3:
            print("3本連続陰線です。売りシグナル点灯しました。")
            return SELL

        return ""

    def closeSignal(self, data, l_ohlc_list):
        if not abs(self.signal) == 3:
            raise EnvironmentError

        l_ohlc = l_ohlc_list[-1]
        if self.signal == 3 and (data.close - l_ohlc.close < 0):
            self.signal = 0
            return True, False
        if self.signal == -3 and (data.close - l_ohlc.close > 0):
            self.signal = 0
            return True, False

        return False, False


if __name__ == '__main__':
    pass
