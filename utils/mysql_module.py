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

    def make_user(self, author):
        to_exec = "INSERT INTO db(snowflake,balance) VALUES(%s,%s)".format(author, '0')
        self.cursor.execute(to_exec)
        self.connection.commit()

    def check_for_user(self, author):
        to_exec = """SELECT snowflake
        FROM db
        WHERE user
        LIKE %s"""
        self.cursor.execute(to_exec, (str(author)))
        result_set = self.cursor.fetchone()
        if result_set == None:
            self.make_user(author)

        return result_set

    def get_bal_lasttxid(self, author):
        to_exec = " SELECT balance,lasttxid FROM db WHERE snowflake LIKE %s "
        self.cursor.execute(to_exec, (author))
        result_set = self.cursor.fetchone()

        return result_set

    def update_db(self, author, db_bal, lasttxid):
        to_exec = """UPDATE db
        SET balance=%s, lasttxid=%s
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, (db_bal,lasttxid,str(author)))
        self.connection.commit()

    def get_user(self, author):
        to_exec = """
        SELECT balance, snowflake, lasttxid, tipped
        FROM db
        WHERE snowflake
        LIKE %s"""
        self.cursor.execute(to_exec, (str(author)))
        result_set = self.cursor.fetchone()

        return result_set
