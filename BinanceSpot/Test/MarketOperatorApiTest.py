from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator.MarketOperatorApi import MarketOperatorApi
from BinanceSpot.TickerStream.TickerStreamSbe import TickerStreamSbe
from BinanceSpot.TickerStream.TickerSymbolAdds import TickerSymbolAdds


class MarketOperatorApiTest():
    def __init__(self):
        super().__init__()

    def Test(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStreamSbe(environment)
        TickerSymbolAdds(tickerStream).AddStableCoins()
        tickerStream.InitConnection()

        thereIsPrice = False
        while not thereIsPrice:
            thereIsPrice = True
            for symbol in tickerStream.listPrices.keys():
                ask = tickerStream.listPrices[symbol].get("ask")
                if(ask is None or ask == 0):
                    thereIsPrice = False

        marketOperatorApi = MarketOperatorApi(environment)

        order1= {
            "symbol": "USDCUSDT",
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": 6,
            "price": tickerStream.listPrices["USDCUSDT"]["bid"],
            "newClientOrderId": "SellStableCoin"
        }

        order2= {
            "symbol": "USDCUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": 5,
            "price": tickerStream.listPrices["USDCUSDT"]["ask"],
            "newClientOrderId": "BuyStableCoin"
        }

        order3= {
            "symbol": "USDCUSDT",
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": 6,
            "price": tickerStream.listPrices["USDCUSDT"]["bid"],
            "newClientOrderId": "SellStableCoin"
        }

        marketOperatorApi.ExecuteOrder(order1)
        marketOperatorApi.ExecuteOrder(order2)
        marketOperatorApi.ExecuteOrder(order3)
        print("terminooo")