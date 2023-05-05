import psycopg2
from db import connect


create_user_query = 'CREATE TABLE IF NOT EXISTS "user" (' \
                    'id SERIAL PRIMARY KEY, ' \
                    'login VARCHAR(100) NOT NULL, ' \
                    'email VARCHAR(100) NOT NULL, ' \
                    'password VARCHAR NOT NULL, ' \
                    'balance INTEGER DEFAULT 0)'

create_transfer_query = 'CREATE TABLE IF NOT EXISTS transfer (' \
                        'id SERIAL PRIMARY KEY,' \
                        'from_id INTEGER REFERENCES "user"(id),' \
                        'to_id INTEGER REFERENCES "user"(id),' \
                        'date DATE,' \
                        'amount INTEGER,' \
                        'title VARCHAR(100),' \
                        'description VARCHAR(255))'

# Creating tables
postgres_connection = connect('bank_website', 'postgres', 'test')
cursor = postgres_connection.cursor()

cursor.execute(create_user_query)
cursor.execute(create_transfer_query)
postgres_connection.commit()
