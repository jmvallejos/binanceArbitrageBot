from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.TriangularArbitrage import TriangularArbitrage
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.TickerStream.TickerStreamSbe import TickerStreamSbe
from BinanceSpot.TickerStream.TickerSymbolAdds import TickerSymbolAdds


class TriangularArbitrageTest():
    def __init__(self):
        super().__init__()

    def Test(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamSbe(environment)
        TickerSymbolAdds(tickerStream).AddSymbols()
        tickerStream.InitConnection()

        marketOperator = MarketOperator(environment)
        accountData = AccountStream(environment, "USDC", marketOperator)

        arbitrage = TriangularArbitrage(environment, tickerStream.triangularPairs, tickerStream.listPrices, 
                                        marketOperator, accountData, "USDC", 0.1)
        
        thereIsPrice = False
        while not thereIsPrice:
            thereIsPrice = True
            for symbol in tickerStream.listPrices.keys():
                ask = tickerStream.listPrices[symbol].get("ask")
                if(ask is None or ask == 0):
                    thereIsPrice = False

        arbitrage.InitArbitrage()

