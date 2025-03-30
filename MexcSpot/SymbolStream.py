import json
import threading

import websocket
from MexcSpot.protoc import PushDataV3ApiWrapper_pb2 as protoc


class SymbolStream():
    def __init__(self, environment, pair):
        self.environment = environment
        self.pair = pair

    def InitConnection(self):
        self.url = self.environment.socketUrl
        threading.Thread(target = self.RunSocket).start()

    def RunSocket(self):
        ws = websocket.WebSocketApp(self.url, on_open=self.OnOpen, on_message=self.OnTick, on_error=self.OnError, on_close=self.OnClose)
        ws.run_forever()

    def OnOpen(self, ws):
        obj = {
            "method": "SUBSCRIPTION",
            "params": ["spot@public.limit.depth.v3.api.pb@"+self.pair["s"]+"@5"]
        }   
        
        ws.send(json.dumps(obj))

    def OnTick(self, ws, message):
        if isinstance(message, str):
            return 
        
        response = protoc.PushDataV3ApiWrapper()
        response.ParseFromString(message)
        
        self.pair["a"] = float(response.publicLimitDepths.asks[0].price)
        self.pair["b"] = float(response.publicLimitDepths.bids[0].price)
        self.pair["A"] = float(response.publicLimitDepths.asks[0].quantity)
        self.pair["B"] = float(response.publicLimitDepths.bids[0].quantity) 
            
        if(response.symbol == "BTCUSDC"):
            print(str(self.pair["a"]) + ' ' + str(self.pair["A"]))
        

    def OnError(self, error, c):
        print(c)
        self.InitConnection()

    def OnClose(self):
        self.InitConnection()