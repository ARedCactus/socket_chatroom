import re
import socket
import threading
import json

class ClientCore:
    def __init__(self, host="localhost", port=8888):
        self.is_server_disconnect = False
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((host, port))
        except socket.error as e:
            self.is_server_disconnect =True
            print(f"socket connection error: {e}")

    def __extractBraceStrings(self, input_string)->list:
        # 使用正则表达式匹配花括号及其中的内容  
        pattern = r'\{.*?\}'  # .*? 表示尽可能少地匹配内容  
        matches = re.findall(pattern, input_string)
        return matches

    def close(self):
        self.__socket.close()
        self.__socket = None

    def tryLogin(self, account:str, password:str)->int:
        if self.is_server_disconnect: return -2 #服务器断开连接
        try:
            self.__socket.send(json.dumps(
                {"request": "login", "account": account, "password": password}
            ).encode())
            for buffer in self.__extractBraceStrings(self.__socket.recv(1024).decode()):
                obj = json.loads(buffer)
                if "response" not in obj: continue

                if obj["response"] == "login_0":   return 0   #账号不存在
                elif obj["response"] == "login_1": return 1 #密码错误
                elif obj["response"] == "login_2": return 2 #账号已在其他地方登录
                elif obj["response"] == "login_3": return 3 #登录成功
            return -1
        except ConnectionResetError: self.is_server_disconnect = True; return -2
        except Exception: return -1
        
    def tryRegister(self, account:str, password:str)->int:
        if self.is_server_disconnect: return -2 #服务器断开连接
        try:
            self.__socket.send(json.dumps(
                {"request": "register", "account": account, "password": password}
            ).encode())
            for buffer in self.__extractBraceStrings(self.__socket.recv(1024).decode()):
                obj = json.loads(buffer)
                if "response" not in obj: continue

                if obj["response"] == "register_failed":      return 0
                elif obj["response"] == "register_successed": return 1
            return -1
        except ConnectionResetError: self.is_server_disconnect = True; return -2
        except Exception: return -1
        
        
    def subscriberCallBack(self):
        try:
            buffers = self.__socket.recv(1024).decode()
            buffer_ext = self.__extractBraceStrings(buffers)
            return [json.loads(item) for item in buffer_ext]
        except socket.error as e:
            self.is_server_disconnect = True
            return None
        except Exception as e:
            print(f"{e}")
            return json.dumps(
                {"publisher": "system", "log": "unable to receive data"}
            )
        
    def send(self, request:str, subscriber:str=None, msg:str="default_msg"):
        if self.is_server_disconnect: return False
        def send_(socket, subscriber:str, message:str):
            socket.send(json.dumps(
                {"request": request, "subscriber": subscriber, "message": message}
            ).encode())
        threading.Thread(target=send_, args=(self.__socket, subscriber, msg,), daemon=True).start()
        return True