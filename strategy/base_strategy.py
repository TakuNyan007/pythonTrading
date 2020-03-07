from datetime import datetime
import calendar
import time
from strategy.models import testresult, ohlc
from abc import ABCMeta, abstractmethod
import json

MODE_BACK_TEST = "MODE_BACK_TEST"
MODE_REAL_TRADE = "MODE_REAL_TRADE"
OHLC_FILE_PATH = "./ohlc.json"
BUY = "buy"
SELL = "sell"
NO_ENTRY = ""


class Strategy(metaclass=ABCMeta):
    def __init__(self, client, logger):
        self.client = client
        self.logger = logger
        self.test_result = None
        self.term = 1  # 継承先でOverride

    def get_price_from_json(self, path=OHLC_FILE_PATH):
        file = open(path, 'r', encoding='utf-8')
        ohlc_dict_list = json.load(fp=file)  # jsonをObjectにパースする方法がわからない
        ohlc_list = []
        for data in ohlc_dict_list:
            ohlc_list.append(ohlc.Ohlc(
                data["close_time"], data["open"], data["high"], data["low"], data["close"]))

        return ohlc_list

    def cancel_all_orders(self, orders, interval):
        if len(orders) == 0:
            return

        now = int(time.time()*1000)  # TODO: 厳密ではないのでちゃんとしたやり方にする
        o_time = orders[0]["timestamp"]
        uncontracted_time = now - o_time
        if uncontracted_time > interval * 5 * 1000:
            self.client.cancel_all_orders()
            print("注文が" + (interval * 5) + "秒以内に約定しなかったため、キャンセルしました。")

    def run_bot(self, lot=1, period=60, mode=MODE_BACK_TEST):
        t1 = time.time()

        ohlc_list = None
        is_backtest = mode != MODE_REAL_TRADE
        if is_backtest:
            ohlc_list = self.get_price_from_json()  # バックテストのみで使用
            self.test_result = testresult.BackTestResult()

        l_ohlc_list = []
        intervalSec = 0 if is_backtest else 10
        idx = 0  # バックテストのみで使用
        while True:
            # 確定している最新の足を取得
            ohlc = ohlc_list[idx] if is_backtest else self.client.get_price_by_idx(
                period)

            # 初回ループ時のみl_ohlc_listにohlcをセット
            if len(l_ohlc_list) < self.term:
                l_ohlc_list.append(ohlc)
                idx += 1
                continue

            # orderが一定時間約定しなかった場合、キャンセルする
            if not is_backtest:
                orders = self.client.fetch_open_orders()
                if len(orders) != 0:
                    self.cancel_all_orders(orders, intervalSec)

            if ohlc.close_time != l_ohlc_list[-1].close_time:
                # ohlc.print_price() # ←これをやるとめちゃくちゃ遅くなるのでコメントアウト
                qty = self.test_result.qty if is_backtest else self.client.get_position()
                if qty != 0:
                    signal, isDoten = self.closeSignal(ohlc, l_ohlc_list)
                    if signal:
                        msg = "[{time}] close position price:{price} amount:{lot}".format(
                            time=ohlc.close_time_str(), price=ohlc.close, lot=lot)

                        if is_backtest:
                            side = self.test_result.close(
                                exit_price=ohlc.close, close_time_str=ohlc.close_time_str())
                            if isDoten:
                                self.test_result.entry(side, lot, ohlc.close)
                        else:
                            self.client.close_position(qty)
                            self.logger.log_and_notify(msg)
                            if isDoten:
                                pass
                                # TODO: Implement Doten logic
                else:  # isDoten = True となるStrategyのときはここは初回Entry時のみ通る
                    side = self.entrySignal(ohlc, l_ohlc_list)
                    if side != "":
                        msg = "[{time}] entry:{side} price:{price} amount:{lot}".format(
                            time=ohlc.close_time_str(), side=side, price=ohlc.close, lot=lot)
                        if is_backtest:
                            self.test_result.entry(side, lot, ohlc.close)
                        else:
                            self.client.create_limit_order(
                                side, ohlc.close, lot)
                            self.logger.log_and_notify(msg)
                del l_ohlc_list[0]
                l_ohlc_list.append(ohlc)

            idx += 1
            if idx >= len(ohlc_list):
                self.test_result.print_result("./result.txt")
                break

            if not is_backtest:
                time.sleep(intervalSec)
        t2 = time.time()
        print(f'{len(ohlc_list)}本のバックテストに{round(t2-t1)}秒かかりました')
        self.test_result.plotProfitChart()

    @abstractmethod
    def closeSignal(self, ohlc, l_ohlc_list):
        return False, False  # closeSignal, dotenSignal

    @abstractmethod
    def entrySignal(self, ohlc, l_ohlc_list):
        return ""


if __name__ == '__main__':
    pass
