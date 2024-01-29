import uvicorn
from settings import settings_db
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time


if __name__ == "__main__":
    connection = psycopg2.connect(user=settings_db['username'], 
                        password=settings_db['password'], 
                        host=settings_db['host'])


    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    try:
        sql_create_database = cursor.execute(f'create database {settings_db['database']}')
    except:
        pass


    cursor.close()
    connection.close()

    uvicorn.run("routings:app", host="0.0.0.0", port=8000, log_level="info")