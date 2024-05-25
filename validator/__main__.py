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
from typing import List

from loguru import logger

from . import ENV

logger.add(sink="validator.log", level="INFO")

APP_ROOT = str(pathlib.Path(__file__).parent.parent)
FILE_PATH = APP_ROOT + "/validator/real_data/"


def main(file: str, date: str):
    logger.info("STARTING VALIDATION")

    dates = create_dates(date)
    logger.info(f"Dates to validate: {dates}")
    logger.info(f"Opening validation file: {file}")

    total_rows = 0

    with open(FILE_PATH + file, mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar='"')

        csv_headers = next(reader)
        logger.info(f"{csv_headers}")

        for row in reader:
            row_date = row[0]
            if row_date in dates:
                logger.info(f"{row}")
                total_rows = total_rows + 1

    logger.info(f"Total number of CSV rows: {total_rows}")


def create_dates(date) -> List:
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

    return dates


def transform_zero_padded_dates(raw_dates: List) -> List:
    dates = []

    for raw_date in raw_dates:
        zero_padded_date = raw_date.strftime("%m/%d/%Y")
        dates.append(zero_padded_date)
    return dates


if __name__ == "__main__":  # pragma: no cover
    file = sys.argv[1]
    date = sys.argv[2]
    msg_count = main(file, date)
