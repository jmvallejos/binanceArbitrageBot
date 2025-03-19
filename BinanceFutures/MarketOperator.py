import requests
import hashlib
import hmac

class MarketOperator():
    API_KEY = 'f3uJfDFZWKwe7hn7gSIAyJI7xC7BmaoVGDuDYmyGNXnRmycLmVWrqlkYfEuicUwJ'
    API_SECRET = 'yFFwhXtBNvib9Jms1lm0ruxLpjL1kUqKwz7mehBgTWOkRRpzX2YtalTJ1rfL30sP'
    URL_BASE = 'https://fapi.binance.com'

    def __init__(self):
        super().__init__()

    def Buy(self, symbol, price, quantity, timeInForce):
        endpoint = '/fapi/v1/order'
        params = {
            'symbol': symbol,
            'side': 'BUY',
            'type': 'LIMIT',
            'quantity': quantity,
            'price': price,
            'timeInForce': timeInForce,
            'timestamp': self.GetServerTime()
        }

        # Crear la firma
        query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
        signature = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        params['signature'] = signature

        # Cabeceras
        headers = {
            'X-MBX-APIKEY': self.API_KEY
        }

        # Hacer la solicitud POST
        response = requests.post(self.BASE_URL + endpoint, headers=headers, params=params)

        # Verificar la respuesta
        if response.status_code == 200:
            print("Orden creada exitosamente:", response.json())
        else:
            print("Error al crear la orden:", response.json())
            
    def Sell(self, symbol):
        a = 1

    def GetSymbolBalance(self, symbol):
        return 100.00
    
    def GetServerTime(self):
        endpoint = '/fapi/v1/time'
        response = requests.get(self.URL_BASE + endpoint)
        if response.status_code == 200:
            return response.json()['serverTime']
        else:
            print("Error al obtener el tiempo del servidor:", response.json())
            return None
