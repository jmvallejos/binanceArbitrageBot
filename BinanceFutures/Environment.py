import time

class Environment:
    def __init__(self):
        self.offsetTimeInSeconds = 0 #Valor negativo o positivo por si el server tiene desfasada la hora.
        self.apiKey = ''
        self.secretKey = ''
        self.apiUrl = ''
        self.socketUrl = ''

    def SetDevValues(self):
        self.offsetTimeInSeconds = -355
        self.apiKey = '66ce4c3b65c8c56ec419451487f4917bdd4b4db65c39115f8866661bb8330f6a'
        self.secretKey = '77360af99ee84dd1c70cc1378526ab69daaed5fd30f47ac3ce925ad981ecb383'
        self.apiUrl = 'https://testnet.binancefuture.com'
        self.socketUrl = 'wss://stream.binancefuture.com'

    def SetProdValues(self):
        self.offsetTimeInSeconds = -355
        self.apiKey = 'f3uJfDFZWKwe7hn7gSIAyJI7xC7BmaoVGDuDYmyGNXnRmycLmVWrqlkYfEuicUwJ'
        self.secretKey = 'yFFwhXtBNvib9Jms1lm0ruxLpjL1kUqKwz7mehBgTWOkRRpzX2YtalTJ1rfL30sP'
        self.apiUrl = 'https://fapi.binance.com'
        self.socketUrl = 'wss://ws-fapi.binance.com'

    def GetLongUtcTimeStamp(self):
        return int((time.time() + self.offsetTimeInSeconds) * 1000) 
