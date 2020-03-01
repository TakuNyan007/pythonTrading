import bitmex
import configparser
from strategy import sanpei
from strategy.models import status
from notification import line
from datetime import datetime
import calendar
import time

# config.iniファイルから設定情報を取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")
line_token = config_ini.get("LINE", "token")

client = bitmex.Bitmex(apiKey, apiSecret)
notifier = line.LineNotifier(line_token)


def cancel_all_orders(orders, interval):
    if len(orders) == 0:
        return

    now = int(time.time()*1000)  # TODO: 厳密ではないのでちゃんとしたやり方にする
    o_time = orders[0]["timestamp"]
    uncontracted_time = now - o_time
    if uncontracted_time > interval * 5 * 1000:
        client.cancel_all_orders()
        print("注文が" + (interval * 5) + "秒以内に約定しなかったため、キャンセルしました。")


def runBot(strategy, intervalSec=10):
    l_ohlc = None
    while True:
        ohlc = client.get_price_by_idx(60)  # 確定している最新の足を取得
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


# runBot(sanpei.Sanpei())
# print(client.handle(client.get_price_by_idx, 60))
# print(client.handle(client.cancel_all_orders))
# notifier.notify("ゴリラ")

print(client.get_price(60))
