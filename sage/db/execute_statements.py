import os
import pathlib
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from loguru import logger

logger.add(sink="debug.log")

# TODO: Consider making a database class with methods
# https://hackersandslackers.com/psycopg2-postgres-python/


def open_connection():
    # Get all environment variables
    app_root = str(pathlib.Path(__file__).parent.parent.parent)
    env_path = app_root + "/.env"
    if not load_dotenv(env_path):
        logger.critical(
            f"ENVIRONMENT ERROR: .env failed to load from \
            {env_path}"
        )
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
        return conn.cursor()
    except psycopg2.DatabaseError as error:
        logger.critical(f"Failed to connect to the database: {error}")
        raise error


def execute_select(query: str, params: Optional[tuple]) -> tuple:
    with open_connection() as connection:
        with connection.cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                records = [row for row in cursor.fetchall()]
                connection.close()
                return records
            except psycopg2.DatabaseError as error:
                logger.error(
                    f"Query execution failed due to an error:\
                        {error}"
                )


def execute_insert(stmt: str, data: tuple) -> tuple:
    with open_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(stmt, data)
                connection.commit()
                connection.close()
                return cursor.rowcount
            except psycopg2.DatabaseError as error:
                logger.error(
                    f"Query execution failed due to an error:\
                     {error}"
                )
