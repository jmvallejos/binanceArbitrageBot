from BinanceByBit.Arbitrage import Arbitrage
from BinanceByBit.Environment import Environment
from BinanceByBit.StreamPrices import StreamPrices
from BinanceByBit.Wallet import Wallet


class BinanceByBitTrader():
    def __init__(self):
        super().__init__()

    def Trade(self):
        #Iniciar el stream de precios.
        environment = Environment()
        environment.SetProdValues()

        streamPrices = StreamPrices(environment)

        pair = "BTCUSDC"
        buyCoin = "USDC"
        sellCoin = "BTC"

        streamPrices.SetBinancePair(pair, buyCoin, sellCoin, 0.0007125)
        streamPrices.SetByBit(pair, buyCoin, sellCoin, 0.001)
        streamPrices.InitStream()

        while(streamPrices.BinancePrice["ask"] == 0 or streamPrices.ByBitPrice["ask"]):
            a = 1

        wallet = Wallet(environment, buyCoin, sellCoin)        
        arbitrage = Arbitrage(environment, streamPrices.BinancePrice, streamPrices.ByBitPrice, wallet, pair, buyCoin, sellCoin)
        arbitrage.InitArbitrage()

        