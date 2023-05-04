import psycopg2


def connect(dbname: str, user: str, password: str):
    DATABASE_URL = f"postgresql://{user}:{password}@db:5432/{dbname}"
    return psycopg2.connect(DATABASE_URL)


postgres_connection = connect('bank_website', 'postgres', 'test')
cursor = postgres_connection.cursor()
