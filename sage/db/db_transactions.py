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
from sqlite3 import Error


def insert_transaction(parsed_email: Dict) -> bool:
    bank_id = get_bank_id(parsed_email.get("bank"), parsed_email.get("account"))
    # entity_id = get_entity_id(parsed_email.get("merchent"), parsed_email.get("payer"))
    # TODO: Build out entity ID table
    # TODO: Incorporate the entity ID into the transaction
    gmail_id = parsed_email.get("gmail ID")
    gmail_time = parsed_email.get("gmail time")
    merchant = parsed_email.get("merchant")
    payer = parsed_email.get("payer")
    dollar_amount = parsed_email.get("amount")

    cent_amount = dollar_amount * 100

    descr = None
    if merchant:
        cent_amount = cent_amount * (-1)
        descr = merchant

    if payer:
        descr = payer

    transaction_data = (gmail_id, bank_id, cent_amount, gmail_time, descr)
    insert_stmt = """
    INSERT INTO
        transactions (gmail_id, bank_id, cents, date, descr)
    VALUES
        (?, ?, ?, ?, ?);
    """
    success = execute_insert(insert_stmt, transaction_data)
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
    bank_id_result = execute_select(select_stmt, parameters)
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
    entity_id = execute_select(select_stmt, entity_name)
    return entity_id


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
