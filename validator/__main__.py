"""
This is a helper module for validating the transaction data in DB against
a bank's CSV of transactions. This module isn't use by the Sage program,
it's used to facilitate local development and troubleshooting.
"""
import calendar
import csv
import pathlib
import sys
from datetime import datetime
from typing import Dict, List

from loguru import logger

from sage.db import transactions
from sage.models.transaction import Transaction

from . import ENV

logger.add(sink="validator.log", level="INFO")

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

    logger.info(f"Getting data from validation CSV file: {file}")
    csv_data = get_csv_data(file, dates)
    total_csv_rows = len(csv_data)

    # transaction dates use ISO 8601 format; 1999-01-08.
    if start_date == stop_date:
        logger.info(f"Getting DB transaction data for {start_date}.")
    else:
        logger.info(f"Getting DB transaction data from {start_date} to {stop_date}.")
    db_data = get_db_data(start_date, stop_date)
    total_db_records = len(db_data)

    logger.info(f"Total CSV rows: {total_csv_rows}")
    logger.info(f"Total DB records: {total_db_records}")
    if total_csv_rows != total_db_records:
        logger.error("Total rows in CSV differs from DB!")


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


def get_db_data(start_date: str, stop_date: str) -> List:
    db_records = transactions.get_complete_transactions_by_daterange(
        start_date, stop_date
    )
    db_data = []

    for db_record in db_records:
        # TODO: Use SQLAlchemy #16
        # Instantiate Transaction object using email ID.
        transaction = Transaction(db_record[1])
        # Transform the date to Huntington's style
        transaction.date = datetime.strftime(db_record[2], "%m/%d/%Y")
        transaction.bank = db_record[3]
        transaction.account = db_record[4]
        # For simplicity sake, let's pretend everyone is a merchant
        transaction.merchant = db_record[5]
        transaction.amount = db_record[6]
        db_data.append(transaction)
    return db_data


if __name__ == "__main__":  # pragma: no cover
    file = sys.argv[1]
    date = sys.argv[2]
    msg_count = main(file, date)
