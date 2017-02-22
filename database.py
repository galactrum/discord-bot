import pymysql.cursors
from utils import parsing, output

config = parsing.parse_json('config.json')["mysql"]
host = config["db_host"]
try:
    port = int(config["db_port"])
except KeyError:
    port = 3306
db_user = config["db_user"]
db_pass = config["db_pass"]
db = config["db"]
connection = pymysql.connect(
    host=host,
    port=port,
    user=db_user,
    password=db_pass,
    db=db)
cursor = connection.cursor(pymysql.cursors.DictCursor)

#cursor.execute("DROP DATABASE IF EXISTS {};".format(database))
#cursor.execute("CREATE DATABASE IF NOT EXISTS {};".format(database))
#conn.commit()

#cursor.execute("USE {};".format(database))


def run():
    cursor.execute("""CREATE TABLE IF NOT EXISTS person (
        userid_pk VARCHAR(17) NOT NULL,
        username VARCHAR(37) NOT NULL,
        balance FLOAT NOT NULL,
        PRIMARY KEY (username)
        ) ENGINE=InnoDB;""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS deposit (
        userid_fk VARCHAR(17) NOT NULL,
        address_from VARCHAR(34) NOT NULL,
        address_to VARCHAR(34) NOT NULL,
        amount FLOAT NOT NULL,
        FOREIGN KEY (userid_fk) REFERENCES person(userid_pk),
        ) ENGINE=InnoDB;""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS withdrawal (
        userid_fk VARCHAR(17) NOT NULL,
        address_from VARCHAR(34) NOT NULL,
        address_to VARCHAR(34) NOT NULL,
        amount FLOAT NOT NULL,
        FOREIGN KEY (userid_fk) REFERENCES person(userid_pk),
        ) ENGINE=InnoDB;""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS tip (
        userid_from_fk VARCHAR(17) NOT NULL,
        userid_to_fk VARCHAR(17) NOT NULL,
        ammount FLOAT NOT NULL,
        FOREIGN KEY (userid_from_fk) REFERENCES person(userid_pk),
        FOREIGN KEY (userid_to_fk) REFERENCES person(userid_pk),
        ) ENGINE=InnoDB;""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS server (
        server_id VARCHAR(18) NOT NULL,
        enable_soak TINYINT(1) NOT NULL,
        PRIMARY KEY (server_id)
        ) ENGINE=InnoDB;""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS channel (
        channel_id VARCHAR(18) NOT NULL,
        server_id VARCHAR(18) NOT NULL,
        enabled TINYINT(1) NOT NULL,
        FOREIGN KEY (server_id) REFERENCES server(server_id),
        PRIMARY KEY (channel_id)
        ) ENGINE=InnoDB;""")

    cursor.execute("CREATE INDEX userindex ON db(user) using BTREE;")
    cursor.execute("CREATE INDEX serverindex ON server(server_id) using BTREE;")
    cursor.execute("CREATE INDEX channelindex ON channel(channel_id) using BTREE;")
