import requests
# from logging import getLogger, Formatter, StreamHandler, FileHandler, INFO, basicConfig
import logging
from notification import line


class BotLogger():
    def __init__(self, log_path, line_token):
        if line_token:
            self.notifier = line.LineNotifier(line_token)
        else:
            self.notifier = None

        # ログの設定
        self.logger = logging.getLogger(__name__)
        handlerSh = logging.StreamHandler()
        handlerFile = logging.FileHandler(filename=log_path, encoding="utf-8")
        handlerSh.setLevel(logging.INFO)
        handlerSh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
        handlerFile.setLevel(logging.INFO)
        handlerFile.setFormatter(
            logging.Formatter("[%(asctime)s] %(message)s"))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handlerSh)
        self.logger.addHandler(handlerFile)

    def print_log(self, text):
        self.logger.info(text)

    def log_and_notify(self, text):
        self.print_log(text)
        if self.notifier:
            self.notifier.notify(text)
