import ccxt
from pprint import pprint  # きれいにprintしてくれるやつ
from datetime import datetime
import requests
import calendar
import time
from strategy.models import ohlc

base_url = 'https://api.cryptowat.ch/markets/bitmex/btcusd-perpetual-futures'
BTC_USD = "BTC/USD"
LIMIT = "limit"
MARKET = "market"
BUY = "buy"
SELL = "sell"


# @with_error_handleデコレータをつけると例外処理付きで実行できます
# デコレータとは？
# https://qiita.com/mtb_beta/items/d257519b018b8cd0cc2e
def with_error_handle(func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                print("request error:", e)
                print("try again after 5 seconds.")
                time.sleep(5)
            except ccxt.BaseError as e:
                print("ccxt error: ", e)
                print("try again after 5 seconds.")
                time.sleep(5)
    return wrapper


class Bitmex:
    def __init__(self, apiKey, secret):
        self.bitmex = ccxt.bitmex()
        self.bitmex.apiKey = apiKey
        self.bitmex.secret = secret

    @with_error_handle
    def get_price(self, periods=60, before=0, after=0):
        params = {"periods": periods}
        if before != 0:
            params["before"] = before
        if after != 0:
            params["after"] = after

        res = requests.get(
            base_url + '/ohlc', params=params)
        res = res.json()
        datalist = res["result"][str(periods)]

        ohlclist = []
        if datalist == None:
            return ohlclist

        for data in datalist:
            ohlclist.append(
                ohlc.Ohlc(data[0], data[1], data[2], data[3], data[4]))
        return ohlclist

    @with_error_handle
    def get_price_by_idx(self, sec, idx=-2):
        res = requests.get(
            base_url + '/ohlc', params={"periods": sec})
        res = res.json()
        data = res["result"][str(sec)][idx]
        return ohlc.Ohlc(data[0], data[1], data[2], data[3], data[4])

    @with_error_handle
    def create_limit_order(self, side, price, amount):
        order = self.bitmex.create_order(
            symbol=BTC_USD,
            type=LIMIT,
            side=side,
            price=price,
            amount=amount
        )
        return order

    @with_error_handle
    def fetch_open_orders(self):
        orders = self.bitmex.fetch_open_orders(symbol='BTC/USD')
        return orders

    @with_error_handle
    def cancel_all_orders(self):
        orders = self.fetch_open_orders()
        for o in orders:
            r = self.bitmex.cancel_order(symbol=BTC_USD, id=o["id"])
            pprint(r)

    @with_error_handle
    def get_position(self):
        positions = self.bitmex.private_get_position()
        for p in positions:
            if p["symbol"] == "XBTUSD":
                return p["currentQty"]
        return None

    @with_error_handle
    def close_position(self, qty):
        side = BUY if qty < 0 else SELL
        return self.create_market_order(side, abs(qty))

    @with_error_handle
    def create_market_order(self, side, amount):
        order = self.bitmex.create_order(
            symbol=BTC_USD,
            type=MARKET,
            side=side,
            amount=amount
        )
        return order
