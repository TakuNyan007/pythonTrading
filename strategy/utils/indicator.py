import pandas as pd
import numpy as np
from strategy.models.ohlc import Ohlc
from typing import List
#from numba import jit


def sma(closeList=[], term=5):
    '''単純移動平均の計算'''
    return list(pd.Series(closeList).rolling(term).mean())


def ema(closeList=[], term=5):
    '''指数平滑移動平均の計算'''
    return list(pd.Series(closeList).ewm(span=term).mean())


# @jit(nopython=True)
def atr(ohlc_list: List[Ohlc] = [], term=20):
    last = ohlc_list[-(term + 1):]
    tr_list = []
    for i, data in enumerate(last):
        if i == 0:
            continue
        hc = data.high - last[i-1].close  # 当日の高値 - 前日の終値
        cl = last[i-1].close - data.low  # 前日の終値 - 当日の安値
        hl = data.high - data.low  # 当日の高値 - 当日の安値
        tr_list.append(max(hc, cl, hl))
    return round(ema(tr_list, term)[-1], 1)
