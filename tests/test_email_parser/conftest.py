import pytest

from .. import ENV


@pytest.fixture(autouse=True)
def prepare_inbox(fresh_inbox):
    fresh_inbox("transaction_emails_development.mbox")
