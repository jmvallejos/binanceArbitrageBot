import pandas as pd

from BinanceFutures.MarketOperator import MarketOperator
from BinanceFutures.TickerStream import TickerStream
from BinanceFutures.TriangularArbitrage import TriangularArbitrage

if __name__ == "__main__":
    #BTC ETH
    futureTickerStream = TickerStream()
    futureTickerStream.addTriangleSpotPair("ETHUSDC","ETHBTC", "BTCUSDC")
    futureTickerStream.InitConnection()
    
    marketOperator = MarketOperator()
    trinagularArbitrage = TriangularArbitrage(futureTickerStream.dfPairs, marketOperator)
    
    thereIsPrice = False
    while(not thereIsPrice):
        thereIsPrice = not any(pair["a"] == 0 for pair in futureTickerStream.listPairs.values())
    
    trinagularArbitrage.InitArbitrage("USDC")