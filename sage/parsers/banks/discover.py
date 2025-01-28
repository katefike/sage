from sage.parsers.utils import regex_search

def parse_withdrawal(body: str) -> tuple[str, str]:
    """
    Extract the txn amount and merchant from the email body
    E.g.
    Transaction Date: June 11, 2022

    Merchant: SQ *EARTH BISTRO CAFE

    Amount: $23.50
    """
    merchant = regex_search(r"(?<=Merchant: )(.*)(?= Amount: )", body)
    raw_amount = regex_search(r"(?<=Amount: \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})", body)
    return merchant, raw_amount
