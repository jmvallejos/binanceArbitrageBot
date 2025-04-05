import datetime
import math
import time
import numpy as np

class TriangularArbitrage():
    def __init__(self, environment, triangularPairs, listPrices, marketOperator, accountStream, symbolBaseCurrency, gainExpected):
        super().__init__()
        self.environment = environment
        self.triangularPairs = triangularPairs
        self.listPrices = listPrices
        self.marketOperator = marketOperator
        self.accountStream = accountStream
        self.symbolBaseCurrency = symbolBaseCurrency
        self.gainExpected = gainExpected
        self.baseCurrencyBalance = 0
        self.lastLogPriceNotWorking = 0
        self.lastLogExecutingArbitrage = 0
        self.lastLogExecutingTwoStepArbitrage = 0
        self.lastTimeLogTimerArbitrage = 0

    def InitArbitrage(self):
        self.accountStream.GetWalletBalance()
        self.baseCurrencyBalance = self.accountStream.WalletSpot[self.symbolBaseCurrency]

        while True:
            try:
                if(not self.CheckPriceStreamIsWorking()):
                    continue
                
                initTime = time.time()
                self.Arbitrage()
                print(f"{(time.time() - initTime):.8f}")
                
            except:
                continue

    def Arbitrage(self):
        for triangular in self.triangularPairs:    
            self.FreezePrice(triangular)
            self.CalculateDirectGain(triangular)
            self.CalculateIndirectGain(triangular)
        
        maxDirectGainRecord = max(self.triangularPairs, key=lambda x: x['gainDirect'])
        maxIndirectGainRecord = max(self.triangularPairs, key=lambda x: x['gainIndirect'])
        
        self.LogExecutingArbitrage(maxDirectGainRecord["gainDirect"], maxIndirectGainRecord["gainIndirect"])

        self.CalculateDirectGainWithCommission(maxDirectGainRecord)
        self.CalculateIndirectGainWithCommission(maxIndirectGainRecord)

        if(maxDirectGainRecord["gainDirect"] >= self.gainExpected and maxDirectGainRecord["gainDirect"] >= maxIndirectGainRecord["gainIndirect"]):
            response = self.marketOperator.DirectOperation(maxDirectGainRecord)
            if(response["coinToReProcess"] != ""):
                self.coinToReprocess = response["coinToReProcess"]
                self.reprocessGain = response["investedCapital"] 
                self.ReprocessCoin()
            
            self.accountStream.GetWalletBalance()
            self.baseCurrencyBalance = self.accountStream.WalletSpot[self.symbolBaseCurrency]
            self.environment.Log("En cartera tras operation: " + str(self.baseCurrencyBalance))   
            return

        if(maxIndirectGainRecord["gainIndirect"] >= self.gainExpected and maxIndirectGainRecord["gainIndirect"] > maxDirectGainRecord["gainDirect"]):
            response = self.marketOperator.IndirectOperation(maxIndirectGainRecord)
            if(response["coinToReProcess"] != ""):
                self.coinToReprocess = response["coinToReProcess"]
                self.reprocessGain = response["investedCapital"] 
                self.ReprocessCoin()
            
            self.accountStream.GetWalletBalance()
            self.baseCurrencyBalance = self.accountStream.WalletSpot[self.symbolBaseCurrency]
            self.environment.Log("En cartera tras operation: " + str(self.baseCurrencyBalance))   
            return

    def CalculateDirectGain(self, tr):
        tr["firstStepDirect"] = self.Round(self.baseCurrencyBalance / tr["ask1"], tr["precisionLote1"])
        tr["initialCapitalDirect"] = tr["firstStepDirect"] * tr["ask1"]

        tr["secondStepDirect"] = self.Round(tr["firstStepDirect"], tr["precisionLote2"])  * tr["bid2"]
        tr["secondStepDirect"] = self.Round(tr["secondStepDirect"], tr["precisionLote3"])  
        tr["thirdStepDirect"] = tr["secondStepDirect"] * tr["bid3"] 

        tr["gainDirect"] = tr["thirdStepDirect"] - tr["initialCapitalDirect"]    

    def CalculateIndirectGain(self, tr):
        tr["firstStepIndirect"] = self.Round(self.baseCurrencyBalance / tr["ask3"], tr["precisionLote3"]) 
        tr["initialCapitalIndirect"] = tr["firstStepIndirect"] * tr["ask3"]

        tr["secondStepIndirect"] = self.Round(tr["firstStepIndirect"] / tr["ask2"], tr["precisionLote2"])         
        tr["thirdStepIndirect"] = self.Round(tr["secondStepIndirect"], tr["precisionLote1"]) * tr["bid1"]                
        
        tr["gainIndirect"] = tr["thirdStepIndirect"] - tr["initialCapitalDirect"]

    def CalculateDirectGainWithCommission(self, row):
        row["commiFirstStepDirect"] = row["firstStepDirect"] * row["commi1"] * row["bid1"]
        row["commiSecondStepDirect"] = row["secondStepDirect"] * row["commi2"] * row["bid3"]  
        row["commiThirdStepDirect"] = row["thirdStepDirect"] * row["commi3"]

        row["gainDirect"] -= (row["commiFirstStepDirect"] + row["commiSecondStepDirect"] + row["commiThirdStepDirect"]) 
    
    def CalculateIndirectGainWithCommission(self, row):
        row["commiFirstStepIndirect"] = row["firstStepIndirect"] * row["commi3"] * row["bid3"]
        row["commiSecondStepIndirect"] = row["secondStepIndirect"] * row["commi2"] * row["bid1"]
        row["commiThirdStepIndirect"] = row["thirdStepIndirect"] * row["commi1"] 

        row["gainIndirect"] -= (row["commiFirstStepIndirect"] + row["commiSecondStepIndirect"] + row["commiThirdStepIndirect"])
        
    def ReprocessCoin(self):
        reprocessEnd = False
        self.accountStream.GetWalletBalance(self.coinToReprocess)
        self.reprocessGain -= self.accountStream.diffAmountAfterConversions
        self.balanceCoinToReprocess = self.accountStream.WalletSpot[self.coinToReprocess]

        while(not reprocessEnd):
            try:
                if(not self.CheckPriceStreamIsWorking()):
                    continue

                reprocessEnd = self.CalculateReprocess()
            except:
                reprocessEnd = False

    def CalculateReprocess(self):
        for triangular in self.triangularPairs:
            self.FreezePrice(triangular)

        successSellStableCoin = self.SellToStableCoin()
        if(successSellStableCoin):
            return True

        for triangular in self.triangularPairs:
            self.DirectGainTwoSteps(triangular)
            self.IndirectGainTwoSteps(triangular)    
          
        maxDirectGainRecord = max(self.triangularPairs, key=lambda x: x['gainDirect'])
        maxIndirectGainRecord = max(self.triangularPairs, key=lambda x: x['gainIndirect'])
        
        self.CalculateDirectGainWithCommissionTwoSteps(maxDirectGainRecord)
        self.CalculateIndirectGainWithCommissionTwoSteps(maxIndirectGainRecord)
        
        self.LogExecutingTwoStepArbitrage(maxDirectGainRecord["gainDirect"], maxIndirectGainRecord['gainIndirect'])

        if(maxDirectGainRecord["gainDirect"] >= self.gainExpected and maxDirectGainRecord["gainDirect"] >= maxIndirectGainRecord['gainIndirect']):
            self.balanceCoinToReprocess = self.Round(self.balanceCoinToReprocess, maxDirectGainRecord["precisionLote2"])
            response = self.marketOperator.DirectOperationTwoSteps(maxDirectGainRecord, self.balanceCoinToReprocess)
            if(response["status"] == "SUCCESS"):
                return True

            if(response["coinToReProcess"] == ""):
                return False

            self.coinToReprocess = response["coinToReProcess"]
            self.reprocessGain = response["investedCapital"]
            self.accountStream.GetWalletBalance(self.coinToReprocess)
            self.reprocessGain -= self.accountStream.diffAmountAfterConversions
            self.balanceCoinToReprocess = self.accountStream.WalletSpot[self.coinToReprocess] 

            return False

        if(maxIndirectGainRecord["gainIndirect"] >= self.gainExpected and maxIndirectGainRecord["gainIndirect"] > maxDirectGainRecord["gainDirect"]):
            self.balanceCoinToReprocess = self.Round(self.balanceCoinToReprocess, maxIndirectGainRecord["precisionLote3"])
            response = self.marketOperator.IndirectOperationTwoStep(maxIndirectGainRecord)
            if(response["status"] == "SUCCESS"):
                return True

            if(response["coinToReProcess"] == ""):
                return False
            
            self.coinToReprocess = response["coinToReProcess"]
            self.reprocessGain = response["investedCapital"]
            self.accountStream.GetWalletBalance(self.coinToReprocess)
            self.reprocessGain -= self.accountStream.diffAmountAfterConversions
            self.balanceCoinToReprocess = self.accountStream.WalletSpot[self.coinToReprocess] 
            
            return False

    def DirectGainTwoSteps(self, tr):
        tr["secondStepDirect"] = self.Round(self.balanceCoinToReprocess, tr["precisionLote2"])  * tr["bid2"]
        tr["secondStepDirect"] = self.Round(tr["secondStepDirect"], tr["precisionLote3"])  
        tr["thirdStepDirect"] = tr["secondStepDirect"] * tr["bid3"] 

        tr["gainDirect"] = tr["thirdStepDirect"] - self.reprocessGain 
        
    def IndirectGainTwoSteps(self, tr):
        tr["secondStepIndirect"] = self.Round(self.balanceCoinToReprocess / tr["ask2"], tr["precisionLote2"])         
        tr["thirdStepIndirect"] = self.Round(tr["secondStepIndirect"], tr["precisionLote1"]) * tr["bid1"]                
        
        tr["gainIndirect"] = tr["thirdStepIndirect"] - self.reprocessGain

    def CalculateDirectGainWithCommissionTwoSteps(self, row):
        row["commiSecondStepDirect"] = row["secondStepDirect"] * row["commi2"] * row["bid3"]  
        row["commiThirdStepDirect"] = row["thirdStepDirect"] * row["commi3"]

        row["gainDirect"] -= (row["commiSecondStepDirect"] + row["commiThirdStepDirect"]) 
    
    def CalculateIndirectGainWithCommissionTwoSteps(self, row):
        row["commiSecondStepIndirect"] = row["secondStepIndirect"] * row["commi2"] * row["bid1"]
        row["commiThirdStepIndirect"] = row["thirdStepIndirect"] * row["commi1"] 

        row["gainIndirect"] -= (row["commiSecondStepIndirect"] + row["commiThirdStepIndirect"])


    def SellToStableCoin(self):
        symbol = ""
        precisionLoteSize = 0
        bid = 0

        direct = next((tr for tr in self.triangularPairs if tr['coin2'] == self.coinToReprocess), None)
        if(direct is None):
            indirect = next((tr for tr in self.triangularPairs if tr['coin3'] == self.coinToReprocess), None)
            symbol = indirect["pair3"]
            bid = indirect["bid3"]
            precisionLoteSize = indirect["precisionLote3"]
            commi = indirect["commi3"]
        else:
            symbol = direct["pair1"]
            bid = direct["bid1"]
            precisionLoteSize = direct["precisionLote1"]
            commi = direct["commi1"]

        self.balanceCoinToReprocess = self.Round(self.balanceCoinToReprocess, precisionLoteSize)
        conversion = bid * self.balanceCoinToReprocess
        commi = conversion * commi

        if(conversion - commi >= self.reprocessGain + self.gainExpected):
            response = self.marketOperator.SellToStableCoin(symbol, self.balanceCoinToReprocess, bid, self.reprocessGain, commi)
            if(response["status"] == "SUCCESS"):
                return True
        return False 

    def Round(self, num, decimals):
        return math.floor(num * decimals) / decimals
    
    def CheckPriceStreamIsWorking(self):
        priceIsWorking = self.environment.PriceStreamIsWorking()
        if(not priceIsWorking):
            currentTime = self.environment.GetLongUtcTimeStamp()
            if(currentTime - self.lastLogPriceNotWorking > 30000):
                self.environment.Log("El stream de precios no esta funcionando")
                self.lastLogPriceNotWorking = currentTime
            return False
        return True
        
    def LogExecutingArbitrage(self, directGain, indirectGain):
        currentTime = self.environment.GetLongUtcTimeStamp()
        if(currentTime - self.lastLogExecutingArbitrage > 30000):
                self.environment.Log("Ejecutando arbitraje " + str(directGain) + ' ' + str(indirectGain))
                self.environment.Log("CoinBaseAmount: "+ str(self.baseCurrencyBalance))
                self.lastLogExecutingArbitrage = currentTime

    def LogExecutingTwoStepArbitrage(self, directGain, indirectGain):
        currentTime = self.environment.GetLongUtcTimeStamp()
        if(currentTime - self.lastLogExecutingTwoStepArbitrage > 30000):
                self.environment.Log("Ejecutando arbitraje two step " + str(directGain) + ' ' + str(indirectGain))
                self.environment.Log("Coin arbitrando: "+ self.coinToReprocess + " " + str(self.balanceCoinToReprocess))
                self.environment.Log("Invertido: " + str(self.reprocessGain))
                self.lastLogExecutingTwoStepArbitrage = currentTime

    def FreezePrice(self, triangular):
        triangular["ask1"] = self.listPrices[triangular["pair1"]]["ask"]
        triangular["bid1"] = self.listPrices[triangular["pair1"]]["bid"]
        triangular["ask2"] = self.listPrices[triangular["pair2"]]["ask"]
        triangular["bid2"] = self.listPrices[triangular["pair2"]]["bid"]
        triangular["ask3"] = self.listPrices[triangular["pair3"]]["ask"]
        triangular["bid3"] = self.listPrices[triangular["pair3"]]["bid"]