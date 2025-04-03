import base64
import datetime
import threading
import time
import requests
import json
import pandas as pd
import simplefix
pd.options.mode.chained_assignment = None 
import socket
import ssl
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from urllib.parse import urlparse
from simplefix import FixMessage

class FixTags:
    BEGIN_STRING = "8"
    BODY_LENGTH = "9"
    CHECKSUM = "10"
    MSG_SEQ_NUM = "34"
    MSG_TYPE = "35"
    SENDER_COMP_ID = "49"
    SENDING_TIME = "52"
    TARGET_COMP_ID = "56"
    TEXT = "58"
    RAW_DATA_LENGTH = "95"
    RAW_DATA = "96"
    ENCRYPT_METHOD = "98"
    HEART_BT_INT = "108"
    TEST_REQ_ID = "112"
    RESET_SEQ_NUM_FLAG = "141"
    USERNAME = "553"
    DROP_COPY_FLAG = "9406"

    RECV_WINDOW = "25000"
    MESSAGE_HANDLING = "25035"
    RESPONSE_MODE = "25036"

    MD_REQUEST_ID = "262"
    MD_SUB_REQUEST_TYPE = "263"
    MD_MARKET_DEPTH = "264"
    MD_AGGREGATE_BOOK = "266"
    MD_NO_RELATED_SYM = "146"
    MD_SYMBOL = "55"
    MD_NO_ENTRY_TYPES = "267"
    MD_ENTRY_TYPE = "269"

class FixMsgTypes:
    HEARTBEAT = "0"
    TEST_REQUEST = "1"
    LOGOUT = "5"
    LOGON = "A"
    REJECT = "3"
    MARKET_DATA = "V"

