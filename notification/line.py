import requests


class LineNotifier:
    def __init__(self, token):
        self.token = token

    def notify(self, msg):
        url = "https://notify-api.line.me/api/notify"
        data = {"message": msg}
        headers = {"Authorization": "Bearer " + self.token}
        requests.post(url, data=data, headers=headers)
