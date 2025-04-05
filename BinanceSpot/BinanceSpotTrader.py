from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.TickerStream.TickerStreamIndividualTick import TickerStreamIndividualTick
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator.MarketOperatorApi import MarketOperatorApi
from BinanceSpot.TickerStream.TickerSymbolAdds import TickerSymbolAdds
from BinanceSpot.TriangularArbitrage import TriangularArbitrage

class BinanceSpotTrader:
    def __init__(self):
        super().__init__()
        
    def Trade(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamIndividualTick(environment)
        TickerSymbolAdds(tickerStream)   
        tickerStream.InitConnection()

        stableCoin = "USDC"

        marketOperator = MarketOperatorApi(environment)
        accountStream = AccountStream(environment, stableCoin, marketOperator)
        
        thereIsPrice = False
        df = tickerStream.dfPairs
        while(not thereIsPrice):
            thereIsPrice = not (df["ask1"].isnull().any() or df["ask2"].isnull().any() or df["ask3"].isnull().any())

        environment.Log("Se llenaron los precios. Inicio del arbitraje")
        trinagularArbitrage = TriangularArbitrage(environment, tickerStream.dfPairs, marketOperator, accountStream, stableCoin, -0.2)
        trinagularArbitrage.InitArbitrage()