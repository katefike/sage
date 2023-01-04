"""
1. Get bank id
2. Get entity id
4. Insert transaction
"""
from typing import Dict, Optional

from loguru import logger

from sage.db.execute_statements import execute_insert, execute_select
from sage.email_data.transaction import Transaction

logger.add(sink="debug.log")


def insert_transaction(transaction: Transaction) -> bool:
    bank_id = get_bank_id(transaction.bank, transaction.account)
    # TODO: Build out entity ID table
    # TODO: Incorporate the entity ID into the transaction
    transaction_data = (
        transaction.uid,
        transaction.date,
        bank_id,
        transaction.type_,
        transaction.amount,
    )
    stmt = """
    INSERT INTO
        transactions (uid, date, type, bank_id, amount)
    VALUES
        (%s, %s, %s, %s, %s);
    """
    row_count = execute_insert(stmt, transaction_data)
    return row_count


def get_bank_id(bank_name: str, account: Optional[str]) -> int:
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
    bank_id_result = execute_select(query, params)
    if bank_id_result:
        if len(bank_id_result) == 1:
            bank_id = bank_id_result[0]
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


def get_entity_id(entity_name: str) -> int:
    select_stmt = """
    SELECT
        id
    FROM
        entities
    WHERE
        name = %s
    """
    entity_id = execute_select(select_stmt, entity_name)
    return entity_id


def insert_entity(entity_name: str):
    return
