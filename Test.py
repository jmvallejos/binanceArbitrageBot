from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.TickerStream import TickerStream
from BinanceSpot.TriangularArbitrage import TriangularArbitrage

if __name__ == "__main__":    
    environment = Environment()
    environment.SetProdValues()

    marketOperator = MarketOperator(environment)
    accountStream = AccountStream(environment, "USDC", marketOperator)
    accountStream.GetWalletBalance()

    
