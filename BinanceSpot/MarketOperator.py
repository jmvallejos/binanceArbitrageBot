import hashlib
import hmac
import json

import requests
from decimal import Decimal, ROUND_FLOOR


class MarketOperator():
    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        
    def DirectOperation(self, pairTriangle):
        orderFirstStep = {
            "symbol": pairTriangle["pair1"],
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": pairTriangle["firstStepDirect"],
            "price": pairTriangle["freezeAsk1"],
            "newClientOrderId": "DirectOperationFirstStep" 
        }

        firstStep = self.ExecuteOrder(orderFirstStep)
        
        if("status" not in firstStep or firstStep["status"]  != "FILLED"):
            self.environment.Log("DirectOperation fallo en el primer paso. No hubo conversiones ni comisiones")
            return {"coinToReProcess": "", "investedCapital": 0.00} #Tested

        orderSecondStep = {
            "symbol": pairTriangle["pair2"],
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": pairTriangle["firstStepDirect"],
            "price": pairTriangle["freezeBid2"],
            "newClientOrderId": "DirectOperationSecondStep"
        }
        secondStep = self.ExecuteOrder(orderSecondStep)
        
        if("status" not in secondStep or secondStep["status"]  != "FILLED"): #TESTED
            self.environment.Log("DirectOperation fallo en el segundo paso") 
            self.environment.Log("Moneda a reprocesar: " + pairTriangle["coin2"])
            totalInvested = pairTriangle["initialCapitalDirect"] + pairTriangle["commiFirstStepDirect"]
            self.environment.Log("Invertido mas comisiones: " + str(totalInvested))
            
            return {"coinToReProcess": pairTriangle["coin2"], 
                    "investedCapital": totalInvested} #TESTED

        orderThirdStep = {
            "symbol": pairTriangle["pair3"],
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": pairTriangle["secondStepDirect"],
            "price": pairTriangle["freezeBid3"],
            "newClientOrderId": "DirectOperationThirdStep"
        }
        thirdStep = self.ExecuteOrder(orderThirdStep)
        
        if("status" not in thirdStep or thirdStep["status"]  != "FILLED"):
            self.environment.Log("DirectOperation fallo en el tercer paso") 
            self.environment.Log("Moneda a reprocesar: " + pairTriangle["coin3"])
            totalInvested = pairTriangle["initialCapitalDirect"] + pairTriangle["commiFirstStepDirect"] + pairTriangle["commiSecondStepDirect"]
            self.environment.Log("Invertido: " + str(totalInvested))

            return {"coinToReProcess": pairTriangle["coin3"], #TESTED
                    "investedCapital": totalInvested}

        totalInvested = pairTriangle["initialCapitalDirect"] + pairTriangle["commiFirstStepDirect"] + pairTriangle["commiSecondStepDirect"] + pairTriangle["commiThirdStepDirect"]
        self.environment.Log("Se completo correctamente el DirectOperation")
        self.environment.Log("Dinero invertido: " + str(totalInvested))
        self.environment.Log("Dinero ganado: " + str(thirdStep["cummulativeQuoteQty"]))
        self.environment.Log("Diferencia: " + str(float(thirdStep["cummulativeQuoteQty"]) - totalInvested))
        
        return {"coinToReProcess": "", "investedCapital": 0.00} #TESTED

    def IndirectOperation(self, pairTriangle):
        orderFirstStep = {
            "symbol": pairTriangle["pair3"],
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": pairTriangle["firstStepIndirect"],
            "price": pairTriangle["freezeAsk3"],
            "newClientOrderId": "IndirectOperationFirstStep" 
        }

        firstStep = self.ExecuteOrder(orderFirstStep)

        if("status" not in firstStep or firstStep["status"]  != "FILLED"):
            self.environment.Log("IndirectOperation fallo en el primer paso. No hubo conversiones ni comisiones")
            return {"coinToReProcess": "", "investedCapital": 0.00} #Tested

        orderSecondStep = {
            "symbol": pairTriangle["pair2"],
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": pairTriangle["secondStepIndirect"],
            "price": pairTriangle["freezeAsk2"],
            "newClientOrderId": "IndirectOperationSecondStep"
        }
        secondStep = self.ExecuteOrder(orderSecondStep)
        if("status" not in secondStep or secondStep["status"]  != "FILLED"):
            self.environment.Log("IndirectOperation fallo en el segundo paso") 
            self.environment.Log("Moneda a reprocesar: " + pairTriangle["coin3"])
            totalInvested = pairTriangle["initialCapitalIndirect"] + pairTriangle["commiFirstStepIndirect"]
            self.environment.Log("Invertido: " + str(totalInvested))

            return {"coinToReProcess": pairTriangle["coin3"], #TESTED
                    "investedCapital": totalInvested}
        
        orderThirdStep = {
            "symbol": pairTriangle["pair1"],
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": pairTriangle["secondStepIndirect"],
            "price": pairTriangle["freezeBid1"],
            "newClientOrderId": "IndirectOperationThirdStep"
        }
        thirdStep = self.ExecuteOrder(orderThirdStep)
        if("status" not in thirdStep or thirdStep["status"]  != "FILLED"):
            self.environment.Log("IndirectOperation fallo en el tercer paso") 
            self.environment.Log("Moneda a reprocesar: " + pairTriangle["coin2"])
            totalInvested = pairTriangle["initialCapitalIndirect"] + pairTriangle["commiFirstStepIndirect"] + pairTriangle["commiSecondStepIndirect"]
            self.environment.Log("Invertido mas comisiones: " + str(totalInvested))

            return {"coinToReProcess": pairTriangle["coin2"], #TESTED
                    "investedCapital": totalInvested}

        totalInvested = pairTriangle["initialCapitalIndirect"] + pairTriangle["commiFirstStepIndirect"] + pairTriangle["commiSecondStepIndirect"] + pairTriangle["commiThirdStepIndirect"]
        self.environment.Log("Se completo correctamente el IndirectOperation")
        self.environment.Log("Dinero invertido: " + str(totalInvested))
        self.environment.Log("Dinero ganado: " + str(thirdStep["cummulativeQuoteQty"]))
        self.environment.Log("Diferencia: " + str(float(thirdStep["cummulativeQuoteQty"]) - totalInvested))


        return {"coinToReProcess": ""} #Tested
    
    def SellToStableCoin(self, symbol, quantity, price, invested, commi):
        order = {
            "symbol": symbol,
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": quantity,
            "price": price,
            "newClientOrderId": "SellToStableCoin"
        }

        response = self.ExecuteOrder(order)
        if("status" not in response or response["status"]  != "FILLED"):
            self.environment.Log("Fallo la conversion al StableCoin")
            self.environment.Log("El capital invertido sigue siendo " + str(invested))
            return {"status": "FAILED"} #TESTED
        
        self.environment.Log("Se vendio al stable coin")
        self.environment.Log("Invertido: " + str(invested + commi))
        self.environment.Log("Ganado: " + str(response["cummulativeQuoteQty"]))
        self.environment.Log("Diferencia: " + str(float(response["cummulativeQuoteQty"]) - (invested + commi)))
        return {"status": "SUCCESS"} #TESTED
    
    def DirectOperationTwoSteps(self, row, initialBalance):
        orderSecondStep = {
            "symbol": row["pair2"],
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": initialBalance,
            "price": row["freezeBid2"],
            "newClientOrderId": "DirectOperationSecondStep"
        }
        secondStep = self.ExecuteOrder(orderSecondStep)
        
        if("status" not in secondStep or secondStep["status"]  != "FILLED"):
            self.environment.Log("DirectTwoStep fallo el primer paso. No hubo conversiones")
            self.environment.Log("El capital invertido sigue siendo " + str(row["investedCapital"]))
            
            return {"coinToReProcess": "", #TESTED
                    "investedCapital": 0,
                    "status": "FAILED"}
        
        orderThirdStep = {
            "symbol": row["pair3"],
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": row["secondStepDirect"],
            "price": row["freezeBid3"],
            "newClientOrderId": "DirectOperationThirdStep"
        }
        thirdStep = self.ExecuteOrder(orderThirdStep)

        if("status" not in thirdStep or thirdStep["status"]  != "FILLED"):
            self.environment.Log("DirectTwoStep fallo el segundo paso")
            self.environment.Log("Moneda a reprocesar: " + row["coin3"])
            totalInvested = row["investedCapital"] + row["commiSecondStepDirect"]
            self.environment.Log("Total invertido: " + str(totalInvested))
            return {"coinToReProcess": row["coin3"], 
                    "investedCapital": totalInvested,
                    "status": "FAILED"} #TESTED
        
        self.environment.Log("DirectTwoStep Se ejecuto correctamente")
        totalInvested = row["investedCapital"] + row["commiSecondStepDirect"] + row["commiThirdStepDirect"] 
        self.environment.Log("Dinero invertido: " + str(totalInvested))
        self.environment.Log("Dinero ganado: " + str(thirdStep["cummulativeQuoteQty"]))
        self.environment.Log("Diferencia: " + str(float(thirdStep["cummulativeQuoteQty"]) - totalInvested))

        return {
            "coinToReProcess": "", 
            "investedCapital": 0,
            "status": "SUCCESS"
        }
    
    def IndirectOperationTwoStep(self, row):
        orderSecondStep = {
            "symbol": row["pair2"],
            "side": "BUY",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": row["secondStepIndirect"],
            "price": row["freezeAsk2"],
            "newClientOrderId": "IndirectOperationSecondStep"
        }
        secondStep = self.ExecuteOrder(orderSecondStep)
        if("status" not in secondStep or secondStep["status"]  != "FILLED"): #TESTED
            self.environment.Log("IndirectTwoStep fallo el primer paso. No hubo conversiones")
            self.environment.Log("El capital invertido sigue siendo " + str(row["investedCapital"]))

            return {"coinToReProcess": "", 
                    "investedCapital": 0,
                    "status": "FAILED"}
        
        orderThirdStep = {
            "symbol": row["pair1"],
            "side": "SELL",
            "type": "LIMIT",
            "timeInForce": "FOK",
            "quantity": row["secondStepIndirect"],
            "price": row["freezeBid1"],
            "newClientOrderId": "IndirectOperationThirdStep"
        }
        thirdStep = self.ExecuteOrder(orderThirdStep)
        if("status" not in thirdStep or thirdStep["status"]  != "FILLED"):
            self.environment.Log("IndirectTwoStep fallo el segundo paso")
            self.environment.Log("Moneda a reprocesar: " + row["coin2"])
            totalInvested = row["investedCapital"] + row["commiSecondStepIndirect"]
            self.environment.Log("Total invertido: " + str(totalInvested))

            return {"coinToReProcess": row["coin2"], #TESTED 
                    "investedCapital": totalInvested,
                    "status": "FAILED"}
        
        self.environment.Log("IndirectTwoStep Se ejecuto correctamente")
        totalInvested = row["investedCapital"] + row["commiSecondStepIndirect"] + row["commiThirdStepIndirect"] 
        self.environment.Log("Dinero invertido: " + str(totalInvested))
        self.environment.Log("Dinero ganado: " + str(thirdStep["cummulativeQuoteQty"]))
        self.environment.Log("Diferencia: " + str(float(thirdStep["cummulativeQuoteQty"]) - totalInvested))
        
        return {
            "coinToReProcess": "", 
            "investedCapital": 0,
            "status": "SUCCESS"
        } #TESTED
    
    def SellToStableCoinMarket(self, symbol, quantity):
        order = {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": quantity,
            "newClientOrderId": "SellToStableCoinMarket"
        }

        self.ExecuteOrder(order) #TESTED
        
        return 

    def ExecuteOrder(self, order):
        endpoint = '/api/v3/order'
        order["timestamp"] = self.environment.GetLongUtcTimeStamp()
        if("price" in order): 
            order["price"] = f"{order["price"]:.8f}".rstrip('0').rstrip('.')
        order["quantity"] = f"{order["quantity"]:.8f}".rstrip('0').rstrip('.')
        query_string = '&'.join([f"{key}={value}" for key, value in order.items()])
        order['signature'] = hmac.new(self.environment.secretKey.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()


        headers = {
            'X-MBX-APIKEY': self.environment.apiKey
        }

        response = requests.post(self.environment.apiUrl + endpoint, headers=headers, params=order)
        data = json.loads(response.text)
        if("status" not in data or data["status"] != "FILLED" and data["status"] != "EXPIRED"):
            print(order)
            print(data)
        return data