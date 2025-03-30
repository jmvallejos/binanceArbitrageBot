import json
import threading

import requests
import websocket
from pybit.unified_trading import WebSocket
from time import sleep

class StreamPrices():
    def __init__(self, environment):
        super().__init__()
        self.BinancePrice = {}
        self.ByBitPrice = {}
        self.Environment = environment

    def SetBinancePair(self, symbol, buyCrypto, sellCrypto, commission):
        self.BinancePrice["symbol"] = symbol
        self.BinancePrice["cb"] = buyCrypto
        self.BinancePrice["cs"] = sellCrypto
        self.BinancePrice["commi"] = commission
        self.BinancePrice["bid"] = 0.00
        self.BinancePrice["ask"] = 0.00
        self.BinancePrice["bidq"] = 0.00
        self.BinancePrice["askq"] = 0.00
        self.BinancePrice["precisionLoteSize"] = 0
        self.BinancePrice["timestamp"] = 0

    def SetByBit(self, symbol, buyCrypto, sellCrypto, commission):
        self.ByBitPrice["symbol"] = symbol
        self.ByBitPrice["cb"] = buyCrypto
        self.ByBitPrice["cs"] = sellCrypto
        self.ByBitPrice["commi"] = commission
        self.ByBitPrice["bid"] = 0.00
        self.ByBitPrice["ask"] = 0.00
        self.ByBitPrice["bidq"] = 0.00
        self.ByBitPrice["askq"] = 0.00
        self.ByBitPrice["precisionLoteSize"] = 0
        self.ByBitPrice["timestamp"] = 0

    def InitStream(self):
        self.FillBinanceSymbolInfo()
        self.FillByBitSymbolInfo()
        self.binanceUrl = self.Environment.binanceSocketUrl  + '/ws/'+ self.BinancePrice["symbol"].lower() + '@ticker'
        self.byBitUrl = self.Environment.byBitSocketUrl + '/orderbook.1.'+ self.ByBitPrice["symbol"]
        threading.Thread(target = self.RunBinanceSocket).start()
        threading.Thread(target = self.RunByBitSocket).start()

    def RunBinanceSocket(self):
        ws = websocket.WebSocketApp(self.binanceUrl, on_message=self.OnTickBinance, on_error=self.OnErrorBinance, on_close=self.OnCloseBinance)
        ws.run_forever()

    def RunByBitSocket(self):
        ws = WebSocket(testnet=False, channel_type="spot")
        ws.orderbook_stream(depth=1, symbol=self.ByBitPrice["symbol"], callback=self.OnTickByBit)

    def OnTickBinance(self, ws, message):
        data = json.loads(message)
        
        self.BinancePrice["bid"] = float(data["b"])
        self.BinancePrice["bidq"] = float(data["B"])
        self.BinancePrice["ask"] = float(data["a"])
        self.BinancePrice["askq"] = float(data["A"])
        self.BinancePrice["timestamp"] = self.Environment.GetLongUtcTimeStamp()

    def OnErrorBinance(self, error, c):
        print(c)
        self.InitStream()

    def OnCloseBinance(self):
        self.InitStream()

    def OnTickByBit(self, message):
        data = message["data"]
        
        self.ByBitPrice["bid"] = float(data["b"][0][0])
        self.ByBitPrice["bidq"] = float(data["b"][0][1])
        self.ByBitPrice["ask"] = float(data["a"][0][0])
        self.ByBitPrice["askq"] = float(data["a"][0][1])
        self.ByBitPrice["timestamp"] = int(message["ts"])
        
    def FillBinanceSymbolInfo(self):
        url = self.Environment.binanceApiUrl
        url += "/api/v3/exchangeInfo?symbol=" + self.BinancePrice["symbol"]
        
        data = requests.get(url)
        loteSize = json.loads(data.text)["symbols"][0]["filters"][1]["stepSize"]
        loteSize = float(loteSize)
        loteSize = str(loteSize)
        self.BinancePrice["precisionLoteSize"] = int(loteSize.split('-')[1])

    def FillByBitSymbolInfo(self):
        url = self.Environment.byBitApiUrl
        url += "/v5/market/instruments-info?category=spot&symbol=" + self.ByBitPrice["symbol"]

        data = requests.get(url) 
        loteSize = json.loads(data.text)["result"]["list"][0]["lotSizeFilter"]["basePrecision"]
        loteSize = float(loteSize)
        loteSize = str(loteSize)
        self.ByBitPrice["precisionLoteSize"] = int(loteSize.split('-')[1])