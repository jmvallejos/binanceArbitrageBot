import hashlib
import hmac
from pybit.unified_trading import HTTP
import requests


class Wallet():
    def __init__(self, environment, buyCoin, sellCoin):
        super().__init__()
        self.environment = environment
        self.buyCoin = buyCoin
        self.sellCoin = sellCoin
        self.BinanceWallet = {}
        self.ByBitWallet = {}

    def UpdateWallet(self):
        self.UpdateBinanceWallet()
        self.UpdateByBitWallet()    

    def UpdateBinanceWallet(self):
        url = self.environment.binanceApiUrl + "/api/v3/account"
        params = {
            'timestamp': self.environment.GetLongUtcTimeStamp()
        }
        
        # Crear la firma
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        signature = hmac.new(self.environment.binanceSecretKey.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        query_string += '&signature=' + signature  

        headers = {
            'X-MBX-APIKEY': self.environment.binanceApiKey
        }

        response = requests.get(url +'?'+ query_string, headers=headers)
        balances = response.json()["balances"]
        self.BinanceWallet = {balance['asset']: float(balance['free']) for balance in balances}

    def UpdateByBitWallet(self):
        url = self.environment.byBitApiUrl + "/v5/asset/transfer/query-account-coins-balance"
        params= 'accountType=UNIFIED&coin='+self.buyCoin+','+self.sellCoin
        timestamp = self.environment.GetLongUtcTimeStamp()
        signature = self.genByBitSignature(params, timestamp)

        headers = {
            'X-BAPI-SIGN': signature,
            'X-BAPI-API-KEY': self.environment.byBitApiKey,
            'X-BAPI-TIMESTAMP': str(timestamp),
            'X-BAPI-RECV-WINDOW': '5000',
            'X-BAPI-SIGN-TYPE': '2'
        }

        response = requests.get(url +"?"+ params, headers=headers)
        balances = response.json()["result"]["balance"]
        self.ByBitWallet = {balance['coin']: float(balance['transferBalance']) for balance in balances}

    def genByBitSignature(self, payload, timestamp):
        param_str= str(timestamp) + self.environment.byBitApiKey + '5000' + payload
        hash = hmac.new(bytes(self.environment.byBitSecretKey, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
        signature = hash.hexdigest()
        return signature