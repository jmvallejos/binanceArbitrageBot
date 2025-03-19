class TriangularArbitrage():
    def __init__(self, dfPairs, marketOperator):
        super().__init__()
        self.dfPairs = dfPairs
        self.marketOperator = marketOperator

    def InitArbitrage(self, symbolCurrencyBalance):
        self.baseCurrencyBalance = self.marketOperator.GetSymbolBalance(symbolCurrencyBalance)
        
        while True:
            self.Arbitrage()

    def Arbitrage(self):
        self.dfPairs["DirectGain"] = self.dfPairs.apply(self.CalculateDirectGain, axis = 1)
        self.dfPairs["IndirectGain"] = self.dfPairs.apply(self.CalculateIndirectGain, axis = 1)

        maxDirectGainIndex = self.dfPairs['DirectGain'].idxmax()
        maxDirectGainRecord = self.dfPairs.loc[maxDirectGainIndex]

        maxIndirectGainIndex = self.dfPairs['IndirectGain'].idxmax()
        maxIndirectGainRecord = self.dfPairs.loc[maxIndirectGainIndex]

        if(maxDirectGainRecord["DirectGain"] >= 0.01 and maxDirectGainRecord["DirectGain"] >= maxIndirectGainRecord["IndirectGain"]):
            self.marketOperator.Buy(maxDirectGainRecord["Pair1"])
            self.marketOperator.Sell(maxDirectGainRecord["Pair2"])
            self.marketOperator.Sell(maxDirectGainRecord["Pair3"])
            print(str(maxDirectGainRecord["DirectGain"]) + ' ' + maxDirectGainRecord["Pair2"]["s"] + ' Future')

        if(maxIndirectGainRecord["IndirectGain"] >= 0.01 and maxIndirectGainRecord["IndirectGain"] > maxIndirectGainRecord["DirectGain"]):
            self.marketOperator.Buy(maxIndirectGainRecord["Pair3"])
            self.marketOperator.Buy(maxIndirectGainRecord["Pair2"])
            self.marketOperator.Sell(maxIndirectGainRecord["Pair1"])        
            print(str(maxIndirectGainRecord["IndirectGain"]) + ' ' + maxIndirectGainRecord["Pair2"]["s"] + ' Future')

    def CalculateDirectGain(self, row):
        commissionUsdc = (1-0)
        commission = (1-0.00018)

        firstStep = self.baseCurrencyBalance * commissionUsdc / row["Pair1"]["a"]
        secondStep = firstStep * commission * row["Pair2"]["b"]
        thirdStep = secondStep * commissionUsdc * row["Pair3"]["b"]

        return thirdStep - self.baseCurrencyBalance

    def CalculateIndirectGain(self, row):
        commissionUsdc = (1-0)
        commission = (1-0.00018)

        firstStep = self.baseCurrencyBalance * commissionUsdc / row["Pair3"]["a"]
        secondStep = firstStep * commission / row["Pair2"]["a"]
        thirdStep = secondStep * commissionUsdc * row["Pair1"]["b"]

        return  thirdStep - self.baseCurrencyBalance