from bitmex import Bitmex
import configparser
from strategy import sanpei
from notification import line
from notification.mylogger import BotLogger


# config.iniファイルから設定情報を取得
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
apiKey = config_ini.get("bitmex", "apiKey")
apiSecret = config_ini.get("bitmex", "apiSecret")
line_token = config_ini.get("LINE", "token")
log_path = config_ini.get("LOG", "path")

client = Bitmex(apiKey, apiSecret)
logger = BotLogger(log_path, line_token)

sanpei = sanpei.Sanpei(client, logger)
sanpei.run_bot()
