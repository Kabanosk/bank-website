#!/bin/bash

# CREATE DATABASE
db_name="bank_website"
psql -U postgres -c "CREATE DATABASE IF NOT EXISTS $db_name"

# CREATE TABLES
create_user_query="CREATE TABLE IF NOT EXISTS \"user\" (
  id SERIAL PRIMARY KEY,
  login VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR NOT NULL,
  balance INTEGER DEFAULT 0
)"

create_transfer_query="CREATE TABLE IF NOT EXISTS transfer (
  id SERIAL PRIMARY KEY,
  from_id INTEGER REFERENCES \"user\"(id),
  to_id INTEGER REFERENCES \"user\"(id),
  date DATE,
  amount INTEGER,
  title VARCHAR(100),
  description VARCHAR(255)
)"

psql -U postgres -d $db_name -c "$create_user_query"
psql -U postgres -d $db_name -c "$create_transfer_query"
