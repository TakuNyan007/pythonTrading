# Python BTC BOT

## What's this Project?
[文系でもわかる！BitcoinのBOT自動売買トレードの始め方](https://ryota-trade.com)を参考にして、BTC自動売買BOTを実装していくプロジェクトです。Bitflyerではなく、Bitmexを扱います。  

## 使い方
1. `config.ini` をcontroller.pyと同じ階層に作成する
2. 下記のようにconfig情報を記載する
```
[bitmex]
apiKey = APIキーを入力
apiSecret = APIシークレットをにゅうろy九

[LINE]
token = ライントークンを入力

```
3. `controller.py`を実行する