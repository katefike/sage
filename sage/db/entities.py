"""
CRUD functions for the entities table.
"""
from typing import Optional

from loguru import logger

from sage.db import execute_statements

logger.add(sink="sage_main.log")


def get_id(merchant: Optional[str], payer: Optional[str]) -> int:
    query = """
    SELECT
        id
    FROM
        entities
    WHERE
        name = %s
        AND payer = %s
    """
    if merchant:
        params = (merchant, False)
    elif payer:
        params = (payer, True)
    row, _column = execute_statements.select(query, params)
    if not bool(row):
        entity_id = insert_get_id(params)
    else:
        entity_id = row[0]
    return entity_id


def insert_get_id(data: tuple) -> int:
    stmt = """
    INSERT INTO
        entities (name, payer)
    VALUES
        (%s, %s)
    RETURNING id;
    """
    entity_id = execute_statements.insert_get_id(stmt, data)
    return entity_id
