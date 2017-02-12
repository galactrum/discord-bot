import requests, json
def rpcdat(method,login,password,params,port):
    try:
        rpcdata = json.dumps({
            "jsonrpc": 1.0,
            "id":"rpctest",
            "method": str(method),
            "params": params,
            "port": port
            })
        req = requests.get('http://127.0.0.1:'+port, data=rpcdata, auth=(login, password), timeout=8)
        return req.json()['result']
    except Exception as e:
        return "Error: "+str(e)
