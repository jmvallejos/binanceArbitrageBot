import requests
import websocket
import json
import threading
import time
import hmac
import hashlib

class AccountStream:
    def __init__(self, environment):
        self.environment = environment
        self.WalletSpot = {}
        self.LastLogError = 0
        
    def GetWalletBalance(self):
        success = False
        while(not success):
            try:
                self.UpdateWallet()
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
    