import pymysql.cursors
import discord
from utils import parsing, output

class Mysql:
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

    def make_user(self, name, snowflake):
        """
        Sets up a new user in the database with given name and snowflake ID
        """
        to_exec = "INSERT INTO users (snowflake_pk, username, balance) VALUES(%s, %s, %s)"
        self.__cursor.execute(to_exec, (str(snowflake), name, '0'))
        self.__connection.commit()

    def check_for_user(self, name, snowflake):
        """
        Checks for a new user and creates one if needed.
        Returns snowflake of created user.
        """

        to_exec = "SELECT snowflake_pk FROM users WHERE snowflake_pk LIKE %s"
        self.__cursor.execute(to_exec, (str(snowflake)))
        result_set = self.__cursor.fetchone()
        if result_set is None:
            self.make_user(name, snowflake)
            result_set = (snowflake)
        return result_set

    def get_user(self, snowflake):
        """
        Gets a user given a snowflake ID.
        """
        to_exec = "SELECT snowflake_pk, username, balance FROM users WHERE snowflake_pk LIKE %s"
        self.__cursor.execute(to_exec, (str(snowflake)))
        result_set = self.__cursor.fetchone()

        return result_set

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

    def set_balance(self, user, to):
        """
        Sets the soak setting for a server.
        """
        to_exec = "UPDATE users SET balance = %s WHERE snowflake_pk = %s"
        self.__cursor.execute(to_exec, (to, user.id,))
        self.__connection.commit()
