import bitmex
import configparser
from strategy import sanpei
from strategy.models import status
from datetime import datetime
import calendar
import time
from notification import mylogger
from myutil import myjson
import json
from strategy.models import ohlc

# config.iniファイルから設定情報を取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")
log_path = config_ini.get("LOG", "path")

OHLC_FILE_PATH = "./ohlc.json"


def print_get_price_result(price):
    if price == None or len(price) == 0:
        print("No data.")
        return
    print("先頭データ : " + price[0].close_time_str() +
          "  UNIX時間 : " + str(price[0].close_time))
    print("末尾データ : " + price[-1].close_time_str() +
          "  UNIX時間 : " + str(price[-1].close_time))
    print("合計 ： " + str(len(price)) + "件のローソク足データを取得")
    print("--------------------------")
    print("--------------------------")


def get_price_from_json(path=OHLC_FILE_PATH):
    file = open(path, 'r', encoding='utf-8')
    ohlc_dict_list = json.load(fp=file)  # jsonをObjectにパースする方法がわからない
    ohlc_list = []
    for data in ohlc_dict_list:
        ohlc_list.append(ohlc.Ohlc(
            data["close_time"], data["open"], data["high"], data["low"], data["close"]))

    return ohlc_list


# price = client.get_price(periods=900, after=1521849600)
# print_get_price_result(price)
#myjson.save_as_json(price, OHLC_FILE_PATH)
#hoge = get_price_from_json()
# print("end")
if __name__ == '__main__':
    pass
