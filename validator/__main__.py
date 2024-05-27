"""
This is a helper module for validating the transaction data in DB against
a bank's CSV of transactions. This module isn't use by the Sage program,
it's used to facilitate local development and troubleshooting.
"""
import calendar
import copy
import csv
import pathlib
import sys
from datetime import datetime
from typing import Dict, List

from loguru import logger

from sage.db import transactions
from sage.models.transaction import Transaction

from . import ENV

logger.add(sink="validator.py", level="INFO")

APP_ROOT = str(pathlib.Path(__file__).parent.parent)
FILE_PATH = APP_ROOT + "/validator/real_data/"


def main(file: str, date: str):
    """
    input:
        bank CSV file
        selected date in 4-2024 format or 1-4-2024 format

    output:
        diff of DB transactions not in CSV
        diff of CSV transaction not in DB
        multiples identified in the DB transactions

    """
    logger.info("STARTING VALIDATION")

    dates, start_date, stop_date = create_dates(date)
    logger.info(f"Dates to validate: {dates}")

    # Get CSV data
    logger.info(f"Getting data from validation CSV file: {file}")
    csv_data = get_csv_data(file, dates)

    # Get DB data
    if start_date == stop_date:
        logger.info(f"Getting DB transaction data for {start_date}.")
    else:
        logger.info(f"Getting DB transaction data from {start_date} to {stop_date}.")
    file_parts = file.split("_")
    bank = file_parts[0]
    account = file_parts[1]
    db_data = get_db_data(start_date, stop_date, bank, account)

    # Diff the CSV and DB data, row-to-record
    diff = diff_csv_and_db_data(csv_data, db_data)

    logger.info(f"CSV rows not in DB:")
    for i, csv_row in enumerate(diff.get("CSV rows not in DB")):
        logger.info(
            f"{i + 1} - {csv_row['Date']}, {csv_row['Payee Name']}, {csv_row['Amount']}"
        )

    logger.info(f"DB records not in CSV:")
    for i, Transaction in enumerate(diff.get("DB records not in CSV")):
        logger.info(
            f"{i + 1} - {Transaction.date}, {Transaction.merchant}, {Transaction.amount}"
        )


def create_dates(date):
    raw_dates = []

    date_parts = date.split("-")

    integer_date_parts = []
    for date_part in date_parts:
        integer_date_parts.append(int(date_part))

    # Split month-day-year format
    if len(integer_date_parts) == 3:
        month = integer_date_parts[0]
        day = integer_date_parts[1]
        year = integer_date_parts[2]
        raw_date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y")
        raw_dates.append(raw_date)
        dates = transform_zero_padded_dates(raw_dates)
        start_date = raw_date.strftime("%Y-%m-%d")
        # The start and stop date are the same
        stop_date = start_date

    # Split month-year format
    if len(integer_date_parts) == 2:
        month = integer_date_parts[0]
        year = integer_date_parts[1]

        # Generate a calendar for the given month and year
        week_calendar = calendar.monthcalendar(2022, 6)

        for week in week_calendar:
            for day in week:
                # When day is zero, the day is a part of a flanking month
                if day == 0:
                    continue
                raw_date = datetime.strptime(f"{month}/{day}/{year}", "%m/%d/%Y")
                raw_dates.append(raw_date)
                dates = transform_zero_padded_dates(raw_dates)
        raw_start_date = datetime.strptime(dates[0], "%m/%d/%Y")
        start_date = raw_start_date.strftime("%Y-%m-%d")
        raw_stop_date = datetime.strptime(dates[-1], "%m/%d/%Y")
        stop_date = raw_stop_date.strftime("%Y-%m-%d")

    return dates, start_date, stop_date


def transform_zero_padded_dates(raw_dates: List) -> List:
    dates = []

    for raw_date in raw_dates:
        zero_padded_date = raw_date.strftime("%m/%d/%Y")
        dates.append(zero_padded_date)
    return dates


def get_csv_data(file: str, dates: List) -> List:
    with open(FILE_PATH + file, mode="r", encoding="utf-8") as open_csv:
        reader = csv.DictReader(open_csv)
        csv_data = []

        for row in reader:
            row_date = row["Date"]
            if row_date in dates:
                csv_data.append(row)
    return csv_data


