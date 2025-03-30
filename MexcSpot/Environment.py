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
        self.apiKey = ''
        self.secretKey = ''
        self.apiUrl = ''
        self.socketUrl = ''

    def SetProdValues(self):
        self.offsetTimeInSeconds = -355
        self.apiKey = 'mx0vgl3EtGkseSzvht'
        self.secretKey = '4f7ed86f7d1f40c1acded65a58ca8d73'
        self.apiUrl = 'https://api.mexc.com'
        self.socketUrl = 'wss://wbs-api.mexc.com/ws'

    def GetLongUtcTimeStamp(self):
        return int((time.time() + self.offsetTimeInSeconds) * 1000) 
