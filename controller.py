import bitmex
import configparser
from strategy import sanpei
from strategy.models import status
from datetime import datetime
import calendar
import time

# config.iniファイルからapiKeyとapiSecretを取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")

client = bitmex.Bitmex(apiKey, apiSecret)


def cancel_all_orders(orders, interval):
    if len(orders) == 0:
        return

    now = int(time.time()*1000)  # TODO: 厳密ではないのでちゃんとしたやり方にする
    o_time = orders[0]["timestamp"]
    uncontracted_time = now - o_time
    if uncontracted_time > interval * 5 * 1000:
        client.cancel_all_orders()
        print("注文が" + (interval * 5) + "秒以内に約定しなかったため、キャンセルしました。")


def runBot(strategy, intervalSec):
    l_ohlc = None
    while True:
        ohlc = client.get_last_price(60)
        # 初回ループ時のみl_ohlcにohlcをセット
        if l_ohlc == None:
            ohlc.print_price()
            l_ohlc = ohlc
            continue

        # orderが一定時間約定しなかった場合、キャンセルする
        orders = client.fetch_open_orders()
        if len(orders) != 0:
            cancel_all_orders(orders, intervalSec)

        if ohlc.close_time != l_ohlc.close_time:
            ohlc.print_price()
            qty = client.get_position()
            if qty != 0:
                signal = strategy.closeSignal(ohlc, l_ohlc)
                if signal:
                    client.close_position(qty)
            else:
                side = strategy.entrySignal(ohlc, l_ohlc)
                if side != "":
                    client.create_limit_order(side, ohlc.close, 10)
                    print(10 + "USD: " + side)
            l_ohlc = ohlc

        time.sleep(intervalSec)


runBot(sanpei.Sanpei(), 10)
