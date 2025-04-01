import base64
import datetime
import threading
import time
import requests
import websocket
import json
import pandas as pd
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

class FixMsgTypes:
    HEARTBEAT = "0"
    TEST_REQUEST = "1"
    LOGOUT = "5"
    LOGON = "A"
    REJECT = "3"

_SOH_ = "\x01"

class TickerStream():
    def __init__(self, environment):
        super().__init__()
        self.environment = environment
        self.lastLogErrorCompleteTickSize = 0
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
        
        self.connected = False

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

        self.endpoint = "tcp+tls://fix-md.binance.com:9000"
        self.fix_version = "FIX.4.4"
        self.msg_type = ""
        self.sender_comp_id = "TEST"
        self.target_comp_id = "SPOT"
        self.encrypt_method = 0
        self.heart_bt_int = 30
        self.reset_seq_num_flag = "Y"
        self.api_key = "oPGodiu3ZyAuXYwgxBizXHJE3txGhZ55yrynzyO23rMyof2WKYgdF1GbW4rmoDqD"
        self.message_handling = 2
        self.response_mode = None
        self.drop_copy_flag = None
        self.messages_sent: list[FixMessage] = []

        self.lock = threading.Lock()


        url = urlparse(self.endpoint)
        sock = socket.create_connection((url.hostname, url.port))
        context = ssl.create_default_context()
        self.sock = context.wrap_socket(sock, server_hostname=url.hostname)
        self.is_connected = True

        self.msg_seq_num = 0

        msg = FixMessage()
        msg.append_pair(FixTags.BEGIN_STRING, self.fix_version, header=True)
        msg.append_pair(FixTags.MSG_TYPE, FixMsgTypes.LOGON, header=True)
        msg.append_pair(FixTags.SENDER_COMP_ID, self.sender_comp_id, header=True)
        msg.append_pair(FixTags.TARGET_COMP_ID, self.target_comp_id, header=True)
        msg.append_pair(FixTags.MSG_SEQ_NUM, self.get_next_seq_num(), header=True)
        msg.append_pair(FixTags.SENDING_TIME, self.current_utc_time(), header=True)
        msg.append_pair(FixTags.RECV_WINDOW, None, header=True)

        with open('private_key.pem', 'rb') as f:
            private_key = load_pem_private_key(data = f.read(), password = None)

        signed_headers = f"A{_SOH_}{self.sender_comp_id}{_SOH_}{self.target_comp_id}{_SOH_}{self.msg_seq_num}{_SOH_}{msg.get(FixTags.SENDING_TIME).decode("utf-8")}"
        signature = private_key.sign(bytes(signed_headers, "ASCII"))
        signature = base64.b64encode(signature).decode("ASCII")

        msg.append_pair(FixTags.ENCRYPT_METHOD, self.encrypt_method, header=False)
        msg.append_pair(FixTags.HEART_BT_INT, self.heart_bt_int, header=False)
        msg.append_data(FixTags.RAW_DATA_LENGTH, FixTags.RAW_DATA, signature, header=False)
        msg.append_pair(FixTags.RESET_SEQ_NUM_FLAG, self.reset_seq_num_flag, header=False)
        msg.append_pair(FixTags.USERNAME, self.api_key, header=False)
        msg.append_pair(FixTags.MESSAGE_HANDLING, self.message_handling, header=False)
        msg.append_pair(FixTags.RESPONSE_MODE, self.response_mode, header=False)
        msg.append_pair(FixTags.DROP_COPY_FLAG, self.drop_copy_flag, header=False)

        with self.lock:  # save the logon message for future auto_reconnects
            self.messages_sent.append(msg)

        if not self.sock:
            self.logger.error("Error: No connection established. can't send message.")
            return
        
        threadLogon = threading.Thread(target=self.ReceiveMessageLogon, daemon=True)
        threadLogon.start()
        self.sock.sendall(msg.encode(False))
        threadLogon.join()

        if(not self.connected):
            self.InitConnection()
            return
        
        msg = FixMessage()
        msg.append_pair(FixTags.BEGIN_STRING, self.fix_version, header=True)
        msg.append_pair(FixTags.MSG_TYPE, "V", header=True)
        msg.append_pair(FixTags.SENDER_COMP_ID, self.sender_comp_id, header=True)
        msg.append_pair(FixTags.TARGET_COMP_ID, self.target_comp_id, header=True)
        msg.append_pair(FixTags.MSG_SEQ_NUM, self.get_next_seq_num(), header=True)
        msg.append_pair(FixTags.SENDING_TIME, self.current_utc_time(), header=True)
        msg.append_pair(FixTags.RECV_WINDOW, None, header=True)

        msg.append_pair(262, "BOOK_TICKER_STREAM")
        msg.append_pair(263, 1)
        msg.append_pair(264, 1)
        msg.append_pair(266, "Y")
        msg.append_pair(146, 1)
        msg.append_pair(55, "BTCUSDC")
        msg.append_pair(267, 2)
        msg.append_pair(269, 0)
        msg.append_pair(269, 1) 


        threadPrice = threading.Thread(target=self.ReceiveMessagePrice, daemon=True)
        self.sock.sendall(msg.encode(False))
        threadPrice.start()




    def ReceiveMessageLogon(self):
        while True:
            response = self.sock.recv(4096).decode('utf-8')
            if(response == ''):
                return
            
            self.connected = '35=A' in response
            break
    
    def ReceiveMessagePrice(self):
        while True:
            try:
                response = self.sock.recv(4096).decode('utf-8')
                if(response == ""): return

                msg = response if response.startswith(_SOH_) else f"{_SOH_}{response}"
                raw_messages = [f"8={x}" for x in msg.split(f"{_SOH_}8=") if x]
                messages: list[FixMessage] = []

                for i in range(len(raw_messages)):
                    tag_values = [x for x in raw_messages[i].split(_SOH_) if x != ""]
                    if tag_values[-1].startswith("10="):
                        fix_msg = FixMessage()
                        fix_msg.append_strings(tag_values)
                        symbol = fix_msg.get(55)
                        bid = fix_msg.get(270,1)
                        bidq = fix_msg.get(271,1)
                        ask = fix_msg.get(270,2)
                        askq = fix_msg.get(271,2)
                        
                        print(f"{bid}")
            except:
                continue


            
                    
            


    def get_next_seq_num(self) -> str:
        with self.lock:
            self.msg_seq_num += 1
            return str(self.msg_seq_num)
        
    def current_utc_time(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H:%M:%S.%f")


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

    