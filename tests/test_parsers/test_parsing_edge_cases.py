"""
Tests the email parser (module sage/parsers/email_parser.py) to ensure it
can handle exceptions and errors from edge cases.

The input is the UID of the email, which maps to an email that was loaded
into the mail server when the docker container was created. These emails
are contained within the file
docker/mailserver/test_data/example_data/transaction_emails.mbox

They're also listed as separate files in
tests/test_parsers/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/models/transaction.py
"""
import pytest

from sage.parsers import email_parser
from tests import utils
