import datetime
import time
import numpy as np

class TriangularArbitrage():
    def __init__(self, environment, dfPairs, marketOperator, accountStream, symbolBaseCurrency, gainExpected):
        super().__init__()
        self.environment = environment
        self.dfPairs = dfPairs
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
                
                #initTime = self.environment.GetLongUtcTimeStamp()
                
                self.Arbitrage()
                
                # currentTime = self.environment.GetLongUtcTimeStamp()
                # if(currentTime - self.lastTimeLogTimerArbitrage > 1000):
                #     result = currentTime - initTime
                #     print(result)
                #     self.lastTimeLogTimerArbitrage = currentTime
            except:
                continue

    def Arbitrage(self):
        self.FreezePrice(self.dfPairs)

        self.CalculateDirectGain()
        self.CalculateIndirectGain()

        maxDirectGainIndex = self.dfPairs['gainDirect'].idxmax()
        maxDirectGainRecord = self.dfPairs.loc[maxDirectGainIndex]

        maxIndirectGainIndex = self.dfPairs['gainIndirect'].idxmax()
        maxIndirectGainRecord = self.dfPairs.loc[maxIndirectGainIndex]
        
        self.LogExecutingArbitrage(maxDirectGainRecord["gainDirect"], maxIndirectGainRecord["gainIndirect"])

        self.CalculateDirectGainWithCommission(True, maxDirectGainRecord)
        self.CalculateIndirectGainWithCommission(True, maxIndirectGainRecord)

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

    def CalculateDirectGain(self):
        df = self.dfPairs
        df["firstStepDirect"] = self.Round(self.baseCurrencyBalance / df["freezeAsk1"], df["precisionLote1"])
        df["initialCapitalDirect"] = df["firstStepDirect"] * df["freezeAsk1"]

        self.DirectGainTwoSteps(df, df["firstStepDirect"], df["initialCapitalDirect"])    

    def CalculateIndirectGain(self):
        df = self.dfPairs
        df["firstStepIndirect"] = self.Round(self.baseCurrencyBalance / df["freezeAsk3"], df["precisionLote3"]) 
        df["initialCapitalIndirect"] = df["firstStepIndirect"] * df["freezeAsk3"]

        self.IndirectGainTwoSteps(df, df["firstStepIndirect"], df["initialCapitalDirect"])

    def DirectGainTwoSteps(self, df, firstStep, initialCapital):
        if df.empty:
            return

        df["secondStepDirect"] = self.Round(firstStep, df["precisionLote2"])  * df["freezeBid2"]
        df["secondStepDirect"] = self.Round(df["secondStepDirect"], df["precisionLote3"])  
        df["thirdStepDirect"] = df["secondStepDirect"] * df["freezeBid3"] 

        df["gainDirect"] = df["thirdStepDirect"] - initialCapital 
        
    def IndirectGainTwoSteps(self, df, firstStep, initialCapital):
        if df.empty:
            return
        
        df["secondStepIndirect"] = self.Round(firstStep / df["freezeAsk2"], df["precisionLote2"])         
        df["thirdStepIndirect"] = self.Round(df["secondStepIndirect"], df["precisionLote1"]) * df["freezeBid1"]                
        
        df["gainIndirect"] = df["thirdStepIndirect"] - initialCapital

    def CalculateDirectGainWithCommission(self, isFirstStepCalculated, row):
        row["commiSecondStepDirect"] = row["secondStepDirect"] * row["commi2"] * row["freezeBid3"]  
        row["commiThirdStepDirect"] = row["thirdStepDirect"] * row["commi3"]

        row["gainDirect"] -= (row["commiSecondStepDirect"] + row["commiThirdStepDirect"]) 

        if(isFirstStepCalculated):
            row["commiFirstStepDirect"] = row["firstStepDirect"] * row["commi1"] * row["freezeBid1"]
            row["gainDirect"] -= row["commiFirstStepDirect"]
    
    def CalculateIndirectGainWithCommission(self, isFirstStepCalculated, row):
        row["commiSecondStepIndirect"] = row["secondStepIndirect"] * row["commi2"] * row["freezeBid1"]
        row["commiThirdStepIndirect"] = row["thirdStepIndirect"] * row["commi1"] 

        row["gainIndirect"] -= (row["commiSecondStepIndirect"] + row["commiThirdStepIndirect"])

        if(isFirstStepCalculated):
            row["commiFirstStepIndirect"] = row["firstStepIndirect"] * row["commi3"] * row["freezeBid3"]
            row["gainIndirect"] -= row["commiFirstStepIndirect"] 
        
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
        self.FreezePrice(self.dfPairs)

        successSellStableCoin = self.SellToStableCoin()
        if(successSellStableCoin):
            return True
        
        df = self.dfPairs
        df["investedCapital"] = self.reprocessGain
        dfDirect = df.loc[df['coin2'] == self.coinToReprocess]
        dfIndirect = df.loc[df['coin3'] == self.coinToReprocess]

        self.DirectGainTwoSteps(dfDirect, self.balanceCoinToReprocess, self.reprocessGain)
        self.IndirectGainTwoSteps(dfIndirect, self.balanceCoinToReprocess, self.reprocessGain)
        
        maxDirectGain = -100
        if not dfDirect.empty:    
            maxDirectGainIndex = dfDirect['gainDirect'].idxmax()
            maxDirectGainRecord = dfDirect.loc[maxDirectGainIndex]
            self.CalculateDirectGainWithCommission(False, maxDirectGainRecord)
            maxDirectGain = maxDirectGainRecord["gainDirect"]

        maxIndirectGain = -100
        if not dfIndirect.empty:
            maxIndirectGainIndex = dfIndirect['gainIndirect'].idxmax()
            maxIndirectGainRecord = dfIndirect.loc[maxIndirectGainIndex]
            self.CalculateIndirectGainWithCommission(False, maxIndirectGainRecord)
            maxIndirectGain = maxIndirectGainRecord['gainIndirect']

        self.LogExecutingTwoStepArbitrage(maxDirectGain, maxIndirectGain)

        if(maxDirectGain >= self.gainExpected and maxDirectGain >= maxIndirectGain):
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

        if(maxIndirectGainRecord["gainIndirect"] >= self.gainExpected and maxIndirectGain > maxDirectGain):
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

    def SellToStableCoin(self):
        df = self.dfPairs

        dfDirect = df.loc[df['coin2'] == self.coinToReprocess]
        index = dfDirect.first_valid_index()
        bid = 0
        precisionLoteSize = 0

        if(index is None):
            dfIndirect = df.loc[df['coin3'] == self.coinToReprocess]
            index = dfIndirect.first_valid_index()
            row = df.loc[index]
            bid = row["bid3"]
            precisionLoteSize = row["precisionLote3"]
            symbol = row["pair3"]
        else:
            row = df.loc[index]
            bid = row["bid1"]
            precisionLoteSize = row["precisionLote1"]
            symbol = row["pair1"]

        self.balanceCoinToReprocess = self.Round(self.balanceCoinToReprocess, precisionLoteSize)
        conversion = bid * self.balanceCoinToReprocess
        commi = conversion * row["commi1"]

        if(conversion - commi >= self.reprocessGain + self.gainExpected):
            response = self.marketOperator.SellToStableCoin(symbol, self.balanceCoinToReprocess, bid, self.reprocessGain, commi)
            if(response["status"] == "SUCCESS"):
                return True
        return False
        

    def Round(self, num, decimals):
        return np.floor(num * decimals) / decimals
    
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

    def FreezePrice(self, df):
        df["freezeAsk1"] = df["ask1"]
        df["freezeBid1"] = df["bid1"]
        df["freezeAsk2"] = df["ask2"]
        df["freezeBid2"] = df["bid2"]
        df["freezeAsk3"] = df["ask3"]
        df["freezeBid3"] = df["bid3"]
