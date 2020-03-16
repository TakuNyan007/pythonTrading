import pandas as pd
import numpy as np
from strategy.models.ohlc import Ohlc
from typing import List
from numba import jit
from bitmex import T, O, H, L, C, V, BUY, SELL

import time

# 時間計測用デコレータ


def calc_time(func):
    def wrapper(*args, **kwargs):
        t_start = time.time()
        result = func(*args, **kwargs)
        t_end = time.time()
        print(f'{func}: {t_end - t_start}[s]')
        return result
    return wrapper


def sma(close_list, term=25):
    nan_array = np.empty(term - 1) * np.nan
    sma_array = np.convolve(close_list, np.ones(term)/term, mode='valid')
    return np.hstack((nan_array, sma_array))


def sma_pd(close_list, term=25):
    return pd.Series(close_list).rolling(term).mean()


def ema(close_list=[], term=5):
    close = close_list
    # np.ndarrayはlistに変換する
    if isinstance(close_list, np.ndarray):
        close = close_list.tolist()
    # https://turtlechan.hatenablog.com/entry/2019/09/07/215105
    '''numpyで指数平滑移動平均の計算'''
    sma0 = sum(close[0: term]) / term  # y0 = SMA[0]
    dataArr = np.array([sma0] + close[term:])

    alpha = 2 / (term + 1.)
    wtArr = (1 - alpha)**np.arange(len(dataArr))
    xArr = (dataArr[1:] * alpha * wtArr[-2::-1]).cumsum() / wtArr[-2::-1]
    emaArr = dataArr[0] * wtArr + np.hstack((0, xArr))
    return np.hstack((np.empty(term - 1) * np.nan, emaArr))


def ema_pd(closeList=[], term=5):
    '''指数平滑移動平均の計算'''
    return pd.Series(closeList).ewm(span=term).mean()


# @jit(nopython=True)
def atr(ohlc_list, term=20):
    h = ohlc_list[H][-(term + 1):]
    l = ohlc_list[L][-(term + 1):]
    c = ohlc_list[C][-(term + 1):]
    # TR = MAX(当日の高値 - 前日の終値, 前日の終値 - 当日の安値, 当日の高値 - 当日の安値)
    tr_list = [
        max(h[i]-c[i-1], c[i-1] - l[i], h[i]-l[i]) for i in range(1, len(h))
    ]
    # ATR = TRのEMA
    return ema(tr_list, term)
