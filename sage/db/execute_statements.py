import psycopg2

DB_PATH = pathlib.Path(__file__).parent.parent.parent / "sage_db.db"


def open_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def execute_select(select_stmt: str, parameters: tuple) -> tuple:
    with open_connection() as connection:
        # possibly not needed to close connection
        with closing(connection.cursor()) as cursor:
            try:
                result = cursor.execute(select_stmt, parameters)
                return result.fetchone()
            except Error as error:
                logger.critical(f"{error}")
                return False


def execute_insert(insert_stmt: str, transaction_data: tuple) -> int:
    with open_connection() as connection:
        with closing(connection.cursor()) as cursor:
            try:
                return cursor.execute(insert_stmt, transaction_data)
            except Error as error:
                logger.critical(f"{error}")
                return False
