import pytest


def test_get_receiving_email_user():
    receiving_email_user = pytest.RECEIVING_EMAIL_USER
    print(receiving_email_user)
    assert "incoming" == receiving_email_user