class TickerStreamFixApi():
    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        self.lastLogErrorCompleteTickSize = 0

        self.url = "tcp+tls://fix-md.binance.com:9000"
        self.sequenceNumber = 0
        self.SOH = "\x01"
        self.senderId = "BOT"
        self.targetId = "SPOT"
        self.api_key = "oPGodiu3ZyAuXYwgxBizXHJE3txGhZ55yrynzyO23rMyof2WKYgdF1GbW4rmoDqD"
        self.fixParser = simplefix.parser.FixParser()

        with open('private_key.pem', 'rb') as f:
            self.private_key = load_pem_private_key(data = f.read(), password = None)

        self.dfPairs = pd.DataFrame(columns=[
            'pair1', 'pair2', 'pair3', 
            'coin1', 'coin2', 'coin3',
            'ask1', 'ask2', 'ask3',
            'askq1', 'askq2', 'askq3',
            'bid1', 'bid2', 'bid3',
            'bid1q', 'bid2q', 'bid3q', 
            'commi1', 'commi2','commi3', 
            'precisionLote1', 'precisionLote2','precisionLote3',
            "ExpectedResult"])
        
    def addTrianglePair(self, pair1, pair2, pair3, coin1, coin2, coin3, 
                        commi1, commi2, commi3):
        
        countRecords = self.dfPairs.shape[0]
        self.dfPairs = pd.concat([self.dfPairs, pd.DataFrame(columns=self.dfPairs.columns)], ignore_index=True)

        self.dfPairs.at[countRecords,"pair1"] = pair1
        self.dfPairs.at[countRecords,"pair2"] = pair2
        self.dfPairs.at[countRecords,"pair3"] = pair3
        self.dfPairs.at[countRecords,"coin1"] = coin1
        self.dfPairs.at[countRecords,"coin2"] = coin2
        self.dfPairs.at[countRecords,"coin3"] = coin3
        self.dfPairs.at[countRecords,"commi1"] = commi1
        self.dfPairs.at[countRecords,"commi2"] = commi2
        self.dfPairs.at[countRecords,"commi3"] = commi3

    def InitConnection(self):
        self.environment.Log("Se inicia el stream de precios")
        self.TryCompletePrecisionLote()
        
        self.url = urlparse(self.url)
        sock = socket.create_connection((self.url.hostname, self.url.port))
        context = ssl.create_default_context()
        self.sock = context.wrap_socket(sock, server_hostname=self.url.hostname)

        self.Logon()

        pairs = pd.Series(self.dfPairs['pair1'].tolist() 
                          + self.dfPairs['pair2'].tolist() 
                          + self.dfPairs['pair3'].tolist()).unique()

        threadPrice = threading.Thread(target=self.ReceiveMessagePrice, daemon=True)
        threadPrice.start()
        self.SubscribeSymbols(pairs) 
        threadPrice.join()


    def Logon(self):
        msg = FixMessage()
        self.BuildHeader(msg, FixMsgTypes.LOGON)
        self.BuildBodyLogon(msg)
        
        threadLogon = threading.Thread(target=self.ReceiveMessageLogon, daemon=True)
        threadLogon.start()
        self.sock.sendall(msg.encode(False))
        threadLogon.join()

        if(not self.connected): self.Logon()
            
    def SubscribeSymbols(self, symbols):
        msg = FixMessage()
        self.BuildHeader(msg, FixMsgTypes.MARKET_DATA)
        self.BuildBodySubscribeSymbols(msg, symbols)
        self.sock.sendall(msg.encode(False))

    def BuildHeader(self,message, messageType):
        message.append_pair(FixTags.BEGIN_STRING, "FIX.4.4", header=True)
        message.append_pair(FixTags.MSG_TYPE, messageType, header=True)
        message.append_pair(FixTags.SENDER_COMP_ID, self.senderId, header=True)
        message.append_pair(FixTags.TARGET_COMP_ID, self.targetId, header=True)
        message.append_pair(FixTags.MSG_SEQ_NUM, self.GetNextsequenceNumber(), header=True)
        message.append_pair(FixTags.SENDING_TIME, self.environment.GetUtcTimeStampFormatted(), header=True)
        message.append_pair(FixTags.RECV_WINDOW, None, header=True)

    def BuildBodyLogon(self, message):
        signed_headers = f"A{self.SOH}{self.senderId}{self.SOH}{self.targetId}{self.SOH}{self.sequenceNumber}{self.SOH}{message.get(FixTags.SENDING_TIME).decode("utf-8")}"
        signature = self.private_key.sign(bytes(signed_headers, "ASCII"))
        signature = base64.b64encode(signature).decode("ASCII")

        message.append_pair(FixTags.ENCRYPT_METHOD, "0", header=False)
        message.append_pair(FixTags.HEART_BT_INT, "30", header=False)
        message.append_data(FixTags.RAW_DATA_LENGTH, FixTags.RAW_DATA, signature, header=False)
        message.append_pair(FixTags.RESET_SEQ_NUM_FLAG, "Y", header=False)
        message.append_pair(FixTags.USERNAME, self.api_key, header=False)
        message.append_pair(FixTags.MESSAGE_HANDLING, "2", header=False)

    def BuildBodySubscribeSymbols(self, message, symbols):
        signed_headers = f"V{self.SOH}{self.senderId}{self.SOH}{self.targetId}{self.SOH}{self.sequenceNumber}{self.SOH}{message.get(FixTags.SENDING_TIME).decode("utf-8")}"
        signature = self.private_key.sign(bytes(signed_headers, "ASCII"))
        signature = base64.b64encode(signature).decode("ASCII")

        message.append_pair(FixTags.MD_REQUEST_ID, "BOOK_TICKER_STREAM", header=False)
        message.append_pair(FixTags.MD_SUB_REQUEST_TYPE, "1", header=False)
        message.append_pair(FixTags.MD_MARKET_DEPTH, "1", header=False)
        message.append_pair(FixTags.MD_AGGREGATE_BOOK, "Y", header=False)
        message.append_pair(FixTags.MD_NO_RELATED_SYM, str(len(symbols)), header=False)
        for symbol in symbols:
            message.append_pair(FixTags.MD_SYMBOL, symbol, header=False)
        message.append_pair(FixTags.MD_NO_ENTRY_TYPES, "2", header=False)
        message.append_pair(FixTags.MD_ENTRY_TYPE, "0", header=False)
        message.append_pair(FixTags.MD_ENTRY_TYPE, "1", header=False)

    def ReceiveMessagePrice(self):
        while True:
            response = self.sock.recv(4096).decode('utf-8')
            if(response == ""): return

            self.fixParser.append_buffer(response)
            fix_message = self.fixParser.get_message()
            symbol = fix_message.get(55).decode()
            timestamp = fix_message.get(52).decode()
            timestamp = datetime.datetime.strptime(timestamp, '%Y%m%d-%H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc).timestamp()
            currentTime = datetime.datetime.now(datetime.timezone.utc).timestamp()
            if(symbol == "BTCUSDC"):
                print(currentTime -  timestamp)
            
    def ReceiveMessageLogon(self):
        while True:
            response = self.sock.recv(4096).decode('utf-8')
            if(response == ''):
                self.connected = False
                continue
            
            self.connected = '35=A' in response
            break
    
    def GetNextsequenceNumber(self):
        self.sequenceNumber += 1
        return str(self.sequenceNumber)

    def TryCompletePrecisionLote(self):
        success = False
        while(not success):
            try:
                self.CompletePrecisionLote()
                success = True
            except:
                success = False
                time.sleep(1)
                current = self.environment.GetLongUtcTimeStamp()
                if(current - self.lastLogErrorCompleteTickSize > 20000):
                    self.environment.Log("Error al intentar setear el lotesize")
                    self.lastLogErrorCompleteTickSize = current

    def CompletePrecisionLote(self):
        url = self.environment.apiUrl
        url += "/api/v3/exchangeInfo?symbols="

        pairs = pd.Series(self.dfPairs['pair1'].tolist() 
                          + self.dfPairs['pair2'].tolist() 
                          + self.dfPairs['pair3'].tolist()).unique()

        url += json.dumps(list(pairs))
        url = url.replace('"', '%22')
        url = url.replace(' ', '')

        data = requests.get(url)
        data = json.loads(data.text)

        for symbol_info in data["symbols"]:
            symbol = symbol_info["symbol"]
            loteSize = symbol_info["filters"][1]["stepSize"]
            loteSize = loteSize.rstrip('0').rstrip('.')
            precision = 0
            if("-" in loteSize):
                precision = int(loteSize.split('-')[1])
            
            if("." in loteSize):
                precision = len(loteSize.split(".")[1])

            self.dfPairs.loc[self.dfPairs['pair1'] == symbol, 'precisionLote1'] = 10 ** precision
            self.dfPairs.loc[self.dfPairs['pair2'] == symbol, 'precisionLote2'] = 10 ** precision
            self.dfPairs.loc[self.dfPairs['pair3'] == symbol, 'precisionLote3'] = 10 ** precision

    