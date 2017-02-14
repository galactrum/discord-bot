from utils import output

def make_user(cur, author):
    to_exec = "INSERT INTO person(userid_pk, username, balance) VALUES(%s, %s, %s)"
    cur.execute(to_exec, (str(author.id), str(author), '0',))
    return


def get_user(cur, author):
    try:
        to_exec = """SELECT userid_pk FROM person WHERE username=%s"""
        cur.execute(to_exec, (str(author),))
        result_set = cur.fetchone()
    except Exception as e:
        print("Error in SQL query: ", str(e))
        return
    return result_set[0]


def check_for_user(cur, author):
    try:
        to_exec = """SELECT username FROM person WHERE userid_pk=%s"""
        cur.execute(to_exec, (str(author.id),))
        result_set = cur.fetchone()
    except Exception as e:
        print("Error in SQL query: ", str(e))
        return
    if not result_set:
        make_user(cur, author)
        return


def set_bal(cur, author_id, db_bal):
    try:
        to_exec = """UPDATE person SET balance=%s WHERE userid_pk=%s"""
        cur.execute(to_exec, (db_bal, str(author_id),))
    except Exception as e:
        print("Error: " + str(e))


def get_bal(cur, author_id):
    try:
        to_exec = """SELECT username FROM person WHERE userid_pk=%s"""
        cur.execute(to_exec, (str(author_id),))
        result_set = cur.fetchone()
    except Exception as e:
        print("Error in SQL query: ", str(e))
        return
    return result_set[0]


def withdraw(cur, author, address_from, address_to, amount):
    old_bal = int(get_bal(cur, author.id))
    new_bal = old_bal - amount
    set_bal(cur, author.id, new_bal)
    try:
        to_exec = "INSERT INTO withdrawal(userid_pk, address_from, address_to, amount) VALUES(%s, %s, %s, %s)"
        cur.execute(to_exec, (str(author.id), address_from, address_to, str(amount),))
    except Exception as e:
        print("Error in SQL query: ", str(e))
        return
    return


def deposit(cur, author, address_from, address_to, amount):
    old_bal = int(get_bal(cur, author.id))
    new_bal = old_bal + amount
    set_bal(cur, author.id, new_bal)
    try:
        to_exec = "INSERT INTO deposit(userid_pk, address_from, address_to, amount) VALUES(%s, %s, %s, %s)"
        cur.execute(to_exec, (str(author.id), address_from, address_to, str(amount),))
    except Exception as e:
        print("Error in SQL query: ", str(e))
        return
    return


def tip(cur, author, user_to, amount):
    old_bal = int(get_bal(cur, author.id))
    new_bal = old_bal - amount
    set_bal(cur, author.id, new_bal)

    user_to_id = get_user(cur, user_to)

    old_bal = int(get_bal(cur, user_to_id))
    new_bal = old_bal + amount
    set_bal(cur, user_to_id, new_bal)
    try:
        to_exec = "INSERT INTO tip(userid_from_fk, userid_to_pk, amount) VALUES(%s, %s, %s)"
        cur.execute(to_exec, (str(author.id), str(author.id), str(user_to_id), str(amount),))
    except Exception as e:
        print("Error in SQL query: ", str(e))
        return
    return
