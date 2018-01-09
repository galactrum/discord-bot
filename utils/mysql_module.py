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

        def __setup_connection(self):
            self.__connection = pymysql.connect(
                host=self.__host,
                port=self.__port,
                user=self.__db_user,
                password=self.__db_pass,
                db=self.__db)
            self.__cursor = self.__connection.cursor(
                pymysql.cursors.DictCursor)

# region User
        def make_user(self, name, snowflake, address):
            to_exec = "INSERT INTO users (snowflake_pk, username, balance, address) VALUES(%s, %s, %s, %s)"
            self.__cursor.execute(
                to_exec, (str(snowflake), name, '0', str(address)))
            self.__connection.commit()

        def check_for_user(self, name, snowflake):
            """
            Checks for a new user and creates one if needed.
            """
            to_exec = "SELECT snowflake_pk, address, balance FROM users WHERE snowflake_pk LIKE %s"
            self.__cursor.execute(to_exec, (str(snowflake)))
            result_set = self.__cursor.fetchone()

            if result_set is None:
                address = rpc.getnewaddress()
                self.make_user(name, snowflake, address)

        def get_user(self, snowflake):
            to_exec = "SELECT snowflake_pk, username, balance, address FROM users WHERE snowflake_pk LIKE %s"
            self.__cursor.execute(to_exec, (str(snowflake)))
            result_set = self.__cursor.fetchone()
            return result_set

        def get_user_by_address(self, address):
            to_exec = "SELECT snowflake_pk, username, balance, address FROM users WHERE address LIKE %s"
            self.__cursor.execute(to_exec, (str(address)))
            result_set = self.__cursor.fetchone()
            return result_set

        def get_address(self, snowflake):
            result_set = self.get_user(snowflake)
            return result_set.get("address")
# endregion

# region Servers/Channels
        def check_server(self, server: discord.Server):
            to_exec = "SELECT server_id, enable_soak FROM server WHERE server_id LIKE %s"
            self.__cursor.execute(to_exec, (server.id))
            result_set = self.__cursor.fetchone()

            if result_set is None:
                self.add_server(server)

        def add_server(self, server: discord.Server):
            to_exec = "INSERT INTO server (server_id, enable_soak) VALUES(%s, %s)"
            self.__cursor.execute(
                to_exec, (str(server.id), str(int(server.large))))
            self.__connection.commit()

        def remove_server(self, server: discord.Server):
            to_exec = "DELETE FROM server WHERE server_id = %s"
            self.__cursor.execute(to_exec, (str(server.id),))
            to_exec = "DELETE FROM channel WHERE server_id = %s"
            self.__cursor.execute(to_exec, (str(server.id),))
            self.__connection.commit()

        def add_channel(self, channel: discord.Channel):
            to_exec = "INSERT INTO channel(channel_id, server_id, enabled) VALUES(%s, %s, 1)"
            self.__cursor.execute(
                to_exec, (str(channel.id), str(channel.server.id)))
            self.__connection.commit()

        def remove_channel(self, channel):
            to_exec = "DELETE FROM channel WHERE channel_id = %s"
            self.__cursor.execute(to_exec, (str(channel.id),))
            self.__connection.commit()
# endregion

# region Balance
        def set_balance(self, snowflake, to):
            to_exec = "UPDATE users SET balance = %s WHERE snowflake_pk = %s"
            self.__cursor.execute(to_exec, (to, snowflake,))
            self.__connection.commit()

        def get_balance(self, snowflake, check_update=False):
            if check_update:
                self.check_for_updated_balance()
            result_set = self.get_user(snowflake)
            return result_set.get("balance")

        def add_to_balance(self, snowflake, amount):
            self.set_balance(snowflake, self.get_balance(
                snowflake) + Decimal(amount))

        def remove_from_balance(self, snowflake, amount):
            self.set_balance(snowflake, self.get_balance(
                snowflake) - Decimal(amount))

        def check_for_updated_balance(self):
            """
            Uses RPC to get the latest transactions and updates
            the user balances accordingly
            """
            transaction_list = rpc.listtransactions("*", 100)
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
                elif status == "UNCONFIRMED" and confirmations >= MIN_CONFIRMATIONS_FOR_DEPOSIT:
                    self.add_to_balance(snowflake_cur, amount)
                    self.confirm_deposit(txid)

        def get_transaction_status_by_txid(self, txid):
            to_exec = "SELECT status from deposit WHERE txid = %s"
            self.__cursor.execute(to_exec, (txid,))
            result_set = self.__cursor.fetchone()
            if not result_set:
                return "DOESNT_EXIST"

            return result_set["status"]
# endregion

# region Deposit/Withdraw/Tip/Soak
        def add_deposit(self, snowflake, amount, txid, status):
            to_exec = "INSERT INTO deposit(snowflake_fk, amount, txid, status) VALUES(%s, %s, %s, %s)"
            self.__cursor.execute(
                to_exec, (str(snowflake), str(amount), str(txid), str(status)))
            self.__connection.commit()

        def confirm_deposit(self, txid):
            to_exec = "UPDATE deposit SET status = %s WHERE txid = %s"
            self.__cursor.execute(to_exec, ('CONFIRMED', str(txid)))
            self.__connection.commit()

        def create_withdrawal(self, snowflake, address, amount):
            txid = rpc.sendtoaddress(address, amount)
            if not txid:
                return None

            self.remove_from_balance(snowflake, amount)
            return self.add_withdrawal(snowflake, amount, txid)

        def add_withdrawal(self, snowflake, amount, txid):
            to_exec = "INSERT INTO withdrawal(snowflake_fk, amount, txid) VALUES(%s, %s, %s)"
            self.__cursor.execute(
                to_exec, (str(snowflake), str(amount), str(txid)))
            self.__connection.commit()
            return txid

        def add_tip(self, snowflake_from_fk, snowflake_to_fk, amount):
            self.remove_from_balance(snowflake_from_fk, amount)
            self.add_to_balance(snowflake_to_fk, amount)
            tip_exec = "INSERT INTO tip(snowflake_from_fk, snowflake_to_fk, amount) VALUES(%s, %s, %s)"
            self.__cursor.execute(
                tip_exec, (str(snowflake_from_fk), str(snowflake_to_fk), str(amount)))
            self.__connection.commit()

        def check_soak(self, server: discord.Server) -> bool:
            self.check_server(server)
            to_exec = "SELECT enable_soak FROM server WHERE server_id = %s"
            self.__cursor.execute(to_exec, (str(server.id)))
            result_set = self.__cursor.fetchone()
            return result_set['enable_soak']

        def set_soak(self, server, to):
            to_exec = "UPDATE server SET enable_soak = %s WHERE server_id = %s"
            self.__cursor.execute(to_exec, (to, str(server.id),))
            self.__connection.commit()
# endregion
