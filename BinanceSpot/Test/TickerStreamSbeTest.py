from BinanceSpot.Environment import Environment
from BinanceSpot.TickerStream.TickerStreamSbe import TickerStreamSbe
from BinanceSpot.TickerStream.TickerSymbolAdds import TickerSymbolAdds


class TickerStreamSbeTest():
    def __init__(self):
        super().__init__()

    def TestSingleSymbols(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamSbe(environment)
        TickerSymbolAdds(tickerStream).AddSingleSymbol()
        tickerStream.InitConnection()

    def TestThreeSymbols(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamSbe(environment)
        TickerSymbolAdds(tickerStream).AddTriangle()
        tickerStream.InitConnection()

    def TestAllSymbols(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamSbe(environment)
        TickerSymbolAdds(tickerStream).AddSymbols()
        tickerStream.InitConnection()