import struct
import threading
import time
import requests
import websocket
import json
import pandas as pd
pd.options.mode.chained_assignment = None 

class TickerStreamSbe():
    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        self.lastLogErrorCompleteTickSize = 0
        self.listPrices = {}
        self.dfPairs = pd.DataFrame(columns=[
            'pair1', 'pair2', 'pair3', 
            'coin1', 'coin2', 'coin3',
            'commi1', 'commi2','commi3', 
            'precisionLote1', 'precisionLote2','precisionLote3',
            "ExpectedResult"])

    def addTrianglePair(self, pair1, pair2, pair3, coin1, coin2, coin3, 
                        commi1, commi2, commi3):
        
        countRecords = self.dfPairs.shape[0]
        self.dfPairs = pd.concat([self.dfPairs, pd.DataFrame(columns=self.dfPairs.columns)], ignore_index=True)

        self.listPrices[pair1] = {}
        self.listPrices[pair2] = {}
        self.listPrices[pair3] = {}


        self.dfPairs.at[countRecords,"pair1"] = pair1
        self.dfPairs.at[countRecords,"pair2"] = pair2
        self.dfPairs.at[countRecords,"pair3"] = pair3
        self.dfPairs.at[countRecords,"coin1"] = coin1
        self.dfPairs.at[countRecords,"coin2"] = coin2
        self.dfPairs.at[countRecords,"coin3"] = coin3
        self.dfPairs.at[countRecords,"commi1"] = commi1
        self.dfPairs.at[countRecords,"commi2"] = commi2
        self.dfPairs.at[countRecords,"commi3"] = commi3

    def InitConnection(self):
        self.environment.Log("Se inicia el stream de precios")
        self.TryCompletePrecisionLote()
        url = "wss://stream-sbe.binance.com/stream?streams="

        pairs = pd.Series(self.dfPairs['pair1'].tolist() 
                          + self.dfPairs['pair2'].tolist() 
                          + self.dfPairs['pair3'].tolist()).unique()

        for symbol in list(pairs):
            url = url + symbol.lower() + '@bestBidAsk/'
        self.url = url[:-1]

        threading.Thread(target = self.RunSocket).start()

    def RunSocket(self):
        header = {
            "X-MBX-APIKEY": "oPGodiu3ZyAuXYwgxBizXHJE3txGhZ55yrynzyO23rMyof2WKYgdF1GbW4rmoDqD"
        }
        ws = websocket.WebSocketApp(self.url, on_message=self.OnTick, on_error=self.OnError, on_close=self.OnClose, header=header)
        ws.run_forever()

    def OnTick(self, ws, message):
        symbol = message[59:59 + message[58]].decode('utf-8')
        
        self.listPrices[symbol] = {
            "bid": struct.unpack("<q", message[26:26 + 8])[0] / 10**8,
            "bidq": struct.unpack("<q", message[34:34 + 8])[0] / 10**8,
            "ask": struct.unpack("<q", message[42:42 + 8])[0] / 10**8,
            "askq": struct.unpack("<q", message[50:50 + 8])[0] / 10**8
        }
        
        self.environment.SetPriceStatus()
        
        #utcTime = struct.unpack("<q", message[8:8 + 8])[0] / 10**6
        #if(symbol == "BTCUSDC"):
            #print(str(time.time() - utcTime))

    def OnError(self, error, c):
        threading.Thread(target = self.RunSocket).start()

    def OnClose(self, a, b, c):
        threading.Thread(target = self.RunSocket).start()

    def TryCompletePrecisionLote(self):
        success = False
        while(not success):
            try:
                self.CompletePrecisionLote()
                success = True
            except:
                success = False
                time.sleep(1)
                current = self.environment.GetLongUtcTimeStamp()
                if(current - self.lastLogErrorCompleteTickSize > 20000):
                    self.environment.Log("Error al intentar setear el lotesize")
                    self.lastLogErrorCompleteTickSize = current

    def CompletePrecisionLote(self):
        url = self.environment.apiUrl
        url += "/api/v3/exchangeInfo?symbols="

        pairs = pd.Series(self.dfPairs['pair1'].tolist() 
                          + self.dfPairs['pair2'].tolist() 
                          + self.dfPairs['pair3'].tolist()).unique()

        url += json.dumps(list(pairs))
        url = url.replace('"', '%22')
        url = url.replace(' ', '')

        data = requests.get(url)
        data = json.loads(data.text)

        for symbol_info in data["symbols"]:
            symbol = symbol_info["symbol"]
            loteSize = symbol_info["filters"][1]["stepSize"]
            loteSize = loteSize.rstrip('0').rstrip('.')
            precision = 0
            if("-" in loteSize):
                precision = int(loteSize.split('-')[1])
            
            if("." in loteSize):
                precision = len(loteSize.split(".")[1])

            self.dfPairs.loc[self.dfPairs['pair1'] == symbol, 'precisionLote1'] = 10 ** precision
            self.dfPairs.loc[self.dfPairs['pair2'] == symbol, 'precisionLote2'] = 10 ** precision
            self.dfPairs.loc[self.dfPairs['pair3'] == symbol, 'precisionLote3'] = 10 ** precision

    