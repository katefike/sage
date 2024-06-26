import copy
import csv
from typing import Dict, List

from loguru import logger

from sage.models.transaction import Transaction

from . import FILE_PATH

logger.add(sink="validator.log", level="INFO")


def get_csv_data(file: str, dates: List) -> List:
    with open(FILE_PATH + file, mode="r", encoding="utf-8") as open_csv:
        reader = csv.DictReader(open_csv)
        csv_data = []

        for row in reader:
            row_date = row["Date"]
            if row_date in dates:
                csv_data.append(row)
    return csv_data


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
            # Convert Transaction decimal to string
            if str(Transaction.amount) != csv_row.get("Amount"):
                continue
            if "transfer" not in Transaction.type_:
                # The Huntington CSV sometimes includes a lot of extra spaces
                if Transaction.merchant.replace(" ", "") != csv_row.get(
                    "Payee Name"
                ).replace(" ", ""):
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
            # Convert Transaction decimal to string
            if str(Transaction.amount) != csv_row.get("Amount"):
                continue
            if "transfer" not in Transaction.type_:
                # The Huntington CSV sometimes includes a lot of extra spaces
                if Transaction.merchant.replace(" ", "") != csv_row.get(
                    "Payee Name"
                ).replace(" ", ""):
                    continue
            # Remove row from CSV data if all three fields are matched
            db_data_copy.remove(Transaction)
    diff["DB records not in CSV"] = db_data_copy

    return diff
