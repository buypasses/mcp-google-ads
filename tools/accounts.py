"""
Account Tools

Pure functions for Google Ads account operations.
"""

from typing import Dict, List, Any

from .client import GoogleAdsClient, format_customer_id


async def list_accounts(client: GoogleAdsClient) -> List[str]:
    """
    List all accessible Google Ads accounts.

    Args:
        client: Google Ads client instance

    Returns:
        List of customer IDs
    """
    result = client.get("customers:listAccessibleCustomers")

    if not result.get('resourceNames'):
        return []

    customer_ids = []
    for resource_name in result['resourceNames']:
        customer_id = resource_name.split('/')[-1]
        customer_ids.append(format_customer_id(customer_id))

    return customer_ids


async def get_account_currency(
    client: GoogleAdsClient,
    customer_id: str,
) -> str:
    """
    Get the currency code for a Google Ads account.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID

    Returns:
        Currency code (e.g., 'USD', 'EUR')
    """
    query = """
        SELECT
            customer.id,
            customer.currency_code
        FROM customer
        LIMIT 1
    """

    result = client.search(customer_id, query)

    if not result.get('results'):
        raise Exception(f"Account not found: {customer_id}")

    return result['results'][0].get('customer', {}).get('currencyCode', 'USD')


async def get_account_info(
    client: GoogleAdsClient,
    customer_id: str,
) -> Dict[str, Any]:
    """
    Get detailed account information.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID

    Returns:
        Account details including name, currency, timezone, etc.
    """
    query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone,
            customer.auto_tagging_enabled,
            customer.manager
        FROM customer
        LIMIT 1
    """

    result = client.search(customer_id, query)

    if not result.get('results'):
        raise Exception(f"Account not found: {customer_id}")

    customer = result['results'][0].get('customer', {})
    return {
        'id': format_customer_id(customer_id),
        'name': customer.get('descriptiveName', 'N/A'),
        'currency': customer.get('currencyCode', 'USD'),
        'timezone': customer.get('timeZone', 'America/Los_Angeles'),
        'auto_tagging': customer.get('autoTaggingEnabled', False),
        'is_manager': customer.get('manager', False),
    }


async def health_check(client: GoogleAdsClient) -> Dict[str, Any]:
    """
    Check if the Google Ads API connection is healthy.

    Args:
        client: Google Ads client instance

    Returns:
        Health check status with account list
    """
    try:
        accounts = await list_accounts(client)
        return {
            'status': 'healthy',
            'accounts_accessible': len(accounts),
            'account_ids': accounts[:5],  # Limit to first 5
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
        }
