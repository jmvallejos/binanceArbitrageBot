from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.TickerStream import TickerStream
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.TriangularArbitrage import TriangularArbitrage

class BinanceSpotTrader:
    def __init__(self):
        super().__init__()
        
    def Trade(self):
        environment = Environment()
        environment.SetProdValues()

        tickerStream = TickerStream(environment)
        self.AdTrianglePairs(tickerStream)
        tickerStream.InitConnection()

        accountStream = AccountStream(environment)
        accountStream.GetWalletBalance()

        marketOperator = MarketOperator(accountStream.WalletSpot, environment)
        
        thereIsPrice = False
        df = tickerStream.dfPairs
        while(not thereIsPrice):
            thereIsPrice = not (df["ask1"].isnull().any() or df["ask2"].isnull().any() or df["ask3"].isnull().any())

        environment.Log("Se llenaron los precios. Inicio del arbitraje")
        trinagularArbitrage = TriangularArbitrage(environment, tickerStream.dfPairs, marketOperator, accountStream, "USDC", 0.1)
        trinagularArbitrage.InitArbitrage()

    def AdTrianglePairs(self, tickerStream):
        tickerStream.addTrianglePair("ETHUSDC", "ETHBTC", "BTCUSDC","USDC", "ETH", "BTC", 0.0007125, 0.00075, 0.0071250)
        
        #SOL
        tickerStream.addTrianglePair("SOLUSDC","SOLETH", "ETHUSDC","USDC", "SOL","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("SOLUSDC","SOLBTC", "BTCUSDC","USDC", "SOL", "BTC", 0.0007125, 0.00075, 0.0007125 )


        #ADA
        tickerStream.addTrianglePair("ADAUSDC","ADAETH", "ETHUSDC","USDC", "ADA","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("ADAUSDC","ADABTC", "BTCUSDC","USDC", "ADA","BTC", 0.0007125, 0.00075, 0.0007125 )


        #DOT
        tickerStream.addTrianglePair("DOTUSDC","DOTETH", "ETHUSDC","USDC", "DOT","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("DOTUSDC","DOTBTC", "BTCUSDC","USDC", "DOT","BTC", 0.0007125, 0.00075, 0.0007125 )
        ###################

        #LTC
        tickerStream.addTrianglePair("LTCUSDC","LTCETH", "ETHUSDC","USDC", "LTC","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("LTCUSDC","LTCBTC", "BTCUSDC","USDC", "LTC","BTC", 0.0007125, 0.00075, 0.0007125 )


        #AVAX
        tickerStream.addTrianglePair("AVAXUSDC","AVAXETH", "ETHUSDC","USDC", "AVAX","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("AVAXUSDC","AVAXBTC", "BTCUSDC","USDC", "AVAX","BTC", 0.0007125, 0.00075, 0.0007125 )

        #LINK
        tickerStream.addTrianglePair("LINKUSDC","LINKETH", "ETHUSDC","USDC", "LINK","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("LINKUSDC","LINKBTC", "BTCUSDC","USDC", "LINK","BTC", 0.0007125, 0.00075, 0.0007125 )
        ############

        #XRP
        tickerStream.addTrianglePair("XRPUSDC","XRPETH", "ETHUSDC","USDC", "XRP","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("XRPUSDC","XRPBTC", "BTCUSDC","USDC", "XRP","BTC", 0.0007125, 0.00075, 0.0007125 )

        #DOGE
        tickerStream.addTrianglePair("DOGEUSDC","DOGEBTC", "BTCUSDC","USDC", "DOGE","ETH", 0.0007125, 0.00075, 0.0007125 )
       
        #NEAR
        tickerStream.addTrianglePair("NEARUSDC","NEARETH", "ETHUSDC","USDC", "NEAR","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("NEARUSDC","NEARBTC", "BTCUSDC","USDC", "NEAR","BTC", 0.0007125, 0.00075, 0.0007125 )

        #POL
        tickerStream.addTrianglePair("POLUSDC","POLETH", "ETHUSDC","USDC", "POL","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("POLUSDC","POLBTC", "BTCUSDC","USDC", "POL","BTC", 0.0007125, 0.00075, 0.0007125 )

        #FILL
        tickerStream.addTrianglePair("FILUSDC","FILETH", "ETHUSDC","USDC", "FIL","ETH", 0.0007125, 0.00075, 0.0007125 )
        tickerStream.addTrianglePair("FILUSDC","FILBTC", "BTCUSDC","USDC", "FIL","BTC", 0.0007125, 0.00075, 0.0007125 )
        #######
        
        #UNI
        tickerStream.addTrianglePair("UNIUSDC","UNIETH", "ETHUSDC","USDC", "UNI","ETH", 0.0007125, 0.00075, 0.0007125)
        tickerStream.addTrianglePair("UNIUSDC","UNIBTC", "BTCUSDC","USDC", "UNI","BTC", 0.0007125, 0.00075, 0.0007125)

        #ATOM
        tickerStream.addTrianglePair("ATOMUSDC","ATOMETH", "ETHUSDC","USDC", "ATOM","ETH", 0.0007125, 0.00075, 0.0007125)
        tickerStream.addTrianglePair("ATOMUSDC","ATOMBTC", "BTCUSDC","USDC", "ATOM","BTC", 0.0007125, 0.00075, 0.0007125)
        
        #ALGO
        tickerStream.addTrianglePair("ALGOUSDC","ALGOBTC", "BTCUSDC","USDC", "ALGO","BTC", 0.0007125, 0.00075, 0.0007125)

        #AAVE
        tickerStream.addTrianglePair("AAVEUSDC","AAVEETH", "ETHUSDC","USDC", "AAVE","ETH", 0.0007125, 0.00075, 0.0007125)
        tickerStream.addTrianglePair("AAVEUSDC","AAVEBTC", "BTCUSDC","USDC", "AAVE","BTC", 0.0007125, 0.00075, 0.0007125)

        #CAKE
        tickerStream.addTrianglePair("CAKEUSDC","CAKEBTC", "BTCUSDC","USDC", "CAKE","BTC", 0.0007125, 0.00075, 0.0007125)

        #RUNE
        tickerStream.addTrianglePair("RUNEUSDC","RUNEETH", "ETHUSDC","USDC", "RUNE","ETH", 0.0007125, 0.00075, 0.0007125)
        tickerStream.addTrianglePair("RUNEUSDC","RUNEBTC", "BTCUSDC","USDC", "RUNE","BTC", 0.0007125, 0.00075, 0.0007125)
        
        #SAND
        tickerStream.addTrianglePair("SANDUSDC","SANDBTC", "BTCUSDC","USDC", "SAND","BTC", 0.0007125, 0.00075, 0.0007125)
