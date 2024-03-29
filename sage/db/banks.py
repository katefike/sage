"""
CRUD methods for the banks table.
"""
from typing import Optional

from sage.db import execute_statements
from loguru import logger

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
    bank_id_result = execute_statements.select(query, params)
    if bank_id_result:
        bank_id = bank_id_result[0]
        return bank_id
    else:
        logger.error(
            f"No bank IDs were returned. BANK: {bank_name} ACCOUNT: {account}."
        )
