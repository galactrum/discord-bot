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
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.db_user,
            password=self.db_pass,
            db=self.db)
        return self.connection

    def cursor(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        return cursor


