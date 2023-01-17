import pytest

from .. import ENV


@pytest.fixture(autouse=True)
def prepare_inbox(fresh_inbox, email_count):
    fresh_inbox("transaction_emails_development.mbox")
    count = len(email_count)
    assert count == 24, print(
        f"CRITICAL: The transaction emails were not successfully loaded into the inbox. The email count is {count}."
    )
