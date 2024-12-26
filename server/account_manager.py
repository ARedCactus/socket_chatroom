import json, os

class AccountManager:
    def __init__(self, filename:str):
        self.__Filename = filename
        self.__accounts = {}
        self.__loadAccounts()

    def __loadAccounts(self):
        if os.path.exists(self.__Filename):
            with open(self.__Filename, "r") as file:
                self.__accounts = json.load(file)

    def __saveAccounts(self):
        with open(self.__Filename, "w") as file:
            json.dump(self.__accounts, file)

    def insertAccount(self, account:str, password:str)->bool:
        if account in self.__accounts:
            return False
        self.__accounts[account] = password
        self.__saveAccounts()
        return True
    
    def deleteAccount(self, account:str):
        if account in self.__accounts:
            del self.__accounts[account]
            self.__saveAccounts()
            return True
        else:
            return False
    
    def queryPassword(self, account:str, password:str)->int:
        if account not in self.__accounts:
            return 0
        if self.__accounts[account] != password:
            return 1
        return 2

    

    