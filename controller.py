from bitmex import Bitmex, T, O, H, L, C, V
import configparser
from strategy import sanpei
from strategy import donchian

from notification import line
from notification.mylogger import BotLogger

import time
import pandas as pd
from datetime import datetime

import numpy as np
from strategy.utils import indicator
import timeit

# config.iniファイルから設定情報を取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")
line_token = config_ini.get("LINE", "token")
log_path = config_ini.get("LOG", "path")

client = Bitmex(apiKey, apiSecret)
logger = BotLogger(log_path, line_token)

hoge = client.get_price_np()

""" a = indicator.sma(hoge[C], term=25)
b = indicator.sma_pd(hoge[C], term=25)
print(a, b) """


result = timeit.timeit(
    'indicator.sma(hoge[C])', globals=globals(), number=6000)

result2 = timeit.timeit(
    'indicator.sma_pd(hoge[C])', globals=globals(), number=6000)

print("[sma] 6000loop:", result, "[s] 1loop:", result/6000, "[s]")
print("[sma_pd] 6000loop:", result2, "[s] 1loop:", result2/6000, "[s]")

""" result = timeit.timeit(
    'indicator.sma_pd(hoge[C].tolist(), 5)', globals=globals(), number=6000)
 """

'''
past6000 = round(time.time()) - 6000 * 3600
ohlc_list = client.get_price(periods=3600, after=past6000)
don = donchian.Donchian(client, logger, 28, 20)
don.run_bot(ohlc_list=ohlc_list)
don.test_result.plotProfitChart()

# バックテストのパラメーター設定
chart_sec_list = [900, 1800, 3600, 7200, 14400, 21600]  # 時間足
term_list = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30]  # 上値ブレイクの判断期間
combinations = [(chart_sec, term)
                for chart_sec in chart_sec_list
                for term in term_list]


tdg_s = time.time()
# 価格データの取得
ohlc_dict = {}
for sec in chart_sec_list:
    now = round(time.time())
    after = 1577804400  # now - sec * 6000
    ohlc_list = client.get_price(periods=sec, after=after)
    print(f'{sec/60}分足：{len(ohlc_list)}本のデータを取得しました')
    ohlc_dict[str(sec)] = ohlc_list
tdg_e = time.time()
print(f'テストデータ取得時間：{tdg_e-tdg_s} [sec]')


sec_list = []
term_list = []

buy_count_list = []
buy_win_rate_list = []
buy_return_avg_list = []
buy_profit_list = []
buy_loss_list = []
buy_profit_loss_list = []

sell_count_list = []
sell_win_rate_list = []
sell_return_avg_list = []
sell_profit_list = []
sell_loss_list = []
sell_profit_loss_list = []

count_list = []
win_rate_list = []
return_avg_list = []
profit_list = []
loss_list = []
pf_list = []
drawdown_list = []

tt_s = time.time()
for sec, term in combinations:
    ohlc_list = ohlc_dict[str(sec)]
    don = donchian.Donchian(client, None, term, 20)
    don.run_bot(lot=1, period=sec, ohlc_list=ohlc_list)
    result = don.test_result.get_result()

    sec_list.append(sec)
    term_list.append(term)

    buy_count_list.append(result["buy_count"])
    buy_win_rate_list.append(result["buy_win_rate"])
    buy_return_avg_list.append(result["buy_return_avg"])
    buy_profit_list.append(result["buy_profit"])
    buy_loss_list.append(result["buy_loss"])
    buy_profit_loss_list.append(result["buy_profit_loss"])

    sell_count_list.append(result["sell_count"])
    sell_win_rate_list.append(result["sell_win_rate"])
    sell_return_avg_list.append(result["sell_return_avg"])
    sell_profit_list.append(result["sell_profit"])
    sell_loss_list.append(result["sell_loss"])
    sell_profit_loss_list.append(result["sell_profit_loss"])

    count_list.append(result["count"])
    win_rate_list.append(result["win_rate"])
    return_avg_list.append(result["return_avg"])
    profit_list.append(result["profit"])
    loss_list.append(result["loss"])
    pf_list.append(result["PF"])
    drawdown_list.append(result["drawdown"])
tt_e = time.time()
print(f'パラメータ最適化テスト処理時間：{tt_e-tt_s} [sec]')

df = pd.DataFrame({
    "時間軸": sec_list,
    "期間": term_list,
    "総エントリ数": count_list,
    "勝率": win_rate_list,
    "平均リターン": return_avg_list,
    "総利益": profit_list,
    "総損失": loss_list,
    "PF": pf_list,
    "最大ドローダウン": drawdown_list,
    "買いエントリ数": buy_count_list,
    "買い勝率": buy_win_rate_list,
    "買い平均リターン": buy_return_avg_list,
    "買い利益": buy_profit_list,
    "買い損失": buy_loss_list,
    "買い損益": buy_profit_loss_list,
    "売りエントリ数": sell_count_list,
    "売り勝率": sell_win_rate_list,
    "売り平均リターン": sell_return_avg_list,
    "売り利益": sell_profit_list,
    "売り損失": sell_loss_list,
    "売り損益": sell_profit_loss_list
})

# 列の順番を固定する
df = df[["時間軸",
         "期間",
         "総エントリ数",
         "勝率",
         "平均リターン",
         "総利益",
         "総損失",
         "PF",
         "最大ドローダウン",
         "買いエントリ数",
         "買い勝率",
         "買い平均リターン",
         "買い利益",
         "買い損失",
         "買い損益",
         "売りエントリ数",
         "売り勝率",
         "売り平均リターン",
         "売り利益",
         "売り損失",
         "売り損益"]]

df.to_csv(f'result-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv')
'''
