import pymysql.cursors, sys, json, requests
from utils import parsing


class Walletnotify:
    def __init__(self):
        self.txid = txid
        self.config = parsing.parse_json('walletnotify.json')
        ##MySQL
        self.config_mysql = self.config["mysql"]
        self.host = self.config_mysql["db_host"]
        try:
            self.port = int(self.config_mysql["db_port"])
        except KeyError:
            self.port = 3306
        self.db_user = self.config_mysql["db_user"]
        self.db_pass = self.config_mysql["db_pass"]
        self.db = self.config_mysql["db"]
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.db_user,
            password=self.db_pass,
            db=self.db)
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        ##RPC
        self.config_rpc = self.config["rpc"]
        self.rpc_host = self.config_rpc["rpc_host"]
        self.rpc_port = self.config_rpc["rpc_port"]
        self.rpc_user = self.config_rpc["rpc_user"]
        self.rpc_pass = self.config_rpc["rpc_pass"]
        self.serverURL = 'http://' + self.rpc_host + ':' + self.rpc_port
        self.headers = {'content-type': 'application/json'}

    def gettransaction(self, txid):
        payload = json.dumps({"method": "gettransaction", "params": [txid], "jsonrpc": "2.0"})
        response = requests.get(self.serverURL, headers=self.headers, data=payload,
                                auth=(self.rpc_user, self.rpc_pass))
        return response.json()['result']

    def get_db(self, tx_account, tx_amount, txid, tx_category):
        to_exec = """SELECT db(balance, staked)
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, str(tx_account))
        result_set = self.cursor.fetchone()
        if tx_category == "generated":
            new_stake = int(result_set["staked"]) - tx_amount
            self.update_db(tx_account, new_stake, txid)
        else:
            new_balance = int(result_set["balance"]) + tx_amount
            self.update_db(tx_account, new_balance, txid)

    def make_user(self, tx_account):
        to_exec = "INSERT INTO db(snowflake, balance) VALUES(%s,%s)"
        self.cursor.execute(to_exec, (str(tx_account), '0'))
        self.connection.commit()

    def check_for_user(self, tx_account):
        to_exec = """SELECT snowflake
        FROM db
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, (str(tx_account)))
        result_set = self.cursor.fetchone()
        if result_set == None:
            self.make_user(tx_account)

        return result_set

    def add_tx_db(self, tx_account, tx_amount, txid):
        to_exec = "INSERT INTO unconfirmed(account, amount, txid) VALUES(%s,%s,%s)"
        self.cursor.execute(to_exec, (str(tx_account), str(tx_amount), str(txid)))
        self.connection.commit()
        self.check_for_user(self, tx_account)

    def remove_tx_db(self, tx_account, tx_amount, txid, tx_category):
        to_exec = "DELETE FROM unconfirmed WHERE VALUES(%s,%s,%s)"
        self.cursor.execute(to_exec, (str(tx_account), str(tx_amount), str(txid)))
        self.connection.commit()
        self.check_for_user(self, tx_account)
        self.get_db(tx_account, tx_amount, txid, tx_category)

    def process_tx(self, txid):
        transaction = self.gettransaction(txid)
        tx_conf = transaction["confirmations"]
        tx_account = transaction["details"][0]["account"]
        tx_amount = int(transaction["details"][0]["amount"])
        if "generated" in transaction:
            tx_category = "generated"
        elif tx_amount < 0:
            tx_category = "send"
        else:
            tx_category = "receive"

        if tx_conf > 0:
            self.remove_tx_db(tx_account, tx_amount, txid, tx_category)
        else:
            self.add_tx_db(tx_account, tx_amount, txid)


if __name__ == "__main__":
    txid = str(sys.argv[1])
    notify = Walletnotify()
    notify.process_tx(txid)
