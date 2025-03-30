import datetime

class TriangularArbitrage():
    def __init__(self, dfPairs):
        self.dfPairs = dfPairs
        self.baseCurrencyBalance = 1000

    def InitArbitrage(self):
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
            formatted_time = datetime.datetime.now().strftime("%M:%S.%f")[:-3]
            print(str(formatted_time) + ' '+ str(maxDirectGainRecord["DirectGain"]) + ' ' + maxDirectGainRecord["Pair2"]["s"])

        if(maxIndirectGainRecord["IndirectGain"] >= 0.01 and maxIndirectGainRecord["IndirectGain"] > maxDirectGainRecord["DirectGain"]):
            formatted_time = datetime.datetime.now().strftime("%M:%S.%f")[:-3]
            print(str(formatted_time) + ' '+ str(maxIndirectGainRecord["IndirectGain"]) + ' ' + maxIndirectGainRecord["Pair2"]["s"])


    def CalculateDirectGain(self, row):
        firstStep = self.baseCurrencyBalance * row["Pair1"]["commi"] / row["Pair1"]["a"]
        secondStep = firstStep * row["Pair2"]["commi"] * row["Pair2"]["b"]
        thirdStep = secondStep * row["Pair3"]["commi"] * row["Pair3"]["b"]
        return thirdStep - self.baseCurrencyBalance

    def CalculateIndirectGain(self, row):
        firstStep = self.baseCurrencyBalance * row["Pair3"]["commi"] / row["Pair3"]["a"]
        secondStep = firstStep * row["Pair2"]["commi"] / row["Pair2"]["a"]
        thirdStep = secondStep * row["Pair1"]["commi"] * row["Pair1"]["b"]

        return  thirdStep - self.baseCurrencyBalance