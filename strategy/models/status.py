import dataclasses
from datetime import datetime


class Status:

    def __init__(self):
        self.position = Position()
        self.order = Order()


class Position:
    def __init__(self):
        self.exist = False
        self.side: ""


class Order:
    def __init__(self):
        self.exist = False
        self.side: ""
        self.count: 0
