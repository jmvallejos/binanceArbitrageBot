from decimal import Decimal, ROUND_FLOOR

class Arbitrage():
    def __init__(self, environment, binancePrice, byBitPrice, wallet, pair, buyCoin, sellCoin):
        super().__init__()
        self.environment = environment
        self.BinancePrice = binancePrice
        self.ByBitPrice = byBitPrice
        self.Wallet = wallet
        self.Pair = pair
        self.BuyCoin = buyCoin 
        self.SellCoin = sellCoin

    def InitArbitrage(self):
        while True:
            self.Wallet.UpdateWallet()
            self.SetAssetCoins()
            self.SetPrecisionToUse()
            
            if(self.binanceBuyCoin > self.byBitBuyCoin):
                self.IterateProcess(self.BuyBinanceSellByBit)

    def IterateProcess(self, fun):
        operationEnd = False
        while not operationEnd:
            operationEnd = fun()

    def BuyBinanceSellByBit(self):
        if(self.ByBitPrice["bid"] <= self.BinancePrice["ask"]):
            return False
        
        diffTimestamp = self.BinancePrice["timestamp"] - self.ByBitPrice["timestamp"]
        if(-3000 > diffTimestamp or diffTimestamp > 3000 ):
            return False

        quantityBinance = self.RoundNumber(self.binanceBuyCoin / self.BinancePrice["ask"], self.precision)
        quantityByBit = self.RoundNumber(self.byBitSellCoin, self.precision) 
        quantity = quantityByBit
        if(quantityBinance < quantityByBit):
            quantity = quantityBinance

        if(quantity * 5 > self.BinancePrice["askq"] or quantity * 5 > self.ByBitPrice["bidq"]):
            return False

        gain = quantity * Decimal(self.ByBitPrice["bid"]) * Decimal(1 - self.ByBitPrice["commi"]) - quantity * Decimal(self.BinancePrice["ask"]) * Decimal(1 - self.BinancePrice["commi"])   
        
        if(gain < 0.1):
            return
        
        print(gain)


    def SetPrecisionToUse(self):
        precisionBinance = self.BinancePrice["precisionLoteSize"]
        precisionByBit = self.ByBitPrice["precisionLoteSize"]
        self.precision = precisionBinance
        if(precisionByBit < precisionBinance):
            self.precision = precisionByBit

    def SetAssetCoins(self):
        self.binanceBuyCoin = 500#self.Wallet.BinanceWallet[self.BuyCoin]
        self.binanceSellCoin = self.Wallet.BinanceWallet[self.SellCoin]            
        self.byBitBuyCoin = self.Wallet.ByBitWallet[self.BuyCoin]
        self.byBitSellCoin = 0.00565839#self.Wallet.ByBitWallet[self.SellCoin]

    def RoundNumber(self, num, decimales):
        num_decimal = Decimal(str(num))
        # Crear el objeto Decimal para el número de decimales
        redondeo = Decimal('1.' + '0' * decimales)
        num_redondeado = num_decimal.quantize(redondeo, rounding=ROUND_FLOOR)
        return num_redondeado
        

        

            