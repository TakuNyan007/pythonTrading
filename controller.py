from bitmex import Bitmex, T, O, H, L, C, V, BUY, SELL
import configparser
from strategy import donchian2

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


""" past6000 = round(time.time()) - 6000 * 3600
ohlc_list = client.get_price_np(periods=3600, after=past6000)
don = donchian2.Donchian(28, 20)
don.run_bot(ohlc_list)
don.plot_gross_plofit()
 """
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
    ohlc_list = client.get_price_np(periods=sec, after=after)
    print(f'{sec/60}分足：{ohlc_list.shape[1]}本のデータを取得しました')
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
    tls = time.time()
    ohlc_list = ohlc_dict[str(sec)]
    don = donchian2.Donchian(term, 20)
    don.run_bot(ohlc_list)
    df = don.result_df()

    sec_list.append(sec)
    term_list.append(term)

    buys = df[df.entry_side.isin([BUY])]
    buy_count = len(buys)
    buy_profit_loss = buys["profit"].sum()
    buy_return_avg = buys["profit"].mean()
    buy_wins = df[df["entry_side"].isin([BUY]) & (df["profit"] > 0)]
    buy_loses = df[df["entry_side"].isin([BUY]) & (df["profit"] < 0)]

    buy_count_list.append(buy_count)
    buy_win_rate_list.append(len(buy_wins)/buy_count * 100)
    buy_return_avg_list.append(buy_return_avg)
    buy_profit_list.append(buy_wins["profit"].sum())
    buy_loss_list.append(buy_loses["profit"].sum())
    buy_profit_loss_list.append(buy_profit_loss)

    sells = df[df["entry_side"].isin([SELL])]
    sell_count = len(sells)
    sell_profit_loss = sells["profit"].sum()
    sell_return_avg = sells["profit"].mean()
    sell_wins = df[df["entry_side"].isin([SELL]) & (df["profit"] > 0)]
    sell_loses = df[df["entry_side"].isin([SELL]) & (df["profit"] < 0)]

    sell_count_list.append(sell_count)
    sell_win_rate_list.append(len(sell_wins)/sell_count)
    sell_return_avg_list.append(sell_return_avg)
    sell_profit_list.append(sell_wins["profit"].sum())
    sell_loss_list.append(sell_loses["profit"].sum())
    sell_profit_loss_list.append(sell_profit_loss)

    profit = df[df["profit"] > 0]["profit"].sum()
    loss = df[df["profit"] < 0]["profit"].sum()
    pf = profit / loss

    count_list.append(len(df))
    win_rate_list.append((len(buy_wins) + len(sell_wins)) / len(df) * 100)
    return_avg_list.append(df["profit"].mean())
    profit_list.append(profit)
    loss_list.append(loss)
    pf_list.append(pf)
    drawdown_list.append(df["drawdown"].max())
    print(f'{term}期間 {sec/60}分足 {time.time() - tls}秒バックテストにかかりました')
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