def get_db_data(start_date: str, stop_date: str, bank: str, account: str) -> List:
    db_records = transactions.get_complete_transactions_by_daterange(
        start_date, stop_date
    )
    db_data = []

    for db_record in db_records:

        # Skip rows that don't match the bank and account specified in the
        # file name
        db_record_bank = db_record[3]
        db_record_account = db_record[4]
        if db_record_bank != bank and db_record_account != account:
            continue

        # TODO: Use SQLAlchemy #16
        # Instantiate Transaction object using email ID.
        transaction = Transaction(db_record[1])
        # Transform the date to Huntington's style
        transaction.date = datetime.strftime(db_record[2], "%m/%d/%Y")
        transaction.bank = db_record_bank
        transaction.account = db_record_account
        # For simplicity sake, let's pretend everyone is a merchant
        transaction.merchant = db_record[5]
        transaction.amount = db_record[6]
        db_data.append(transaction)
    return db_data


def diff_csv_and_db_data(csv_data: List, db_data: List) -> Dict:
    """
    csv_data:
        [{
            "Date": "04/01/2024",
            "Payee Name": "UBER BV          IAT PAYPAL",
            "Amount": "-0.51",
        },
        {
            "Date": "04/02/2024",
            "Payee Name": "INTERNET TFR FRM SAVINGS",
            "Amount": "1000.01",
        },]

    db_data:
        [Transaction(
            date="04/01/2024",
            merchant="UBER BV IAT PAYPAL",
            amount=Decimal("-0.51"),
        ),
        Transaction(
            date="04/03/2024",
            merchant="DISCOVER         E-PAYMENT",
            amount=Decimal("-49.53"),
        ),]
    diff:
        {
            "CSV rows not in DB": {
                "Date": "04/02/2024",
                "Payee Name": "INTERNET TFR FRM SAVINGS",
                "Amount": "1000.01",
            },
            "DB records not in CSV": Transaction(
                date="04/03/2024",
                merchant="DISCOVER         E-PAYMENT",
                amount=Decimal("-49.53"),
            ),
        }
    """
    # Compare total CSV rows to total DB records
    total_csv_rows = len(csv_data)
    logger.info(f"Total CSV rows: {total_csv_rows}")
    total_db_records = len(db_data)
    logger.info(f"Total DB records: {total_db_records}")
    if total_csv_rows != total_db_records:
        logger.error("Total rows in CSV differs from DB!")

    diff = {}

    # Identify CSV rows not in DB
    csv_data_copy = copy.deepcopy(csv_data)
    for Transaction in db_data:
        for csv_row in csv_data_copy:
            if Transaction.date != csv_row.get("Date"):
                continue
            # The Huntington CSV sometimes includes a lot of extra spaces
            if Transaction.merchant.replace(" ", "") != csv_row.get(
                "Payee Name"
            ).replace(" ", ""):
                continue
            # Convert Transaction decimal to string
            if str(Transaction.amount) != csv_row.get("Amount"):
                continue
            # Remove row from CSV data if all three fields are matched
            csv_data_copy.remove(csv_row)
    diff["CSV rows not in DB"] = csv_data_copy

    # Identify DB records not in CSV
    db_data_copy = copy.deepcopy(db_data)
    for csv_row in csv_data:
        for Transaction in db_data_copy:
            if Transaction.date != csv_row.get("Date"):
                continue
            # The Huntington CSV sometimes includes a lot of extra spaces
            if Transaction.merchant.replace(" ", "") != csv_row.get(
                "Payee Name"
            ).replace(" ", ""):
                continue
            # Convert Transaction decimal to string
            if str(Transaction.amount) != csv_row.get("Amount"):
                continue
            # Remove row from CSV data if all three fields are matched
            db_data_copy.remove(Transaction)
    diff["DB records not in CSV"] = db_data_copy

    return diff


if __name__ == "__main__":  # pragma: no cover
    file = sys.argv[1]
    date = sys.argv[2]
    msg_count = main(file, date)
