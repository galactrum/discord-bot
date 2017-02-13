import pymysql.cursors, json


class Mysql:

    def __init__(self):
        with open("config.json", 'r') as f:
            config = json.loads(f.read())

        self.host = config["db_host"]
        self.port = int(config["db_port"])
        self.db_user = config["db_user"]
        self.db_pass = config["db_pass"]
        self.db = config["db"]

        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.db_user,
            password=self.db_pass,
            db=self.db)
        return self.connection

    def cursor(self):
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        return self.cursor


