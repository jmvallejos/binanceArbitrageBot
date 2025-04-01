from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.TickerStream import TickerStream
from BinanceSpot.TriangularArbitrage import TriangularArbitrage

if __name__ == "__main__":    
    environment = Environment()
    environment.SetProdValues()

    tickerStream = TickerStream(environment)
    tickerStream.addTrianglePair("ETHUSDC", "ETHBTC", "BTCUSDC","USDC", "ETH", "BTC", 0.0007125, 0.00075, 0.0071250)

    tickerStream.InitConnection()

    while True:
        a = 1
    
