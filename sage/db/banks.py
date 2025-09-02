"""
CRUD methods for the banks table.
"""
from typing import Optional, Dict, Any

from loguru import logger

from sage.db import execute_statements

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
    
    if not rows:
        raise ValueError(f"Bank not found: {bank_name}" + (f" account: {account}" if account else ""))
    
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
    query = """
    SELECT
        name,
        account,
        type,
        email_addresses,
        date_opened,
        date_closed
    FROM
        banks
    ORDER BY
        name, account
    """
    
    rows, columns = execute_statements.select(query)
    
    banks_config = {}
    
    for row in rows:
        bank_name = row[0]
        account = row[1]
        account_type = row[2]
        email_addresses = row[3]
        date_opened = row[4]
        date_closed = row[5]
        
        if bank_name not in banks_config:
            banks_config[bank_name] = {
                'email_addresses': [],
                'accounts': []
            }
        
        # Add email addresses if not already present
        for email in email_addresses:
            if email not in banks_config[bank_name]['email_addresses']:
                banks_config[bank_name]['email_addresses'].append(email)
        
        # Add account information
        account_info = {
            'type': account_type,
            'date_opened': date_opened,
            'date_closed': date_closed
        }
        
        if account:
            account_info['name'] = account
            
        banks_config[bank_name]['accounts'].append(account_info)
    
    return banks_config
