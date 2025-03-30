from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.TickerStream import TickerStream
from BinanceSpot.TriangularArbitrage import TriangularArbitrage

if __name__ == "__main__":    
    environment = Environment()
    environment.SetProdValues()

    tickerStream = TickerStream(environment)
    tickerStream.addTrianglePair("ETHUSDC", "ETHBTC", "BTCUSDC","USDC", "ETH", "BTC", 0, 0, 0)
    tickerStream.addTrianglePair("SOLUSDC","SOLETH", "ETHUSDC","USDC", "SOL","ETH", 0, 0, 0)

    tickerStream.InitConnection()

    thereIsPrice = False
    df = tickerStream.dfPairs
    while(not thereIsPrice):
        thereIsPrice = not (df["ask1"].isnull().any() or df["ask2"].isnull().any() or df["ask3"].isnull().any())

    accountStream = AccountStream(environment)
    accountStream.GetWalletBalance()

    marketOperator = MarketOperator(accountStream.WalletSpot, environment)

    triangularArbitrage = TriangularArbitrage(tickerStream.dfPairs, marketOperator, accountStream, "USDC", -0.9)
    triangularArbitrage.InitArbitrage()

    
