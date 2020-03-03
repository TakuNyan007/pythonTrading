from strategy.models import ohlc

PARAM_INCREASE_RATE = 0.0005
PARAM_REALBODY_RATE = 0.5


class Sanpei:
    signal: int

    def __init__(self):
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

    def entrySignal(self, data, last_data):
        if not self.check_candle(data):
            self.signal = 0
            return ""

        ascend_param = self.check_ascend(data, last_data)
        if ascend_param == 0:
            self.signal = 0
            return ""

        self.signal += ascend_param

        if self.signal == 3:
            print("3本連続陽線です。買いシグナル点灯しました。")
            return "buy"

        if self.signal == -3:
            print("3本連続陰線です。売りシグナル点灯しました。")
            return "sell"

        return ""

    def closeSignal(self, data, last_data):
        if not abs(self.signal) == 3:
            raise EnvironmentError

        if self.signal == 3 and (data.close - last_data.close < 0):
            self.signal = 0
            return True
        if self.signal == -3 and (data.close - last_data.close > 0):
            self.signal = 0
            return True

        return False
