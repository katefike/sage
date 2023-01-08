"""
CRUD methods for the banks table.
"""
from typing import Optional

from db import execute_statements
from loguru import logger

logger.add(sink="debug.log")


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
        if len(bank_id_result) == 1:
            bank_id = bank_id_result[0]
            print(bank_id)
            return bank_id
        else:
            logger.error(
                f"{len(bank_id_result)} bank IDs were returned.\
                     BANK: {bank_name} ACCOUNT: {account}."
            )
    else:
        logger.error(
            f"No bank IDs were returned. BANK: {bank_name} ACCOUNT: {account}."
        )
