import psycopg2


def connect(dbname: str, user: str, host: str, password: str):
    return psycopg2.connect(f"dbname={dbname} user={user} host={host} password='{password}'")


# dbname=bank_website user=mathmate host=localhost password=mathmate
postgres_connection = connect('bank_website', 'postgres', 'test')
cursor = postgres_connection.cursor()
