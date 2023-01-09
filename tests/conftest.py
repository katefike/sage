import os
import pathlib

import pytest
from dotenv import load_dotenv


def pytest_configure():
    app_root = str(pathlib.Path(__file__).parent.parent)
    env_path = app_root + "/.env"
    if not load_dotenv(env_path):
        print(f".env faled to load from {env_path}")
    pytest.DOMAIN = os.environ.get("DOMAIN")
    pytest.IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
    pytest.FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
    pytest.RECEIVING_EMAIL_USER = os.environ.get("RECEIVING_EMAIL_USER")
    pytest.RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD") # noqa: E501,E261,W292
