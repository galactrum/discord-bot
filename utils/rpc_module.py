import json, requests

class Rpc:
    @staticmethod
    def __init__(self):
        self.port = "11311"
        self.rpc_user = 'srf2UUR0'
        self.rpc_pass = 'srf2UUR0XomxYkWw'
        self.serverURL = 'http://localhost:' + self.port
        self.headers = {'content-type': 'application/json'}

    def listtransactions(self, params, count):
        payload = json.dumps({"method": "listtransactions", "params": [params, count], "jsonrpc": "2.0"})
        response = requests.get(self.serverURL, headers=self.headers, data=payload,
                                auth=(self.rpc_user, self.rpc_pass))
        return (response.json()['result'])

    def validateaddress(self, params):
        payload = json.dumps({"method": "validateaddress", "params": [params], "jsonrpc": "2.0"})
        response = requests.get(self.serverURL, headers=self.headers, data=payload,
                                auth=(self.rpc_user, self.rpc_pass))
        return (response.json()['result'])

    def withdraw(self, account, address, amount):
        payload = json.dumps({"method": "sendfrom", "params": [account, address, amount], "jsonrpc": "2.0"})
        response = requests.get(self.serverURL, headers=self.headers, data=payload,
                                auth=(self.rpc_user, self.rpc_pass))
        return (response.json()['result'])

    def getaddressesbyaccount(self, account):
        payload = json.dumps({"method": "getaddressesbyaccount", "params": [account], "jsonrpc": "2.0"})
        response = requests.get(self.serverURL, headers=self.headers, data=payload,
                                auth=(self.rpc_user, self.rpc_pass))
        return (response.json()['result'])