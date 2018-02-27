import pymysql.cursors
import discord
from utils import parsing, rpc_module
from decimal import Decimal

rpc = rpc_module.Rpc()

MIN_CONFIRMATIONS_FOR_DEPOSIT = 2


class Mysql:
    """
    Singleton helper for complex database methods
    """
    instance = None

    def __init__(self):
        if not Mysql.instance:
            Mysql.instance = Mysql.__Mysql()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __Mysql:
        def __init__(self):
            config = parsing.parse_json('config.json')["mysql"]
            self.__host = config["db_host"]
            self.__port = int(config.get("db_port", 3306))
            self.__db_user = config["db_user"]
            self.__db_pass = config["db_pass"]
            self.__db = config["db"]
            self.__connected = 1
            self.__setup_connection()
            self.txfee = parsing.parse_json('config.json')["txfee"]

        def __setup_connection(self):
            self.__connection = pymysql.connect(
                host=self.__host,
                port=self.__port,
                user=self.__db_user,
                password=self.__db_pass,
                db=self.__db)

# region User
        def make_user(self, snowflake, address):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "INSERT INTO users (snowflake_pk, balance, balance_unconfirmed, address) VALUES(%s, %s, %s, %s)"
            cursor.execute(
                to_exec, (str(snowflake), '0', '0', str(address)))
            cursor.close()
            self.__connection.commit()

        def check_for_user(self, snowflake):
            """
            Checks for a new user and creates one if needed.
            """
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "SELECT snowflake_pk, address, balance, balance_unconfirmed FROM users WHERE snowflake_pk LIKE %s"
            cursor.execute(to_exec, (str(snowflake)))
            result_set = cursor.fetchone()
            cursor.close()

            if result_set is None:
                address = rpc.getnewaddress(snowflake)
                self.make_user(snowflake, address)

        def get_user(self, snowflake):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "SELECT snowflake_pk, balance, balance_unconfirmed, address FROM users WHERE snowflake_pk LIKE %s"
            cursor.execute(to_exec, (str(snowflake)))
            result_set = cursor.fetchone()
            cursor.close()
            return result_set

        def get_user_by_address(self, address):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)           
            to_exec = "SELECT snowflake_pk, balance, balance_unconfirmed, address FROM users WHERE address LIKE %s"
            cursor.execute(to_exec, (str(address)))
            result_set = cursor.fetchone()
            cursor.close()
            return result_set

        def get_address(self, snowflake):
            result_set = self.get_user(snowflake)
            return result_set.get("address")
# endregion

# region Servers/Channels
        def check_server(self, server: discord.Server):
            if server is None:
                return
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)        
            to_exec = "SELECT server_id, enable_soak FROM server WHERE server_id LIKE %s"
            cursor.execute(to_exec, (server.id))
            result_set = cursor.fetchone()
            cursor.close()

            if result_set is None:
                self.add_server(server)

        def add_server(self, server: discord.Server):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "INSERT INTO server (server_id, enable_soak) VALUES(%s, %s)"
            cursor.execute(
                to_exec, (str(server.id), str(int(server.large))))
            cursor.close()
            self.__connection.commit()

        def remove_server(self, server: discord.Server):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "DELETE FROM server WHERE server_id = %s"
            cursor.execute(to_exec, (str(server.id),))
            to_exec = "DELETE FROM channel WHERE server_id = %s"
            cursor.execute(to_exec, (str(server.id),))
            cursor.close()
            self.__connection.commit()

        def add_channel(self, channel: discord.Channel):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)            
            to_exec = "INSERT INTO channel(channel_id, server_id, enabled) VALUES(%s, %s, 1)"
            cursor.execute(
                to_exec, (str(channel.id), str(channel.server.id)))
            cursor.close()
            self.__connection.commit()

        def remove_channel(self, channel):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)            
            to_exec = "DELETE FROM channel WHERE channel_id = %s"
            cursor.execute(to_exec, (str(channel.id),))
            cursor.close()
            self.__connection.commit()
# endregion

