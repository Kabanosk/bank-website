from argon2 import PasswordHasher

from .db import postgres_connection, cursor


class User:
    def __init__(self, id_: int, login: str, email: str, password: str, balance: int):
        self.id_ = id_
        self.login = login
        self.email = email
        self.password = password
        self.balance = balance

    @staticmethod
    def get(login: str = None, email: str = None, id_: int = None):
        if not login and not email and not id_:
            return
        query = 'SELECT * FROM "user" '
        if login:
            query += 'WHERE login = %s'
            cursor.execute(query, (login,))
        if email:
            query += 'WHERE email = %s'
            cursor.execute(query, (email,))
        if id_:
            query += 'WHERE id = %s'
            cursor.execute(query, (id_,))
        res = cursor.fetchone()
        if res:
            return User(*res)
        return User(-1, "", "", "", 0)

    def exists(self):
        query = 'SELECT * FROM "user" WHERE email = %s AND login = %s'
        cursor.execute(query, (self.email, self.login))
        if cursor.fetchone():
            return True
        return False

    def add_to_db(self):
        if not (self.login and self.email and self.password):
            return {"error": "some of fields are NULL"}
        ph = PasswordHasher()
        h_pass = ph.hash(self.password)

        query = 'INSERT INTO "user" (login, email, password)  VALUES (%s, %s, %s)'
        cursor.execute(query, (self.login, self.email, h_pass))
        postgres_connection.commit()

    def update_password(self, new_password: str):
        ph = PasswordHasher()
        h_pass = ph.hash(new_password)

        self.password = h_pass
        query = 'UPDATE "user" SET password = %s WHERE email = %s'
        cursor.execute(query, (h_pass, self.email))
        postgres_connection.commit()

    def update_balance(self, balance_to_add: int):
        self.balance += balance_to_add
        query = 'UPDATE "user" SET balance = %s WHERE login = %s AND email = %s'
        cursor.execute(query, (self.balance, self.login, self.email))
        postgres_connection.commit()

    def to_dict(self):
        return {
            "id": self.id_,
            "login": self.login,
            "email": self.email,
            "balance": self.balance
        }

    @staticmethod
    def from_dict(user: dict):
        return User(user["id"], user["login"], user['email'], user['password'], user["balance"])
