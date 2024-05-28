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
    bank_id_results, _colummns = execute_statements.select(query, params)
    if bank_id_results:
        bank_id = bank_id_results[0][0]
        return bank_id
    else:
        logger.error(
            f"No bank IDs were returned. BANK: {bank_name} ACCOUNT: {account}."
        )
