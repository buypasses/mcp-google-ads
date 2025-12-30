"""
Account Tools

Functions for Google Ads account operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Optional
from api_client import GoogleAdsClient, format_customer_id


def list_accounts(client: GoogleAdsClient) -> List[str]:
    """
    List all accessible Google Ads accounts.

    Returns:
        List of customer IDs
    """
    return client.list_accessible_customers()


def get_account_info(client: GoogleAdsClient, customer_id: str) -> Dict[str, Any]:
    """
    Get account information for a customer.

    Args:
        client: Google Ads client
        customer_id: The customer ID to get info for

    Returns:
        Account information dict
    """
    query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.manager
        FROM customer
        LIMIT 1
    """

    results = client.query(customer_id, query)

    if not results.get('results'):
        return {}

    customer = results['results'][0].get('customer', {})
    return {
        'id': customer.get('id'),
        'name': customer.get('descriptiveName'),
        'currency': customer.get('currencyCode'),
        'timezone': customer.get('timeZone'),
        'is_manager': customer.get('manager', False)
    }


def get_account_currency(client: GoogleAdsClient, customer_id: str) -> str:
    """
    Get the currency code for an account.

    Args:
        client: Google Ads client
        customer_id: The customer ID

    Returns:
        Currency code (e.g., 'USD', 'EUR')
    """
    info = get_account_info(client, customer_id)
    return info.get('currency', 'Unknown')


def health_check(client: GoogleAdsClient) -> Dict[str, Any]:
    """
    Check if the API connection is working.

    Returns:
        Dict with status and accessible accounts
    """
    try:
        accounts = list_accounts(client)
        return {
            'status': 'ok',
            'accessible_accounts': len(accounts),
            'accounts': accounts
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
