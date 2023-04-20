from model.user import User

import psycopg2

postgres_connection = psycopg2.connect("dbname=bank_website user=mathmate host=localhost password=mathmate")
cursor = postgres_connection.cursor()


def get_user(login, password):
    query = f"SELECT login, email, password FROM \"user\" WHERE login = %s AND password = %s"
    cursor.execute(query, (login, password))
    res = cursor.fetchone()
    return res


def get_user_id(email: str):
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


def add_user_to_database(user: User):
    if not (user.login and user.email and user.password):
        return {"error": "some of fields are NULL"}

    query = f"INSERT INTO \"user\" (login, email, password)  VALUES (%s, %s, %s)"
    cursor.execute(query, (user.login, user.email, user.password))
    postgres_connection.commit()


def get_all_transfers_from(user: User):
    query = "SELECT (to_id, date, amount) FROM transfer WHERE from_id = %s"
    cursor.execute(query, (get_user_id(user.email), ))
    return cursor.fetchall()


def get_all_transfers_to(user: User):
    query = "SELECT (from_id, date, amount) FROM transfer WHERE to_id = %s"
    cursor.execute(query, (get_user_id(user.email), ))
    return cursor.fetchall()


def add_transfer(from_id: int, to_id: int, amount: int):
    query = "INSERT INTO transfer (from_id, to_id, date, amount) VALUES (%s, %s, now(), %s)"
    cursor.execute(query, (from_id, to_id, amount))
    postgres_connection.commit()
