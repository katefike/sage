"""
Identify the oldest txn that has the same attributes as the current txn.
"""

from loguru import logger

from sage.db import txns
from sage.models.transaction import Transaction

logger.add(sink="sage_main.log")


def main(txn: Transaction) -> Transaction:
    txn.identical_txn_id = txns.get_identical_txn_id(txn)
    if txn.identical_txn_id is not None:
        logger.warning(f"Idential txn ID {txn.identical_txn_id} exists for txn {txn}.")
    return txn
