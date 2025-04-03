from BinanceSpot.Environment import Environment
from BinanceSpot.TickerStream.TickerStreamFixApi import TickerStreamFixApi
from BinanceSpot.TickerStream.TickerSymbolAdds import TickerSymbolAdds


class TickerStreamFixApiTest():
    def __init__(self):
        super().__init__()

    def TestSingleSymbol(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamFixApi(environment)
        TickerSymbolAdds(tickerStream).AddSingleSymbol()
        tickerStream.InitConnection()