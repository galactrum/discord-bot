import pymysql.cursors, json
from utils import parsing, output

class Mysql:

    def __init__(self):
        config = parsing.parse_json('config.json')["mysql"]
        self.host = config["db_host"]
        try:
            self.port = int(config["db_port"])
        except KeyError:
            self.port = 3306
        self.db_user = config["db_user"]
        self.db_pass = config["db_pass"]
        self.db = config["db"]
        self.connected = 1
        self.my_connection()

    def my_connection(self):
        if self.connected == 0:
            output.warning("Connection has been lost, attempting to reconnect...")
        elif self.connected == 1:
            output.info("Establishing connection to database...")
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.db_user,
            password=self.db_pass,
            db=self.db)
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        return

    def make_user(self, name, snowflake):
        to_exec = "INSERT INTO db(user, snowflake, balance) VALUES(%s,%s,%s)"
        try:
            self.cursor.execute(to_exec, (str(name).encode('ascii', 'ignore'), snowflake, '0'))
            self.connection.commit()
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def check_for_user(self, name, snowflake):
        to_exec = """SELECT snowflake
        FROM db
        WHERE snowflake
        LIKE %s"""
        try:
            self.cursor.execute(to_exec, (str(snowflake)))
            result_set = self.cursor.fetchone()
            if result_set == None:
                self.make_user(name, snowflake)

            return result_set
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def get_bal_lasttxid(self, snowflake):
        to_exec = " SELECT balance, staked, lasttxid FROM db WHERE snowflake LIKE %s "
        try:
            self.cursor.execute(to_exec, (str(snowflake)))
            result_set = self.cursor.fetchone()

            return result_set
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def update_db(self, snowflake, db_bal, db_staked, lasttxid):
        to_exec = """UPDATE db
        SET balance=%s, staked=%s, lasttxid=%s
        WHERE snowflake
        LIKE %s"""
        try:
            self.cursor.execute(to_exec, (db_bal,db_staked,lasttxid,snowflake))
            self.connection.commit()
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def get_user(self, snowflake):
        to_exec = """
        SELECT snowflake, balance, staked, lasttxid
        FROM db
        WHERE snowflake
        LIKE %s"""
        try:
            self.cursor.execute(to_exec, (str(snowflake)))
            result_set = self.cursor.fetchone()

            return result_set
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def add_server(self, server):
        to_exec = "INSERT INTO server(server_id, enable_soak) VALUES(%s)"
        try:
            self.cursor.execute(to_exec, (str(server.id), int(server.large)))
            self.connection.commit()
            return
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def remove_server(self, server):
        to_exec = "DELETE FROM server WHERE server_id = %s"
        try:
            self.cursor.execute(to_exec, (str(server.id),))
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()
        to_exec = "DELETE FROM channel WHERE server_id = %s"
        try:
            self.cursor.execute(to_exec, (str(server.id),))
            self.connection.commit()
            return
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def add_channel(self, channel):
        to_exec = "INSERT INTO channel(channel_id, server_id, enabled) VALUES(%s, %s, 1)"
        try:
            self.cursor.execute(to_exec, (str(channel.id), str(channel.server.id),))
            self.connection.commit()
            return
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def remove_channel(self, channel):
        to_exec = "DELETE FROM channel WHERE channel_id = %s"
        try:
            self.cursor.execute(to_exec, (str(channel.id),))
            self.connection.commit()
            return
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def check_soak(self, server):
        to_exec = "SELECT enable_soak FROM server WHERE server_id = %s"
        try:
            self.cursor.execute(to_exec, (str(server.id)))
            result_set = self.cursor.fetchone()
            return result_set
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()

    def set_soak(self, server, to):
        to_exec = "UPDATE server SET enable_soak = %s WHERE server_id = %s"
        try:
            self.cursor.execute(to_exec, (to, str(server.id),))
            self.connection.commit()
            return
        except BrokenPipeError:
            self.connected = 0
            self.my_connection()