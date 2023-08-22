"""

"""
from sage.__main__ import main
from tests import utils


def test_email_insert(conn):
    """
    Ensure that all emails in the inbox are inserted into the emails table.
    """
    utils.fresh_inbox("transaction_emails.mbox")
    msg_count = main()
    # Query to get the count of the emails table.
    with conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*)
            FROM
                emails
            """
        )
        for result in cursor.fetchall():
            inserted_count = result[0]
    print(f"CHECK: {inserted_count}")
    assert 1 == 2
    assert msg_count.get("retrieved") == inserted_count
