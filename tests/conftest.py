import os
import pathlib
from typing import Dict

import psycopg2
import pytest
from dotenv import dotenv_values


@pytest.fixture(scope="session")
def env() -> Dict:
    app_root = str(pathlib.Path(__file__).parent.parent)
    env = dotenv_values(app_root + "/.env")
    return env


# @pytest.fixture(scope="session")
# def db_conn(env):
#     assert (
#         "test" in env["COMPOSE_PROJECT_NAME"]
#     ), "CRITICAL: env not the test env. DON'T NUKE YOUR PROD ENV!!"

#     connection = psycopg2.connect(
#         host="localhost",
#         dbname="postgres",
#         user="postgres",
#         password=env["POSTGRES_PASSWORD"],
#         port=env["POSTGRES_PORT"],
#     )
#     yield connection
#     connection.close()


# def truncate_db(db_conn):
#     """Only truncates `public` tables"""

#     LIST_OF_TABLES_NOT_TO_TRUNCATE = []
#     with db_conn, db_conn.cursor() as cursor:
#         cursor.execute(
#             """
#             SELECT
#                 table_name
#             FROM
#                 information_schema.tables
#             WHERE
#                 table_schema = 'public'
#                 AND table_type = 'BASE TABLE'
#             """
#         )
#         for result in cursor.fetchall():
#             table_name = result[0]
#             if table_name in LIST_OF_TABLES_NOT_TO_TRUNCATE:
#                 # we don't want these truncated
#                 continue
#             cursor.execute(f"TRUNCATE {table_name} CASCADE")

#         print("TRUNCATED DB")

# @pytest.fixture(scope="function")
# def fresh_db_conn(db_conn):

#     # preemptive truncation
#     util.truncate_db(db_co
#     yield db_c
#     # cleanup truncation
#     util.truncate_db(db_conn)
