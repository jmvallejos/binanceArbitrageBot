import json
import time
import pandas as pd
import requests

from MexcSpot.SymbolStream import SymbolStream

class TickerStream():
    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        self.listPairs = dict()
        self.dfPairs = pd.DataFrame(columns=['Pair1', 'Pair2', 'Pair3'])

    def addTrianglePair(self, pair1, pair2, pair3, crypto1, crypto2, crypto3, 
                        commi1, commi2, commi3):
        self.addPair(pair1, crypto1, crypto2, commi1)
        self.addPair(pair2, crypto3, crypto2, commi2)
        self.addPair(pair3, crypto1, crypto3, commi3)

        countRecords = self.dfPairs.shape[0]
        self.dfPairs.loc[countRecords] = [self.listPairs[pair1], self.listPairs[pair2], 
                                        self.listPairs[pair3]]

    def addPair(self,pair, cryptoBuy, cryptoSell, commi):
        if(pair in self.listPairs):
            return
        self.listPairs[pair] = {"s": pair, "a": 0.00, "b": 0.00, "A": 0.00, "B": 0.00, 
            "cb": cryptoBuy, "cs": cryptoSell, "commi": (1-commi)}

    def InitConnection(self):
        for symbol in self.listPairs.keys():
            symbolStream = SymbolStream(self.environment, self.listPairs[symbol])
            symbolStream.InitConnection()
    
    