from model.user import User

import psycopg2

postgres_connection = psycopg2.connect("dbname=bank_website user=postgres password='test'")
cursor = postgres_connection.cursor()


def get_user(login, password):
    query = f"SELECT login, email, password FROM \"user\" WHERE login = %s AND password = %s"
    cursor.execute(query, (login, password))
    res = cursor.fetchone()
    return res


def get_user_data_by_id(_id: int):
    query = "SELECT login, email, password FROM \"user\" WHERE id = %s"
    cursor.execute(query, (_id,))
    return cursor.fetchone()


def get_user_id_by_email(email: str):
    query = "SELECT id FROM \"user\" WHERE email = %s"
    cursor.execute(query, (email, ))
    res = cursor.fetchone()
    if res is not None:
        res = res[0]
    return res


def get_user_id_by_login(login: str):
    query = "SELECT id FROM \"user\" WHERE login = %s"
    cursor.execute(query, (login, ))
    res = cursor.fetchone()
    if res is not None:
        res = res[0]
    return res


def get_user_balance(user: User):
    query = 'SELECT balance FROM "user" WHERE email = %s AND login = %s'
    cursor.execute(query, (user.email, user.login))
    res = cursor.fetchone()
    if res:
        res = res[0]
    return res


def user_exists(user: User):
    if not user.email and not user.login:
        return
    if user.email:
        query = 'SELECT * FROM "user" WHERE email = %s'
        cursor.execute(query, (user.email, ))
    elif user.login:
        query = 'SELECT * FROM "user" WHERE login = %s'
        cursor.execute(query, (user.login, ))
    if cursor.fetchone():
        return True
    return False


def add_user_to_database(user: User):
    if not (user.login and user.email and user.password):
        return {"error": "some of fields are NULL"}

    query = f"INSERT INTO \"user\" (login, email, password)  VALUES (%s, %s, %s)"
    cursor.execute(query, (user.login, user.email, user.password))
    postgres_connection.commit()


def get_all_transfers_from(user: User):
    query = 'SELECT login, date, amount FROM transfer ' \
            'JOIN "user" u ON to_id = u.id WHERE from_id = %s ORDER BY date'
    cursor.execute(query, (get_user_id_by_email(user.email),))
    return cursor.fetchall()


def get_all_transfers_to(user: User):
    query = 'SELECT login, date, amount FROM transfer ' \
            'JOIN "user" u ON to_id = u.id WHERE to_id = %s ORDER BY date'
    cursor.execute(query, (get_user_id_by_email(user.email),))
    return cursor.fetchall()


def add_transfer(from_id: int, to_id: int, amount: int):
    query = "INSERT INTO transfer (from_id, to_id, date, amount) VALUES (%s, %s, now(), %s)"
    cursor.execute(query, (from_id, to_id, amount))
    postgres_connection.commit()


def update_user_balance(user: User, balance_to_add: int):
    balance = get_user_balance(user)
    new_balance = balance + balance_to_add
    query = 'UPDATE "user" SET balance = %s WHERE login = %s AND email = %s'
    cursor.execute(query, (new_balance, user.login, user.email))
    postgres_connection.commit()
