import csv
from typing import List

from . import FILE_PATH


def main(file: str, dates: List) -> List:
    with open(FILE_PATH + file, mode="r", encoding="utf-8") as open_csv:
        reader = csv.DictReader(open_csv)
        csv_data = []

        for row in reader:
            row_date = row["Date"]
            if row_date in dates:
                csv_data.append(row)
    return csv_data
