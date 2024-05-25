"""
CRUD methods for the entities table and the .
"""
from typing import Optional

from loguru import logger

from sage.db import execute_statements

logger.add(sink="sage_main.log")


def get_id(merchant: Optional[str], payer: Optional[str]) -> int:
    stmt = """
    SELECT
        id
    FROM
        entities
    WHERE
        name = %s
        AND payer = %s
    """
    if merchant:
        entity_data = (merchant, False)
    elif payer:
        entity_data = (payer, True)
    entity_id = execute_statements.select(stmt, entity_data)

    # Convert the tuple to an integer by accessing its first element
    # FIXME: Make it impossible to have the same combo of name and payer
    if isinstance(entity_id, list) and len(entity_id) == 1:
        entity_id = entity_id[0][0]

    if not bool(entity_id):
        entity_id = insert_get_id(entity_data)
    return entity_id


def insert_get_id(entity_data: tuple) -> int:
    stmt = """
    INSERT INTO
        entities (name, payer)
    VALUES
        (%s, %s)
    RETURNING id;
    """
    entity_id = execute_statements.insert_get_id(stmt, entity_data)
    return entity_id
