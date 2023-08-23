"""
CRUD methods for the emails table.
"""
from loguru import logger

from sage.db import execute_statements
from sage.email_data.email import Email

logger.add(sink="sage_main.log")


def insert_email(email: Email) -> int:
    stmt = """
    INSERT INTO
        emails (uid, batch_time, forwarded_date, from_, origin, subject, html, body)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    email_data = (
        email.uid,
        email.batch_time,
        email.forwarded_date,
        email.from_,
        email.origin,
        email.subject,
        email.html,
        email.body,
    )
    email_id = execute_statements.insert_get_id(stmt, email_data)
    return email_id
