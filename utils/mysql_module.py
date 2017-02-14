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
        self.connection.cursor(pymysql.cursors.DictCursor)

    def make_user(self, author):
        to_exec = "INSERT INTO person(user,balance) VALUES(%s,%s)"
        cursor.execute(to_exec, str(author), '0')
        connection.commit()
