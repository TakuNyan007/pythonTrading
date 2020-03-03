import bitmex
import configparser
from strategy import sanpei
from strategy.models import status
from notification import line
from datetime import datetime
import calendar
import time
from notification import mylogger
import backtest
from strategy.models import testresult

# config.iniファイルから設定情報を取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")
line_token = config_ini.get("LINE", "token")
log_path = config_ini.get("LOG", "path")

client = bitmex.Bitmex(apiKey, apiSecret)
logger = mylogger.BotLogger(log_path, line_token)
testlogger = mylogger.BotLogger("./test.log", None)


def cancel_all_orders(orders, interval):
    if len(orders) == 0:
        return

    now = int(time.time()*1000)  # TODO: 厳密ではないのでちゃんとしたやり方にする
    o_time = orders[0]["timestamp"]
    uncontracted_time = now - o_time
    if uncontracted_time > interval * 5 * 1000:
        client.cancel_all_orders()
        print("注文が" + (interval * 5) + "秒以内に約定しなかったため、キャンセルしました。")


MODE_BACK_TEST = "MODE_BACK_TEST"
MODE_REAL_TRADE = "MODE_REAL_TRADE"


def runBot(strategy=sanpei.Sanpei(), lot=1, period=60, mode=MODE_BACK_TEST):
    t1 = time.time()

    ohlc_list = None
    result = None
    is_backtest = mode != MODE_REAL_TRADE
    if is_backtest:
        ohlc_list = backtest.get_price_from_json()  # バックテストのみで使用
        result = testresult.BackTestResult()

    l_ohlc = None
    intervalSec = 0 if is_backtest else 10
    idx = 0  # バックテストのみで使用
    while True:
        # 確定している最新の足を取得
        ohlc = ohlc_list[idx] if is_backtest else client.get_price_by_idx(
            period)

        # 初回ループ時のみl_ohlcにohlcをセット
        if l_ohlc == None:
            ohlc.print_price()
            l_ohlc = ohlc
            idx += 1
            continue

        # orderが一定時間約定しなかった場合、キャンセルする
        if not is_backtest:
            orders = client.fetch_open_orders()
            if len(orders) != 0:
                cancel_all_orders(orders, intervalSec)

        if ohlc.close_time != l_ohlc.close_time:
            ohlc.print_price()
            qty = result.qty if is_backtest else client.get_position()  # TODO: change lot
            if qty != 0:
                signal = strategy.closeSignal(ohlc, l_ohlc)
                if signal:
                    msg = "[{time}] close position price:{price} amount:{lot}".format(
                        time=ohlc.close_time_str(), price=ohlc.close, lot=lot)

                    if is_backtest:
                        result.close(exit_price=ohlc.close)
                        testlogger.print_log(msg)

                    else:
                        client.close_position(qty)
                        logger.log_and_notify(msg)
            else:
                side = strategy.entrySignal(ohlc, l_ohlc)
                if side != "":
                    msg = "[{time}] entry:{side} price:{price} amount:{lot}".format(
                        time=ohlc.close_time_str(), side=side, price=ohlc.close, lot=lot)
                    if is_backtest:
                        result.entry(side, lot, ohlc.close)
                        testlogger.print_log(msg)
                    else:
                        client.create_limit_order(side, ohlc.close, lot)
                        logger.log_and_notify(msg)

            l_ohlc = ohlc
        idx += 1
        if idx >= len(ohlc_list):
            result.print_result("./result.txt")
            break

        if not is_backtest:
            time.sleep(intervalSec)
    t2 = time.time()
    print(f'{len(ohlc_list)}本のバックテストに{round(t2-t1)}秒かかりました')


runBot()
# runBot(sanpei.Sanpei(), intervalSec=10, lot=1, period=60)
# print(client.handle(client.get_price_by_idx, 60))
# print(client.handle(client.cancel_all_orders))
# notifier.notify("ゴリラ")
# print(client.get_price(60))
# logger.log_and_notify("テスト")
