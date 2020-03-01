import json
from strategy.models import ohlc


def obj_json_default(obj):
    # https://qiita.com/Akio-1978/items/0bb4075ea05a8b4d53cc
    if isinstance(obj, object) and hasattr(obj, '__dict__'):
        return obj.__dict__
    raise TypeError


def save_as_json(obj_list, file_path, indent=4):
    file = open(file_path, "w", encoding="utf-8")
    json.dump(obj_list, fp=file, indent=indent, default=obj_json_default)
