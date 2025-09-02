"""
CRUD functions for the txns table.
"""

from typing import List, Optional

from loguru import logger

from sage.db import banks, entities, execute_statements
from sage.models.transaction import Transaction

logger.add(sink="sage_main.log")


def insert_txn(txn: Transaction) -> bool:
    bank_id = banks.get_id(txn.bank, txn.account)

    # Transfers don't have entities
    entity_id = None
    if "transfer" not in txn.type_:
        entity_id = entities.get_id(txn.merchant, txn.payer)
    data = (
        txn.email_id,
        txn.date,
        bank_id,
        txn.type_,
        txn.amount,
        txn.balance,
        entity_id,
        txn.identical_txn_id,
    )
    stmt = """
    INSERT INTO
        txns (
                email_id,
                date,
                bank_id,
                type,
                amount,
                balance,
                entity_id,
                identical_txn_id
            )
    VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    row_count = execute_statements.insert(stmt, data)
    return row_count


def get_txns_by_daterange_and_bank_account(
    start_date: str, stop_date: str, bank: str, account: Optional[str]
) -> List[tuple]:  # pragma: no cover
    """
    Used in sage.validator; not a part of the main Sage program.
    That's why this function doesn't have test coverage.
    """
    bank_id = banks.get_id(bank, account)
    params = (start_date, stop_date, bank_id)
    query = """
    SELECT
        t.id AS "txn_id",
        t.email_id AS "email_id",
        t.date,
        b.name AS "bank_name",
        b.account AS "bank_account",
        e.name AS "entity_name",
        CASE
            WHEN t.type LIKE '%%withdrawal' THEN t.amount * -1
            ELSE t.amount
        END,
        t.type
    FROM txns t
        JOIN banks b ON b.id = t.bank_id
        LEFT JOIN entities e ON e.id = t.entity_id
    WHERE
        t.date >= %s 
        AND t.date <= %s
        AND t.bank_id = %s
    ORDER BY t.date ASC;
    """
    rows = execute_statements.select(query, params)
    return rows[0]


def get_identical_txn_id(txn: Transaction) -> Optional[int]:
    """
    Identify the oldest txn that is identical to the current txn for the
    following attributes:
    - date
    - type
    - bank
    - amount
    - entity (merchant/payer)
    """
    bank_id = banks.get_id(txn.bank, txn.account)

    params = (
        txn.date,
        txn.type_,
        bank_id,
        txn.amount,
    )

    # Transfers don't have entities
    if "transfer" in txn.type_:
        query = """
        SELECT
            MIN(t.id) AS "txn_id"
        FROM txns t
        WHERE t.date = %s
            AND t.type = %s
            AND t.bank_id = %s
            AND t.amount = %s
            AND t.entity_id IS NULL;
        """
    else:
        entity_id = entities.get_id(txn.merchant, txn.payer)
        query = """
        SELECT
            MIN(t.id) AS "txn_id"
        FROM txns t
        WHERE t.date = %s
            AND t.type = %s
            AND t.bank_id = %s
            AND t.amount = %s
            AND t.entity_id = %s;
        """
        params = params + (entity_id,)
    
    row, _column = execute_statements.select(query, params)
    identical_txn_id = row[0][0]
    return identical_txn_id


def get_identical_txns() -> tuple:
    """
    Get all txns that have been flagged with an identical txn.
    """
    query = """
    SELECT
        *
    FROM txns t
    WHERE t.identical_txn_id IS NOT NULL;
    """
    rows, _columns = execute_statements.select(query)
    return rows
