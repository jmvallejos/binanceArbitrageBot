import time

class Environment:
    def __init__(self):
        self.offsetTimeInSeconds = 0 #Valor negativo o positivo por si el server tiene desfasada la hora.
        self.binanceApiKey = ''
        self.binanceSecretKey = ''
        self.binanceApiUrl = ''
        self.binanceSocketUrl = ''
        
        self.byBitApiUrl = ''
        self.byBitApiKey = ''
        self.byBitSecretKey = ''
        self.byBitSocketUrl = ''

    def SetProdValues(self):
        self.offsetTimeInSeconds = -355
        self.binanceApiKey = 'f3uJfDFZWKwe7hn7gSIAyJI7xC7BmaoVGDuDYmyGNXnRmycLmVWrqlkYfEuicUwJ'
        self.binanceSecretKey = 'yFFwhXtBNvib9Jms1lm0ruxLpjL1kUqKwz7mehBgTWOkRRpzX2YtalTJ1rfL30sP'
        self.binanceApiUrl = 'https://api.binance.com'
        self.binanceSocketUrl = 'wss://stream.binance.com:9443'
        
        self.byBitApiUrl = "https://api.bybit.com"
        self.byBitSocketUrl = 'wss://stream.bybit.com/v5/public/spot'
        self.byBitSecretKey = 'E0El8K1cumgGiamvYExAiT76bOqvylRbHXsI'
        self.byBitApiKey = 'RS010X20Q93tnV8s8j'

    def GetLongUtcTimeStamp(self):
        return int((time.time() + self.offsetTimeInSeconds) * 1000) 
