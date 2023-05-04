from .db import postgres_connection, cursor
from .user import User


class Transfer:
    def __init__(self, from_id: int, to_id: int, title: str, description: str, amount: int):
        self.from_id = from_id
        self.to_id = to_id
        self.title = title
        self.description = description
        self.amount = amount

    def add_to_db(self):
        query = "INSERT INTO transfer (from_id, to_id, title, description, date, amount) " \
                "VALUES (%s, %s, %s, %s, now(), %s)"
        cursor.execute(query, (self.from_id, self.to_id, self.title, self.description, self.amount))
        postgres_connection.commit()

    @staticmethod
    def all_to(user: User, all_: bool = False):
        query = 'SELECT login, title, description, date, amount FROM transfer ' \
                'JOIN "user" u ON from_id = u.id WHERE to_id = %s ORDER BY date DESC'
        if not all_:
            query += ' LIMIT 5'

        cursor.execute(query, (user.id_,))
        return cursor.fetchall()

    @staticmethod
    def all_from(user: User, all_: bool = False):
        query = 'SELECT login, title, description, date, amount FROM transfer ' \
                'JOIN "user" u ON to_id = u.id WHERE from_id = %s ORDER BY date DESC'
        if not all_:
            query += ' LIMIT 5'
        cursor.execute(query, (user.id_,))
        return cursor.fetchall()
