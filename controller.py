import bitmex
import configparser
from strategy import sanpei
from strategy.models import status
import time

# config.iniファイルからapiKeyとapiSecretを取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")

client = bitmex.Bitmex(apiKey, apiSecret)


def runBot(strategy):
    s = status.Status()
    l_ohlc = None
    while True:
        if s.order.exist:
            # TODO: orderが約定したかチェック
            # TODO: orderが約定していなかった場合キャンセル
            pass

        ohlc = client.get_last_price(60)
        if l_ohlc == None:
            l_ohlc = ohlc
            continue
        if ohlc.close_time != l_ohlc.close_time:
            ohlc.print_price()
            if s.position.exist:
                s.position.exist = strategy.closeSignal(ohlc, l_ohlc)
            else:
                side = strategy.entrySignal(ohlc, l_ohlc)
                client.create_order(side)

            l_ohlc = ohlc

        time.sleep(10)


def runBackTest(strategy, past_ohlc):
    s = status.Status()
    l_ohlc = None
    for ohlc in past_ohlc:
        if l_ohlc == None:
            l_ohlc = ohlc
            continue

        if ohlc.close_time != l_ohlc.close_time:
            ohlc.print_price()
            if s.has_position:
                if strategy.closeSignal(ohlc, l_ohlc):
                    client.closePosition()  # TODO: implement
            else:
                entry = strategy.entrySignal(ohlc, l_ohlc)
                if entry != "NO_SIGNAL":
                    s.has_position = True
                    # TODO: order
        l_ohlc = ohlc


past_ohlc = client.get_price(60)
runBackTest(sanpei.Sanpei(), past_ohlc)
