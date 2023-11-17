import os

import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve the database URL from the .env file
DATABASE_URL = os.getenv("DB_CONNECTION")

# Database connection
connection = pymysql.connect(host='host',
                             user='user',
                             password='password',
                             database='dbname')


def get_db_session():
    try:
        yield connection
    finally:
        connection.close()
