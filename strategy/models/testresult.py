import numpy as np
from notification import mylogger

TAKER_FEE = 0.00075
MAKER_FEE = -0.00025


class BackTestResult():
    def __init__(self):
        self.buy_count = 0
        self.buy_winning = 0
        self.buy_return = []
        self.buy_profit = []
        self.sell_count = 0
        self.sell_winning = 0
        self.sell_return = []
        self.sell_profit = []
        self.slippage = []
        self.log = []

        self.entry_price = None
        self.side = ""
        self.qty = 0

        self.result_logger = mylogger.BotLogger("./result.log", None)

    def entry(self, side, lot, entry_price):
        self.entry_price = entry_price
        self.qty = lot
        self.side = side

    def close(self, exit_price):
        # 取引手数料
        #entry_trade_cost = round(self.qty * TAKER_FEE)
        #exit_trade_cost = round(self.qty * TAKER_FEE)
        #trade_cost = entry_trade_cost + exit_trade_cost
        # self.slippage.append(trade_cost)
        trade_cost = 0

        if self.side == "buy":
            buy_profit = (exit_price - self.entry_price) * \
                self.qty - trade_cost
            self.buy_count += 1
            self.buy_profit.append(buy_profit)
            self.buy_return.append(
                round(buy_profit / self.entry_price * 100, 4))
            if buy_profit > 0:
                self.buy_winning += 1
            self.result_logger.print_log(
                f'BUY  Entry:{str(self.entry_price).rjust(8)} Close:{str(exit_price).rjust(8)} Profit:{str(buy_profit).rjust(6)}')

        if self.side == "sell":
            sell_profit = (self.entry_price - exit_price) * \
                self.qty - trade_cost
            self.sell_count += 1
            self.sell_profit.append(sell_profit)
            self.sell_return.append(
                round(sell_profit / self.entry_price * 100, 4))
            if sell_profit > 0:
                self.sell_winning += 1
            self.result_logger.print_log(
                f'SELL Entry:{str(self.entry_price).rjust(8)} Close:{str(exit_price).rjust(8)} Profit:{str(sell_profit).rjust(6)}')

        self.qty = 0
        self.side = ""
        self.entry_price = None

    def print_result(self, file_path):
        buy_gross_profit = np.sum(self.buy_profit)
        sell_gross_profit = np.sum(self.sell_profit)

        print("バックテストの結果")
        print("--------------------------")
        print("買いエントリの成績")
        print("--------------------------")
        print("トレード回数  :  {}回".format(self.buy_count))
        print("勝率          :  {}％".format(
            round(self.buy_winning / self.buy_count * 100, 1)))
        print("平均リターン  :  {}％".format(
            round(np.average(self.buy_return), 4)))
        print("総損益        :  {}円".format(
            np.sum(self.buy_profit)))

        print("--------------------------")
        print("売りエントリの成績")
        print("--------------------------")
        print("トレード回数  :  {}回".format(self.sell_count))
        print("勝率          :  {}％".format(
            round(self.sell_winning / self.sell_count * 100, 1)))
        print("平均リターン  :  {}％".format(
            round(np.average(self.sell_return), 4)))
        print("総損益        :  {}円".format(
            np.sum(self.sell_profit)))

        print("--------------------------")
        print("総合の成績")
        print("--------------------------")
        print("総損益        :  {}円".format(
            np.sum(self.sell_profit) + np.sum(self.buy_profit)))
        print("手数料合計    :  {}円".format(np.sum(self.slippage)))

        # ログファイルの出力
        # file = open(file_path, 'wt', encoding='utf-8')
        # file.writelines(self.log)
