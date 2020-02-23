import dataclasses
from datetime import datetime


@dataclasses.dataclass(frozen=True)
class Ohlc:
    close_time: int
    open: float
    high: float
    low: float
    close: float

    def print_price(self):
        close_time_str = datetime.fromtimestamp(
            self.close_time).strftime('%Y/%m/%d %H:%M')
        print(close_time_str, "open:", self.open, "high:",
              self.high, "low:", self.low, "close:", self.close)
