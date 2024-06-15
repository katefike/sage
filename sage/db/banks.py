"""
CRUD methods for the banks table.
"""
from typing import Optional

from loguru import logger

from sage.db import execute_statements

logger.add(sink="sage_main.log")


def get_id(bank_name: str, account: Optional[str]) -> int:
    if account:
        params = (bank_name, account)
        query = """
        SELECT
            id
        FROM
            banks
        WHERE
            name = %s
            AND account = %s
        """
    else:
        params = (bank_name,)
        query = """
            SELECT
                id
            FROM
                banks
            WHERE
                name = %s
            """
    rows, _colummns = execute_statements.select(query, params)
    bank_id = rows[0][0]
    return bank_id
