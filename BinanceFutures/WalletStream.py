import requests
import websocket
import json
import threading
import time
import hmac
import hashlib

class WalletStream:
    def __init__(self, environment):
        self.environment = environment
        self.api_key = environment.apiKey
        self.api_secret = environment.secretKey
        self.base_api_url = environment.apiUrl
        self.base_socket_url = environment.socketUrl
        self.listen_key = self.create_user_data_stream()
        self.WalletFuture = {}  

    def create_user_data_stream(self):
        url = self.base_api_url + "/fapi/v1/listenKey"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        response = requests.post(url, headers=headers)
        return response.json()['listenKey']

    def run(self):
        self.get_wallet_balance()  # Obtiene el saldo inicial
        threading.Thread(target=self.start_websocket).start()

    def start_websocket(self):
        ws_url = f"{self.base_socket_url}/ws/{self.listen_key}"
        ws = websocket.WebSocketApp(ws_url,
                                    on_message=self.on_message,
                                    on_error=self.on_error)
        ws.run_forever()

    def on_message(self, ws, message):
        self.get_wallet_balance()

    def on_error(self, ws, error):
        print("Error:", error)

    def get_wallet_balance(self):
        url = self.base_api_url + "/fapi/v2/balance"
        params = {
            'timestamp': self.environment.GetLongUtcTimeStamp()
        }
        
        # Crear la firma
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        signature = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        query_string += '&signature=' + signature  

        headers = {
            'X-MBX-APIKEY': self.api_key
        }

        response = requests.get(url +'?'+ query_string, headers=headers)
        balances = response.json()
        self.WalletFuture = {item['asset']: item['balance'] for item in balances}
        print(self.WalletFuture)