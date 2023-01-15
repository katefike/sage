from typing import List, Optional

import psycopg2
from loguru import logger

from . import ENV

logger.add(sink="debug.log")

# TODO: Consider making a database class with methods
# https://hackersandslackers.com/psycopg2-postgres-python/


def open_connection():
    try:
        conn = psycopg2.connect(
            host=ENV["POSTGRES_HOST"],
            dbname=ENV["POSTGRES_DB"],
            user=ENV["POSTGRES_USER"],
            password=ENV["POSTGRES_PASSWORD"],
        )
        return conn
    except psycopg2.DatabaseError as error:
        logger.critical(f"Failed to connect to the database: {error}")
        raise error


def select(query: str, params: Optional[tuple] = None) -> List:
    with open_connection() as conn:
        with conn.cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                records = [row for row in cursor.fetchall()]
                return records
            except psycopg2.DatabaseError as error:
                logger.error(f"Query execution failed due to an error: {error}")


def insert(stmt: str, data: tuple) -> int:
    with open_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(stmt, data)
                conn.commit()
                return cursor.rowcount
            except psycopg2.DatabaseError as error:
                logger.error(f"Query execution failed due to an error: {error}")


def insert_get_id(stmt: str, data: tuple) -> int:
    with open_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(stmt, data)
                id = cursor.fetchone()[0]
                conn.commit()
                return id
            except psycopg2.DatabaseError as error:
                logger.error(f"Query execution failed due to an error: {error}")
