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
        self.listenKey = self.CreteUserListenKey()
        self.WalletSpot = {}
        threading.Thread(target=self.KeepAliveListenKey).start()
        

    def CreteUserListenKey(self):
        url = self.environment.apiUrl + "/api/v3/userDataStream"
        headers = {
            'X-MBX-APIKEY': self.environment.apiKey
        }
        response = requests.post(url, headers=headers)
        return response.json()['listenKey']
    
    def KeepAliveListenKey(self):
        while True:
            time.sleep(30*60)
            url = self.environment.apiUrl + "/api/v3/userDataStream"
            headers = {
                'X-MBX-APIKEY': self.environment.apiKey
            }
            requests.put(url+"?listenKey="+self.listenKey, headers=headers)

    def GetWalletBalance(self):
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

    def run(self):
         self.GetWalletBalance()  # Obtiene el saldo inicial
         threading.Thread(target=self.start_websocket).start()
     
    def start_websocket(self):
         ws_url = self.environment.socketUrl + "/ws/"+ self.listenKey
         ws = websocket.WebSocketApp(ws_url,
                                     on_message=self.on_message,
                                     on_error=self.on_error)
         ws.run_forever()
         self.KeepAliveListenKey()

     
    def on_message(self, ws, message):
         event = json.loads(message)
         if(event["e"] == "balanceUpdate"):
            self.GetWalletBalance()
     
    def on_error(self, ws, error):
         print("Error:", error)

    
    