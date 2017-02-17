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
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.db_user,
            password=self.db_pass,
            db=self.db)
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)

    def make_user(self, name, snowflake):
        to_exec = "INSERT INTO db(user, snowflake, balance) VALUES(%s,%s,%s)"
        self.cursor.execute(to_exec, (str(name).encode('ascii', 'ignore'), snowflake, '0'))
        self.connection.commit()

    def check_for_user(self, name, snowflake):
        to_exec = """SELECT snowflake
        FROM db
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, (str(snowflake)))
        result_set = self.cursor.fetchone()
        if result_set == None:
            self.make_user(name, snowflake)

        return result_set

    def get_bal_lasttxid(self, snowflake):
        to_exec = " SELECT balance,lasttxid FROM db WHERE snowflake LIKE %s "
        self.cursor.execute(to_exec, (str(snowflake)))
        result_set = self.cursor.fetchone()

        return result_set

    def update_db(self, snowflake, db_bal, lasttxid):
        to_exec = """UPDATE db
        SET balance=%s, lasttxid=%s
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, (db_bal,lasttxid,snowflake))
        self.connection.commit()

    def get_user(self, snowflake):
        to_exec = """
        SELECT balance, snowflake, lasttxid
        FROM db
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, (str(snowflake)))
        result_set = self.cursor.fetchone()

        return result_set
