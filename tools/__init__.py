"""
Google Ads Tools

Pure functions for Google Ads API operations.
These tools can be used by the MCP server, CLI, or any other project.

Usage:
    from tools import create_client, list_accounts, get_campaign_performance

    client = create_client(credentials_path='/path/to/creds.json')
    accounts = await list_accounts(client)
"""

from .client import (
    GoogleAdsClient,
    create_client,
    format_customer_id,
)
from .accounts import (
    list_accounts,
    get_account_currency,
    get_account_info,
    health_check,
)
from .campaigns import (
    list_campaigns,
    get_campaign,
    get_campaign_performance,
    create_campaign,
    update_campaign_status,
)
from .ads import (
    get_ad_performance,
    get_ad_creatives,
    list_ad_groups,
)
from .gaql import (
    execute_gaql_query,
    run_gaql,
)
from .reporting import (
    get_keyword_performance,
    get_search_terms_report,
    get_budget_report,
    get_conversion_report,
)

__all__ = [
    # Client
    'GoogleAdsClient',
    'create_client',
    'format_customer_id',
    # Accounts
    'list_accounts',
    'get_account_currency',
    'get_account_info',
    'health_check',
    # Campaigns
    'list_campaigns',
    'get_campaign',
    'get_campaign_performance',
    'create_campaign',
    'update_campaign_status',
    # Ads
    'get_ad_performance',
    'get_ad_creatives',
    'list_ad_groups',
    # GAQL
    'execute_gaql_query',
    'run_gaql',
    # Reporting
    'get_keyword_performance',
    'get_search_terms_report',
    'get_budget_report',
    'get_conversion_report',
]
