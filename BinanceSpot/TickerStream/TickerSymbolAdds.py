class TickerSymbolAdds():
    def __init__(self, tickerStream):
        super().__init__()
        self.tickerStream = tickerStream

    def AddSymbols(self):
        self.tickerStream.addTrianglePair("ETHUSDC", "ETHBTC", "BTCUSDC","USDC", "ETH", "BTC", 0.0007125, 0.00075, 0.0071250)
        
        #SOL
        self.tickerStream.addTrianglePair("SOLUSDC","SOLETH", "ETHUSDC","USDC", "SOL","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("SOLUSDC","SOLBTC", "BTCUSDC","USDC", "SOL", "BTC", 0.0007125, 0.00075, 0.0007125 )


        #ADA
        self.tickerStream.addTrianglePair("ADAUSDC","ADAETH", "ETHUSDC","USDC", "ADA","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("ADAUSDC","ADABTC", "BTCUSDC","USDC", "ADA","BTC", 0.0007125, 0.00075, 0.0007125 )


        #DOT
        self.tickerStream.addTrianglePair("DOTUSDC","DOTETH", "ETHUSDC","USDC", "DOT","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("DOTUSDC","DOTBTC", "BTCUSDC","USDC", "DOT","BTC", 0.0007125, 0.00075, 0.0007125 )
        ###################

        #LTC
        self.tickerStream.addTrianglePair("LTCUSDC","LTCETH", "ETHUSDC","USDC", "LTC","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("LTCUSDC","LTCBTC", "BTCUSDC","USDC", "LTC","BTC", 0.0007125, 0.00075, 0.0007125 )


        #AVAX
        self.tickerStream.addTrianglePair("AVAXUSDC","AVAXETH", "ETHUSDC","USDC", "AVAX","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("AVAXUSDC","AVAXBTC", "BTCUSDC","USDC", "AVAX","BTC", 0.0007125, 0.00075, 0.0007125 )

        #LINK
        self.tickerStream.addTrianglePair("LINKUSDC","LINKETH", "ETHUSDC","USDC", "LINK","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("LINKUSDC","LINKBTC", "BTCUSDC","USDC", "LINK","BTC", 0.0007125, 0.00075, 0.0007125 )
        ############

        #XRP
        #self.tickerStream.addTrianglePair("XRPUSDC","XRPETH", "ETHUSDC","USDC", "XRP","ETH", 0.0007125, 0.00075, 0.0007125 )
        #self.tickerStream.addTrianglePair("XRPUSDC","XRPBTC", "BTCUSDC","USDC", "XRP","BTC", 0.0007125, 0.00075, 0.0007125 )

        #DOGE
        self.tickerStream.addTrianglePair("DOGEUSDC","DOGEBTC", "BTCUSDC","USDC", "DOGE","BTC", 0.0007125, 0.00075, 0.0007125 )
    
        #NEAR
        self.tickerStream.addTrianglePair("NEARUSDC","NEARETH", "ETHUSDC","USDC", "NEAR","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("NEARUSDC","NEARBTC", "BTCUSDC","USDC", "NEAR","BTC", 0.0007125, 0.00075, 0.0007125 )

        #POL
        #self.tickerStream.addTrianglePair("POLUSDC","POLETH", "ETHUSDC","USDC", "POL","ETH", 0.0007125, 0.00075, 0.0007125 )
        #self.tickerStream.addTrianglePair("POLUSDC","POLBTC", "BTCUSDC","USDC", "POL","BTC", 0.0007125, 0.00075, 0.0007125 )

        #FILL
        #self.tickerStream.addTrianglePair("FILUSDC","FILETH", "ETHUSDC","USDC", "FIL","ETH", 0.0007125, 0.00075, 0.0007125 )
        self.tickerStream.addTrianglePair("FILUSDC","FILBTC", "BTCUSDC","USDC", "FIL","BTC", 0.0007125, 0.00075, 0.0007125 )
        #######
        
        #UNI
        self.tickerStream.addTrianglePair("UNIUSDC","UNIETH", "ETHUSDC","USDC", "UNI","ETH", 0.0007125, 0.00075, 0.0007125)
        self.tickerStream.addTrianglePair("UNIUSDC","UNIBTC", "BTCUSDC","USDC", "UNI","BTC", 0.0007125, 0.00075, 0.0007125)

        #ATOM
        #self.tickerStream.addTrianglePair("ATOMUSDC","ATOMETH", "ETHUSDC","USDC", "ATOM","ETH", 0.0007125, 0.00075, 0.0007125)
        self.tickerStream.addTrianglePair("ATOMUSDC","ATOMBTC", "BTCUSDC","USDC", "ATOM","BTC", 0.0007125, 0.00075, 0.0007125)
        
        #ALGO
        self.tickerStream.addTrianglePair("ALGOUSDC","ALGOBTC", "BTCUSDC","USDC", "ALGO","BTC", 0.0007125, 0.00075, 0.0007125)

        #AAVE
        self.tickerStream.addTrianglePair("AAVEUSDC","AAVEETH", "ETHUSDC","USDC", "AAVE","ETH", 0.0007125, 0.00075, 0.0007125)
        self.tickerStream.addTrianglePair("AAVEUSDC","AAVEBTC", "BTCUSDC","USDC", "AAVE","BTC", 0.0007125, 0.00075, 0.0007125)

        #CAKE
        self.tickerStream.addTrianglePair("CAKEUSDC","CAKEBTC", "BTCUSDC","USDC", "CAKE","BTC", 0.0007125, 0.00075, 0.0007125)

        #RUNE
        #self.tickerStream.addTrianglePair("RUNEUSDC","RUNEETH", "ETHUSDC","USDC", "RUNE","ETH", 0.0007125, 0.00075, 0.0007125)
        #self.tickerStream.addTrianglePair("RUNEUSDC","RUNEBTC", "BTCUSDC","USDC", "RUNE","BTC", 0.0007125, 0.00075, 0.0007125)
        
        #SAND
        self.tickerStream.addTrianglePair("SANDUSDC","SANDBTC", "BTCUSDC","USDC", "SAND","BTC", 0.0007125, 0.00075, 0.0007125)

    def AddSingleSymbol(self):
        self.tickerStream.addTrianglePair("BTCUSDC", "BTCUSDC", "BTCUSDC","USDC", "ETH", "BTC", 0.0007125, 0.00075, 0.0071250)

    def AddTriangle(self):
        self.tickerStream.addTrianglePair("ETHUSDC", "ETHBTC", "BTCUSDC","USDC", "ETH", "BTC", 0.0007125, 0.00075, 0.0071250)

    def AddStableCoins(self):
        self.tickerStream.addTrianglePair("USDCUSDT", "USDCUSDT", "USDCUSDT","USDC", "USDT", "USDC", 0, 0, 0)