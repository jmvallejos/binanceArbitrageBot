from MexcSpot.TriangularArbitrage import TriangularArbitrage
from MexcSpot.Environment import Environment
from MexcSpot.TickerStream import TickerStream

class MexcSpotTrader():
    def __init__(self):
        super().__init__()

    def Trade(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStream(environment)
        self.AdTrianglePairs(tickerStream)
        tickerStream.InitConnection()

        thereIsPrice = False
        while(not thereIsPrice):
            thereIsPrice = not any(pair["a"] == 0 for pair in tickerStream.listPairs.values())

        triangularArbitrage = TriangularArbitrage(tickerStream.dfPairs)
        triangularArbitrage.InitArbitrage()

    def AdTrianglePairs(self, tickerStream):
        tickerStream.addTrianglePair("ETHUSDC", "ETHBTC", "BTCUSDC","USDC", "ETH", "BTC", 0, 0.004, 0)

        #MX
        #tickerStream.addTrianglePair("MXUSDC", "MXETH", "ETHUSDC","USDC", "MX", "ETH", 0, 0.004, 0)
        #tickerStream.addTrianglePair("MXUSDC", "MXBTC", "BTCUSDC","USDC", "MX", "BTC", 0, 0.004, 0)