# region Balance
        def set_balance(self, snowflake, to, is_unconfirmed = False):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            if is_unconfirmed:
                to_exec = "UPDATE users SET balance_unconfirmed = %s WHERE snowflake_pk = %s"
            else:
                to_exec = "UPDATE users SET balance = %s WHERE snowflake_pk = %s"
            cursor.execute(to_exec, (to, snowflake,))
            cursor.close()
            self.__connection.commit()

        def get_balance(self, snowflake, check_update=False, check_unconfirmed = False):
            if check_update:
                self.check_for_updated_balance(snowflake)
            result_set = self.get_user(snowflake)
            if check_unconfirmed:
                return result_set.get("balance_unconfirmed")
            else:
                return result_set.get("balance")

        def add_to_balance(self, snowflake, amount, is_unconfirmed = False):
            self.set_balance(snowflake, self.get_balance(
                snowflake) + Decimal(amount))

        def remove_from_balance(self, snowflake, amount):
            self.set_balance(snowflake, self.get_balance(
                snowflake) - Decimal(amount))

        def add_to_balance_unconfirmed(self, snowflake, amount):
            balance_unconfirmed = self.get_balance(snowflake, check_unconfirmed = True) 
            self.set_balance(snowflake, balance_unconfirmed + Decimal(amount), is_unconfirmed = True)

        def remove_from_balance_unconfirmed(self, snowflake, amount):
            balance_unconfirmed = self.get_balance(snowflake, check_unconfirmed = True) 
            self.set_balance(snowflake, balance_unconfirmed - Decimal(amount), is_unconfirmed = True)
            
        def check_for_updated_balance(self, snowflake):
            """
            Uses RPC to get the latest transactions and updates
            the user balances accordingly

            This code is based off of parse_incoming_transactions in
            https://github.com/tehranifar/ZTipBot/blob/master/src/wallet.py
            """
            transaction_list = rpc.listtransactions(snowflake, 100)
            for tx in transaction_list:
                if tx["category"] != "receive":
                    continue
                txid = tx["txid"]
                amount = tx["amount"]
                confirmations = tx["confirmations"]
                address = tx["address"]
                status = self.get_transaction_status_by_txid(txid)
                user = self.get_user_by_address(address)

                # This address isn't a part of any user's account
                if not user:
                    continue

                snowflake_cur = user["snowflake_pk"]
                if status == "DOESNT_EXIST" and confirmations >= MIN_CONFIRMATIONS_FOR_DEPOSIT:
                    self.add_to_balance(snowflake_cur, amount)
                    self.add_deposit(snowflake_cur, amount, txid, 'CONFIRMED')
                elif status == "DOESNT_EXIST" and confirmations < MIN_CONFIRMATIONS_FOR_DEPOSIT:
                    self.add_deposit(snowflake_cur, amount,
                                     txid, 'UNCONFIRMED')
                    self.add_to_balance_unconfirmed(snowflake_cur, amount)
                elif status == "UNCONFIRMED" and confirmations >= MIN_CONFIRMATIONS_FOR_DEPOSIT:
                    self.add_to_balance(snowflake_cur, amount)
                    self.remove_from_balance_unconfirmed(snowflake_cur, amount)
                    self.confirm_deposit(txid)

        def get_transaction_status_by_txid(self, txid):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "SELECT status from deposit WHERE txid = %s"
            cursor.execute(to_exec, (txid,))
            result_set = cursor.fetchone()
            cursor.close()
            if not result_set:
                return "DOESNT_EXIST"

            return result_set["status"]
# endregion

# region Deposit/Withdraw/Tip/Soak
        def add_deposit(self, snowflake, amount, txid, status):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "INSERT INTO deposit(snowflake_fk, amount, txid, status) VALUES(%s, %s, %s, %s)"
            cursor.execute(
                to_exec, (str(snowflake), str(amount), str(txid), str(status)))
            cursor.close()
            self.__connection.commit()

        def confirm_deposit(self, txid):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "UPDATE deposit SET status = %s WHERE txid = %s"
            cursor.execute(to_exec, ('CONFIRMED', str(txid)))
            cursor.close()
            self.__connection.commit()

        def create_withdrawal(self, snowflake, address, amount):
            res = rpc.settxfee(self.txfee)
            if not res:
                return None

            txid = rpc.sendtoaddress(address, amount - self.txfee)
            if not txid:
                return None

            self.remove_from_balance(snowflake, amount)
            return self.add_withdrawal(snowflake, amount, txid)

        def add_withdrawal(self, snowflake, amount, txid):
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "INSERT INTO withdrawal(snowflake_fk, amount, txid) VALUES(%s, %s, %s)"
            cursor.execute(
                to_exec, (str(snowflake), str(amount), str(txid)))
            cursor.close()
            self.__connection.commit()
            return txid

        def add_tip(self, snowflake_from_fk, snowflake_to_fk, amount):
            self.remove_from_balance(snowflake_from_fk, amount)
            self.add_to_balance(snowflake_to_fk, amount)
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            tip_exec = "INSERT INTO tip(snowflake_from_fk, snowflake_to_fk, amount) VALUES(%s, %s, %s)"
            cursor.execute(
                tip_exec, (str(snowflake_from_fk), str(snowflake_to_fk), str(amount)))
            cursor.close()
            self.__connection.commit()

        def check_soak(self, server: discord.Server) -> bool:
            if server is None:
                return False
            self.check_server(server)
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "SELECT enable_soak FROM server WHERE server_id = %s"
            cursor.execute(to_exec, (str(server.id)))
            result_set = cursor.fetchone()
            cursor.close()
            return result_set['enable_soak']

        def set_soak(self, server, to):
            self.check_server(server)
            cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)
            to_exec = "UPDATE server SET enable_soak = %s WHERE server_id = %s"
            cursor.execute(to_exec, (to, str(server.id),))
            cursor.close()
            self.__connection.commit()
# endregion
