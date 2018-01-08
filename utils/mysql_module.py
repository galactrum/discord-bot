import pymysql.cursors
import discord
from utils import parsing, output, rpc_module
from decimal import *

rpc = rpc_module.Rpc()

MIN_CONFIRMATIONS_FOR_DEPOSIT = 2

class Mysql:
    instance = None

    def __init__(self):
        if not Mysql.instance:
            Mysql.instance = Mysql.__Mysql()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __Mysql:
        """
        Handles database related tasks.
        """
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
            self.__cursor = self.__connection.cursor(pymysql.cursors.DictCursor)

        def make_user(self, name, snowflake, address):
            """
            Sets up a new user in the database with given name and snowflake ID
            """
            to_exec = "INSERT INTO users (snowflake_pk, username, balance, address) VALUES(%s, %s, %s, %s)"
            self.__cursor.execute(to_exec, (str(snowflake), name, '0', str(address)))
            self.__connection.commit()

        def check_for_user(self, name, snowflake):
            """
            Checks for a new user and creates one if needed.
            Also checks if an user is a legacy user and creates an address for them
            """
            to_exec = "SELECT snowflake_pk, address, balance FROM users WHERE snowflake_pk LIKE %s"
            self.__cursor.execute(to_exec, (str(snowflake)))
            result_set = self.__cursor.fetchone()

            if result_set is None:
                address = rpc.getnewaddress()
                self.make_user(name, snowflake, address)
            elif result_set["address"] == "":
                address = rpc.getnewaddress()
                to_exec = "UPDATE users SET address = %s WHERE snowflake_pk = %s"
                self.__cursor.execute(to_exec, (address, str(snowflake)))
                self.__connection.commit()
                # Check calculate balance from database because previous balance might be wrong
                balance = self.calculate_balance_from_beginning(snowflake)
                self.set_balance(snowflake, balance)

        def get_user(self, snowflake):
            """
            Gets a user given a snowflake ID.
            """
            to_exec = "SELECT snowflake_pk, username, balance, address FROM users WHERE snowflake_pk LIKE %s"
            self.__cursor.execute(to_exec, (str(snowflake)))
            result_set = self.__cursor.fetchone()
            return result_set

        def get_user_by_address(self, address):
            """
            Gets a user given an address.
            """
            to_exec = "SELECT snowflake_pk, username, balance, address FROM users WHERE address LIKE %s"
            self.__cursor.execute(to_exec, (str(address)))
            result_set = self.__cursor.fetchone()
            return result_set

        def check_server(self, server: discord.Server):
            """
            Checks for a new server and creates a db entry if needed.
            """
            to_exec = "SELECT server_id, enable_soak FROM server WHERE server_id LIKE %s"
            self.__cursor.execute(to_exec, (server.id))
            result_set = self.__cursor.fetchone()

            if result_set is None:
                self.add_server(server)
        
        def add_server(self, server: discord.Server):
            """
            Adds a server to the database.
            """
            to_exec = "INSERT INTO server (server_id, enable_soak) VALUES(%s, %s)"
            self.__cursor.execute(to_exec, (str(server.id), str(int(server.large))))
            self.__connection.commit()

        def remove_server(self, server: discord.Server):
            """
            Removes a server from the database.
            """
            to_exec = "DELETE FROM server WHERE server_id = %s"
            self.__cursor.execute(to_exec, (str(server.id),))
            to_exec = "DELETE FROM channel WHERE server_id = %s"
            self.__cursor.execute(to_exec, (str(server.id),))
            self.__connection.commit()

        def add_channel(self, channel: discord.Channel):
            """
            Adds a channel to the database.
            """
            to_exec = "INSERT INTO channel(channel_id, server_id, enabled) VALUES(%s, %s, 1)"
            self.__cursor.execute(to_exec, (str(channel.id), str(channel.server.id)))
            self.__connection.commit()

        def remove_channel(self, channel):
            """
            Removes a channel from the database.
            """
            to_exec = "DELETE FROM channel WHERE channel_id = %s"
            self.__cursor.execute(to_exec, (str(channel.id),))
            self.__connection.commit()

        def check_soak(self, server: discord.Server) -> bool:
            """
            Checks if soak is enabled for a specific server.
            """
            self.check_server(server)
            to_exec = "SELECT enable_soak FROM server WHERE server_id = %s"
            self.__cursor.execute(to_exec, (str(server.id)))
            result_set = self.__cursor.fetchone()
            return result_set['enable_soak']

        def set_soak(self, server, to):
            """
            Sets the soak setting for a server.
            """
            to_exec = "UPDATE server SET enable_soak = %s WHERE server_id = %s"
            self.__cursor.execute(to_exec, (to, str(server.id),))
            self.__connection.commit()

        def set_balance(self, snowflake, to):
            """
            Sets the soak setting for a server.
            """
            to_exec = "UPDATE users SET balance = %s WHERE snowflake_pk = %s"
            self.__cursor.execute(to_exec, (to, snowflake,))
            self.__connection.commit()

        def get_balance(self, snowflake, check_update = False):
            if check_update:
                self.check_for_updated_balance()
            result_set = self.get_user(snowflake)
            return result_set.get("balance")

        def add_to_balance(self, snowflake, amount):
            self.set_balance(snowflake, self.get_balance(snowflake) + Decimal(amount))

        def remove_from_balance(self, snowflake, amount):
            self.set_balance(snowflake, self.get_balance(snowflake) - Decimal(amount))

        def get_address(self, snowflake):
            result_set = self.get_user(snowflake)
            return result_set.get("address")


        def get_username_by_address(self, address):
            user = self.get_user_by_address(address)
            if not user:
                return None

            return user["address"]

        def check_for_updated_balance(self):
            # could this be empty here?
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
                if not user:
                    continue
                snowflake_cur = user["snowflake_pk"]
                if status == "DOESNT_EXIST" and confirmations >= MIN_CONFIRMATIONS_FOR_DEPOSIT:
                    self.add_to_balance(snowflake_cur, amount)
                    self.add_deposit(snowflake_cur, amount, txid, 'CONFIRMED')
                elif status == "DOESNT_EXIST" and confirmations < MIN_CONFIRMATIONS_FOR_DEPOSIT:
                    self.add_deposit(snowflake_cur, amount, txid, 'UNCONFIRMED')
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

        def add_deposit(self, snowflake, amount, txid, status):
            to_exec = "INSERT INTO deposit(snowflake_fk, amount, txid, status) VALUES(%s, %s, %s, %s)"
            self.__cursor.execute(to_exec, (str(snowflake), str(amount), str(txid), str(status)))
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
            self.__cursor.execute(to_exec, (str(snowflake), str(amount), str(txid)))
            self.__connection.commit()
            return txid

        def add_tip(self, snowflake_from_fk, snowflake_to_fk, amount):
            self.remove_from_balance(snowflake_from_fk, amount)
            self.add_to_balance(snowflake_to_fk, amount)
            tip_exec = "INSERT INTO tip(snowflake_from_fk, snowflake_to_fk, amount) VALUES(%s, %s, %s)"
            self.__cursor.execute(tip_exec, (str(snowflake_from_fk), str(snowflake_to_fk), str(amount)))
            self.__connection.commit()

        def calculate_balance_from_beginning(self, snowflake):
            tips_from_exec = "SELECT amount FROM tip WHERE snowflake_from_fk = %s"
            self.__cursor.execute(tips_from_exec, (snowflake))
            tips_from = self.__cursor.fetchall()

            tips_to_exec = "SELECT amount FROM tip WHERE snowflake_to_fk = %s"
            self.__cursor.execute(tips_to_exec, (snowflake))
            tips_to = self.__cursor.fetchall()

            withdrawals_exec = "SELECT amount FROM withdrawal WHERE snowflake_fk = %s"
            self.__cursor.execute(withdrawals_exec, (snowflake))
            withdrawals = self.__cursor.fetchall()

            deposits_exec = "SELECT amount from deposit WHERE snowflake_fk = %s"
            self.__cursor.execute(deposits_exec, (snowflake))
            deposits = self.__cursor.fetchall()

            print(tips_from, tips_to, withdrawals, deposits)

            balance_sum = 0
            for tip_from in tips_from:
                # add up the tips from others
                balance_sum += tip_from["amount"]

            for tip_to in tips_to:
                # subtract the tips from others
                balance_sum -= tip_to["amount"]

            for withdrawal in withdrawals:
                # subtract withdrawals
                balance_sum -= withdrawal["amount"]

            for deposit in deposits:
                # add up deposits
                balance_sum += deposit["amount"]

            return balance_sum
            

