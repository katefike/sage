"""
CRUD methods for the banks table.
"""
from typing import Optional, Dict, Any

from loguru import logger

from sage.db import execute_statements
import datetime

logger.add(sink="sage_main.log")


def get_id(bank_name: str, account: Optional[str]) -> int:
    if account:
        params = (bank_name, account)
        query = """
        SELECT
            id
        FROM
            banks
        WHERE
            name = %s
            AND account = %s
        """
    else:
        params = (bank_name,)
        query = """
            SELECT
                id
            FROM
                banks
            WHERE
                name = %s
            """
    rows, _colummns = execute_statements.select(query, params)
    bank_id = rows[0][0]
    return bank_id


def get_banks_config() -> Dict[str, Any]:
    """
    Load banks configuration from the database and format it to match
    the structure of the original YAML config.
    
    Returns:
        Dict with bank names as keys and their configuration as values.
        The structure matches the original YAML format:
        
        {
            'Chase': {
                'email_addresses': ['no.reply.alerts@chase.com'],
                'accounts': [
                    {
                        'type': 'credit',
                        'date_opened': datetime.date(2024, 1, 1),
                        'date_closed': datetime.date(2024, 12, 31)
                    }
                ]
            },
            'Discover': {
                'email_addresses': ['discover@services.discover.com'],
                'accounts': [
                    {
                        'type': 'credit',
                        'date_opened': datetime.date(2024, 1, 1),
                        'date_closed': datetime.date(2024, 12, 31)
                    }
                ]
            },
            'Huntington': {
                'email_addresses': [
                    'HuntingtonAlerts@email.huntington.com',
                    'HuntingtonOnline@email.huntington.com'
                ],
                'accounts': [
                    {
                        'type': 'liquid',
                        'name': 'SAVE',
                        'date_opened': datetime.date(2024, 1, 1),
                        'date_closed': datetime.date(2024, 12, 31)
                    },
                    {
                        'type': 'liquid',
                        'name': 'CHECK',
                        'date_opened': datetime.date(2024, 1, 1),
                        'date_closed': datetime.date(2024, 12, 31)
                    }
                ]
            }
        }
    """
