import pymysql.cursors

host = "127.0.0.1"
port = 3306
user = "root"
passwd = "password"
database = "netcoin"

conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    passwd=passwd,
    charset='utf8'
)

cursor = conn.cursor()

#cursor.execute("DROP DATABASE IF EXISTS {};".format(database))
cursor.execute("CREATE DATABASE IF NOT EXISTS {};".format(database))
conn.commit()

cursor.execute("USE {};".format(database))

cursor.execute("""CREATE TABLE IF NOT EXISTS db (
    user VARCHAR(17) NOT NULL,
    balance FLOAT NOT NULL,
    lasttxid TEXT,
    tipped TEXT
    snowflake VARCHAR(17),
    PRIMARY KEY (user)
    ) ENGINE=InnoDB;""")

cursor.execute("CREATE INDEX userindex ON db(user) using BTREE;")
