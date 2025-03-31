import math
import requests
import websocket
import json
import threading
import time
import hmac
import hashlib

class AccountStream:
    def __init__(self, environment, stableCoin, marketOperator):
        self.environment = environment
        self.WalletSpot = {}
        self.LastLogError = 0
        self.StableCoin = stableCoin
        self.marketOperator = marketOperator
        self.diffAmountAfterConversions = 0
        
    def GetWalletBalance(self, arbitrageCoin = ""):
        success = False
        while(not success):
            try:
                self.UpdateWallet()
                self.FixBalances(arbitrageCoin)
                success = True
            except:
                success = False
                time.sleep(1)
                current = self.environment.GetLongUtcTimeStamp()
                if(current - self.LastLogError > 20000):
                    self.environment.Log("Error al intentar actualizar la billetera")
                    self.LastLogError = current

    def UpdateWallet(self):
        url = self.environment.apiUrl + "/api/v3/account"
        params = {
            'timestamp': self.environment.GetLongUtcTimeStamp()
        }
        
        # Crear la firma
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        signature = hmac.new(self.environment.secretKey.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        query_string += '&signature=' + signature  

        headers = {
            'X-MBX-APIKEY': self.environment.apiKey
        }

        response = requests.get(url +'?'+ query_string, headers=headers)
        balances = response.json()["balances"]
        self.WalletSpot = {balance['asset']: float(balance['free']) for balance in balances}

    def FixBalances(self, arbitrageCoin):
        balanceStableCoin = self.WalletSpot[self.StableCoin]

        coinsWithBalance = {key: value for key, value in self.WalletSpot.items() 
                            if value > 0 and key != self.StableCoin and key != arbitrageCoin and key != "BNB"}
        
        for coin in coinsWithBalance:    
            self.SellSurplusToMarket(coin)
            self.ConvertSurplus(coin)

        self.diffAmountAfterConversions = self.WalletSpot[self.StableCoin] - balanceStableCoin  

    def SellSurplusToMarket(self, coin):
        try:
            symbol = coin + self.StableCoin
            url = self.environment.apiUrl
            url += "/api/v3/exchangeInfo?symbol=" + symbol
            data = requests.get(url)
            data = json.loads(data.text)
            balanceCoin = self.WalletSpot[coin]
            
            loteSize = data["symbols"][0]["filters"][1]["stepSize"]
            loteSize = loteSize.rstrip('0').rstrip('.')
            precision = 0
            if("." in loteSize):
                    precision = len(loteSize.split(".")[1])
            
            precision = 10 ** precision

            quantityToSell = math.floor(balanceCoin * precision) / precision
             
            if(quantityToSell == 0):
                return

            self.marketOperator.SellToStableCoinMarket(symbol, quantityToSell)
            
            self.UpdateWallet()
        except:
            self.UpdateWallet()
            return

    def ConvertSurplus(self, coin):
        balanceCoin = self.WalletSpot[coin]
        if(balanceCoin == 0):
            return
        
        url = self.environment.apiUrl + "/sapi/v1/convert/getQuote"

        params = {
            'fromAsset': coin,
            'toAsset': self.StableCoin,
            'fromAmount': f"{balanceCoin:.8f}".rstrip('0').rstrip('.'),
            'timestamp': self.environment.GetLongUtcTimeStamp()
        }
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        params['signature'] = hmac.new(self.environment.secretKey.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

        headers = {
            'X-MBX-APIKEY': self.environment.apiKey
        }

        response = requests.post(url, headers=headers, params=params)
        quoteId = json.loads(response.text)["quoteId"]

        url = self.environment.apiUrl + "/sapi/v1/convert/acceptQuote"
        params = {
            'quoteId': quoteId,
            'timestamp': self.environment.GetLongUtcTimeStamp()
        }
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        params['signature'] = hmac.new(self.environment.secretKey.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

        response = requests.post(url, headers=headers, params=params)
        data = json.loads(response.text)

        self.UpdateWallet()


    