import threading
import websocket
import json
from functools import partial
import pandas as pd

class TickerStream():
    def __init__(self):
        super().__init__()
        self.listPairs = dict()
        self.dfPairs = pd.DataFrame(columns=['Pair1', 'Pair2', 'Pair3'])

    def addTrianglePair(self, pair1, pair2, pair3):
        self.addPair(pair1)
        self.addPair(pair2)
        self.addPair(pair3)

        countRecords = self.dfPairs.shape[0]
        self.dfPairs.loc[countRecords] = [self.listPairs[pair1], self.listPairs[pair2], self.listPairs[pair3]]

    def addPair(self,pair):
        if(pair in self.listPairs):
            return
        self.listPairs[pair] = {"s": pair, "a": 0.00, "b": 0.00, "A": 0.00, "B": 0.00}
        
    def InitConnection(self):
        url = 'wss://fstream.binance.com/stream?streams='
        for key in self.listPairs.keys():
            url = url + key.lower() + '@bookTicker/'
        self.url = url[:-1]

        threading.Thread(target = self.RunSocket).start()

    def RunSocket(self):
        ws = websocket.WebSocketApp(self.url, on_message=partial(self.OnTick, self.listPairs), on_error=self.OnError)
        ws.run_forever()

    def OnTick(p, fun, ws, message):
        data = json.loads(message)["data"]

        pair = p.listPairs[data["s"]] 
        pair["a"] = float(data["a"])
        pair["b"] = float(data["b"])
        pair["A"] = float(data["A"])
        pair["B"] = float(data["B"])

    def OnError(ws, error, c):
        print("Error" + c)
