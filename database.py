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

cursor.execute("CREATE INDEX userindex ON db(user) using BTREE;")
