from sage.__main__ import main
from tests import utils


def test_email_insert(etl_db_conn):
    """
    Ensure that all emails in the inbox are inserted into the emails table.
    """
    utils.refresh_inbox("txn_emails.mbox")
    msg_count = main()
    # Query to get the count of the emails table.
    with etl_db_conn, etl_db_conn.cursor() as cursor:
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
    # Without this it "passes" even if no emails were retrieved
    assert msg_count.get("retrieved") > 0
    assert msg_count.get("retrieved") == inserted_count
