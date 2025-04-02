from BinanceSpot.Environment import Environment
from BinanceSpot.TickerStream.TickerStreamIndividualTick import TickerStreamIndividualTick
from BinanceSpot.TickerStream.TickerSymbolAdds import TickerSymbolAdds


class TickerStreamIndividualTickTest():
    def __init__(self):
        super().__init__()

    def TestAllSymbols(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamIndividualTick(environment)
        TickerSymbolAdds(tickerStream).AddSymbols()
        tickerStream.InitConnection()