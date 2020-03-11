import dataclasses
from datetime import datetime
#from numba import jitclass, float64, int32

# spec = [("close_time", int32), ("open", float64),
#        ("high", float64), ("low", float64), ("close", float64)]


# @jitclass(spec)
@dataclasses.dataclass(frozen=True)
class Ohlc:
    close_time: int
    open: float
    high: float
    low: float
    close: float

    def print_price(self):
        print(self.close_time_str, " open:", self.open, "high:",
              self.high, "low:", self.low, "close:", self.close)

    def close_time_str(self):
        return datetime.fromtimestamp(
            self.close_time).strftime('%Y/%m/%d %H:%M')


if __name__ == '__main__':
    pass
