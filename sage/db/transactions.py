"""
1. Get bank id
2. Get entity id
3. Convert amount to cents
4. Insert transaction
"""
from contextlib import closing
from loguru import logger
from db import open_connection
from typing import Dict, Optional
import execute_statements


def insert_transaction(parsed_email: Dict) -> bool:
    bank_id = get_bank_id(parsed_email.get("bank"), parsed_email.get("account"))
    # entity_id = get_entity_id(parsed_email.get("merchent"), parsed_email.get("payer"))
    # TODO: Build out entity ID table
    # TODO: Incorporate the entity ID into the transaction
    gmail_id = parsed_email.get("gmail ID")
    gmail_time = parsed_email.get("gmail time")
    descr = parsed_email.get("descr")
    cent_amount = parsed_email.get("amount")

    transaction_data = (gmail_id, bank_id, cent_amount, gmail_time, descr)
    insert_stmt = """
    INSERT INTO
        transactions (gmail_id, bank_id, cents, date, descr)
    VALUES
        (?, ?, ?, ?, ?);
    """
    success = execute_statements.execute_insert(insert_stmt, transaction_data)
    if success:
        return True


def get_bank_id(bank_name: str, account: Optional[str]) -> int:
    if account:
        parameters = (bank_name, account)
        select_stmt = """
        SELECT
            id
        FROM
            banks
        WHERE
            name = ?
            AND account = ?
        """
    else:
        parameters = (bank_name,)
        select_stmt = """
            SELECT
                id
            FROM
                banks
            WHERE
                name = ?
            """
    bank_id_result = execute_statements.execute_select(select_stmt, parameters)
    if bank_id_result:
        if len(bank_id_result) == 1:
            bank_id = bank_id_result[0]
            return bank_id
        else:
            logger.error(
                f"{len(bank_id_result)} bank IDs were returned for the bank {bank_name} and account {account}"
            )
            return False
    else:
        logger.error(
            f"No bank IDs were returned for the bank {bank_name} and account {account}"
        )
        return False


def get_entity_id(entity_name: str) -> int:
    select_stmt = """
    SELECT
        id
    FROM
        entities
    WHERE
        name = ?
    """
    entity_id = execute_statements.execute_select(select_stmt, entity_name)
    return entity_id
