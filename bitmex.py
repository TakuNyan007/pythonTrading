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


class Bitmex:
    def __init__(self, apiKey, secret):
        self.bitmex = ccxt.bitmex()
        self.bitmex.apiKey = apiKey
        self.bitmex.secret = secret

    def get_price(self, sec):
        res = requests.get(
            base_url + '/ohlc', params={"periods": sec})
        res = res.json()
        datalist = res["result"][str(sec)]  # 確定している最新の足

        ohlclist = []
        for data in datalist:
            ohlclist.append(
                ohlc.Ohlc(data[0], data[1], data[2], data[3], data[4]))
        return ohlclist

    def get_last_price(self, sec):
        res = requests.get(
            base_url + '/ohlc', params={"periods": sec})
        res = res.json()
        data = res["result"][str(sec)]  # 確定している最新の足
        return ohlc.Ohlc(data[0], data[1], data[2], data[3], data[4])

    def create_limit_order(self, side, price, amount):
        order = self.bitmex.create_order(
            symbol=BTC_USD,
            type=LIMIT,
            side=side,
            price=price,
            amount=amount
        )
        return order

    def fetch_open_orders(self):
        orders = self.bitmex.fetch_open_orders(symbol='BTC/USD')
        return orders

    def cancel_all_orders(self):
        orders = self.fetch_open_orders()
        for o in orders:
            r = self.bitmex.cancel_order(symbol=BTC_USD, id=o["id"])
            pprint(r)

    def closePosition(self):
        pass

    def create_order(self, side):
        pass
