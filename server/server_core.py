import socket, threading, json
import account_manager

class ServerCore:
    def __init__(self, filename:str, host="localhost", port=8888):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((host, port))
        self.__socket.listen(10)
        print("[server] server is running ...")

        self.__stop_event_listener = threading.Event()
        self.__connections = {}
        self.__manager = account_manager.AccountManager(filename=filename)

        def waitForConnection():
            while not self.__stop_event_listener.is_set():
                try:
                    connection, address = self.__socket.accept()
                    print(f"Accepted connection from {address}", connection.getsockname(), connection.fileno())
                    threading.Thread(target=self.__handleRequest, args=(connection,), daemon=True).start()
                except socket.error as e:
                    print("socket error: {e}")

        threading.Thread(target=waitForConnection, daemon=True).start()

        try:
            while not self.__stop_event_listener.is_set():
                pass
        except KeyboardInterrupt:
            print("[server] received ctrl+c, stoping server ...")
            self.__stop_event_listener.set()

    def __broadcast(self, publisher:str="system", subscriber:str=None, message:str="system_message"):
        def sendMsg(account, publisher, subscriber:str=None, message:str="default message"):
            if account in self.__connections:
                self.__connections[account].send(json.dumps(
                    {"publisher": publisher, "subscriber": subscriber, "message": message}
                ).encode())
        
        if subscriber: sendMsg(account=subscriber, publisher=publisher, subscriber=subscriber, message=message); return
        for account in self.__connections: 
            if account != publisher: sendMsg(account=account, publisher=publisher, message=message)
            

    def __destoryConnection(self, connection):
        if connection != None:
            connection.close()
            connection = None

    def __sendConnectionsInfo(self):
        accounts = ["group"]
        for account in self.__connections:
            accounts.append(account)
        for account in  self.__connections:
             self.__connections[account].send(json.dumps(
                {"accounts": accounts}
            ).encode())

    def __handleChat(self, account:str):
        connection = self.__connections[account]
        print("[server] User {} joined in chatroom".format(account))
        self.__broadcast(message=f"User {account} joined in chatroom")

        while not self.__stop_event_listener.is_set():
            try:
                buffer = connection.recv(1024).decode()
                obj = json.loads(buffer)

                if obj["request"] == "logout" or obj["request"] == "offline":
                    break

                elif obj["request"] == "send" and "message" in obj:
                    if "subscriber" not in obj: print("[server] Subscriber Not specified"); continue
                    self.__broadcast(publisher=account, subscriber=obj["subscriber"], message=obj["message"])
                
                else:
                    print("[server] parsing json packet failed")

            except Exception:
                print("[server] unable to receive data __handleChat")
                break
        self.__destoryConnection(connection=connection)
        if account in self.__connections:
            del self.__connections[account]
        self.__sendConnectionsInfo()
        self.__broadcast(message=f"User {account} has leaved the chatroom")
        print("User {} has leaved the chatroom".format(account))

    def __handleRequest(self, connection):
        while not self.__stop_event_listener.is_set():
            try:
                buffer = connection.recv(1024).decode()
                obj = json.loads(buffer)

                if obj["request"] == "register" and "account" in obj and "password" in obj:
                    result = "register_successed" if self.__manager.insertAccount(account=obj["account"], password=obj["password"]) else "register_failed"
                    connection.send(json.dumps(
                        {"response": result}
                    ).encode())

                elif obj["request"] == "offline":
                    break

                elif obj["request"] == "login" and "account" in obj and "password" in obj:
                    result = self.__manager.queryPassword(account=obj["account"], password=obj["password"])
                    if result == 2 and obj["account"] not in self.__connections: result = 3 #密码正确， 且账号未登录
                    connection.send(json.dumps(
                        {"response": "login_{}".format(str(result))}
                    ).encode())
                    if result != 3: continue
                    self.__connections[obj["account"]] = connection
                    self.__sendConnectionsInfo()
                    self.__handleChat(obj["account"])
                    if obj["account"] in self.__connections:
                        del self.__connections[obj["account"]]
                    break

                else:
                    print("[server] parsing json packet failed")

            except Exception:
                print("[server] unable to receive data __handleRequest")
                break
        self.__destoryConnection(connection=connection)
        self.__sendConnectionsInfo()

if __name__ == "__main__":
    server_core = ServerCore(filename="source\\passwords.json", host="localhost", port=8888)