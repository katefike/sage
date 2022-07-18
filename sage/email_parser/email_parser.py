import base64
import re
import datetime
from loguru import logger


def main(msg) -> dict:

    # Initialize returned variables
    transaction = False
    gmail_id = None
    gmail_time = None
    bank = None
    merchant = None
    payer = None
    dollar_amount = None
    account = None
    balance = None

    headers = msg["payload"]["headers"]

    for data in headers:
        if data["name"] == "From":
            sender = data["value"]
        if data["name"] == "Subject":
            subject = data["value"]

    if "data" in msg["payload"]["body"]:
        str_data = msg["payload"]["body"]["data"]
        html_data = data_encoder(str_data)
    elif "data" in msg["payload"]["parts"][0]["body"]:
        str_data = msg["payload"]["parts"][0]["body"]["data"]
        html_data = data_encoder(str_data)
    else:
        html_data = None

    # Parse the email based on who the sender is
    if sender == "Chase <no.reply.alerts@chase.com>":
        bank = "Chase"
        merchant, dollar_amount = parse_chase(subject)

    if html_data:
        if sender == "Discover Card <discover@services.discover.com>":
            bank = "Discover"
            if subject != "Transaction Alert":
                return False
            merchant, dollar_amount = parse_discover(html_data)

        if sender == "Huntington Alerts <HuntingtonAlerts@email.huntington.com>":
            bank = "Huntington"
            if subject == "Deposit":
                payer, dollar_amount = parse_huntington_deposit(html_data)
            elif subject == "Withdrawal or Purchase":
                merchant, dollar_amount = parse_huntington_charge(html_data)
            else:
                return False
            account = identify_huntington_account(html_data)
            balance = get_huntington_balance(html_data)

    gmail_id = msg["id"]
    epoch_gmail_time = float(msg["internalDate"])
    gmail_time = datetime.datetime.fromtimestamp(epoch_gmail_time / 1000.0).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if bank and dollar_amount and (merchant or payer):
        cent_amount = transform_amount(dollar_amount)
        if cent_amount:
            # Successfully parsed transaction
            # Ready to be inserted into the database
            transaction = True
            if merchant:
                descr = merchant
                cent_amount = cent_amount * (-1)
            if payer:
                descr = payer

            parsed_email = {
                "transaction": transaction,
                "gmail ID": gmail_id,
                "gmail time": gmail_time,
                "sender": sender,
                "subject": subject,
                "bank": bank,
                "descr": descr,
                "amount": cent_amount,
                "account": account,
                "balance": balance,
            }
        else:
            # Transaction that failed to parse
            # Regex failed to get the dollar amount
            logger.critical(
                f"\n GMAIL TIME: {gmail_time} \n GMAIL ID: {gmail_id} \
                \n SENDER: {sender} \n SUBJECT: {subject} \
                \n PROBLEMATIC DOLLAR AMOUNT: {dollar_amount}"
            )
            return False

    else:
        # Non-transaction or transaction that failed to parse
        parsed_email = {
            "transaction": transaction,
            "gmail ID": gmail_id,
            "time": gmail_time,
            "sender": sender,
            "subject": subject,
        }
        # UNCOMMENT
        # logger.debug(
        #     f"\n GMAIL TIME: {gmail_time} \n GMAIL ID: {gmail_id} \
        #     \n SENDER: {sender} \n SUBJECT: {subject}"
        # )
    return parsed_email


def data_encoder(str_data: str) -> str:
    if len(str_data) > 0:
        byte_data = base64.urlsafe_b64decode(str_data)
        html_data = str(byte_data, "utf-8")
    return html_data


def parse_chase(subject: str) -> str:
    """
    Extract the transaction dollar_amount and merchant from the email subject
    I.e.
    Your $1.00 transaction with DIGITALOCEAN.COM
    """
    merchant = regex_search("(?<=with )(.*)", subject)
    dollar_amount = regex_search("(?<=\$)(.*)(?= transaction)", subject)
    return merchant, dollar_amount


def parse_discover(html_data: str) -> str:
    """
    Extract the transaction dollar_amount and merchant from the email body
    I.e.
    Transaction Date:: June 11, 2022

    Merchant: SQ *EARTH BISTRO CAFE

    dollar_amount: $23.50
    """
    merchent = regex_search("(?<=Merchant: )(.*)(?=\n)", html_data)
    dollar_amount = regex_search("(?<=dollar_amount: )(.*)(?=\n)", html_data)
    return merchent, dollar_amount


def parse_huntington_charge(html_data: str) -> str:
    """
    Extract the transaction dollar_amount and merchent from the email body
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY
    from your account nicknamed SAVE.
    """
    merchent = regex_search("(?<= at )(.*)(?= from your account nicknamed)", html_data)
    dollar_amount = regex_search("(?<=for \$)(.*)(?= at)", html_data)
    return merchent, dollar_amount


def parse_huntington_deposit(html_data: str) -> str:
    """
    Extract the transaction dollar_amount and merchent from the email body
    I.e.
    We've processed an ACH deposit for $59.81
    from CHASE CREDIT CRD RWRD RDM to your account nicknamed CHECK.
    """
    payer = regex_search("(?<= from )(.*)(?= to your account nicknamed)", html_data)
    dollar_amount = regex_search("(?<=for \$)(.*)(?= from)", html_data)
    return payer, dollar_amount


def identify_huntington_account(html_data: str) -> str:
    """
    Identify the Huntington account referenced.
    Works for deposits or charges.
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY
    from your account nicknamed SAVE.
    """
    account = regex_search(
        "(?<= your account nicknamed )(.*)(?=. That's above the)", html_data
    )
    if account == "CHECK":
        account = "checking"
    if account == "SAVE":
        account = "savings"
    return account


def get_huntington_balance(html_data: str) -> str:
    """
    Extract the account balance for Huntington savings or checking accounts.
    Works for deposits or charges.
    I.e.
    Your balance is $19,748.78 as of 6/25/22 2:35 AM ET.
    """
    balance = regex_search("(?<=Your balance is \$)(.*)(?=. as of)", html_data)
    return balance


def regex_search(pattern, string) -> str:
    results = re.search(pattern, string)
    if results:
        all_matches = results.group(0)
        return all_matches
    else:
        return None


def transform_amount(dollar_amount: str) -> int:
    # Remove the comma
    dollar_amount = re.sub(",","",dollar_amount)
    try:
        cent_amount = int(float(dollar_amount) * 100)
        return cent_amount
    except ValueError:  # The dollar amount cannot be converted from a string to a float
        # Due to incorrect parsing using regex
        logger.critical(f"Failure to transform the amount due to value error.")
        return False
