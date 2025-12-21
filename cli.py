#!/usr/bin/env python3
"""
Google Ads CLI

Command-line interface for Google Ads operations.
Uses the same tools as the MCP server.

Usage:
    google-ads accounts                     List accessible accounts
    google-ads account <id> info            Get account info
    google-ads campaigns list <id>          List campaigns
    google-ads performance <id>             Get campaign performance
    google-ads health                       Check API connection
"""

import argparse
import asyncio
import json
import sys
from typing import Any

from tools import (
    create_client,
    list_accounts,
    get_account_info,
    get_account_currency,
    health_check,
    list_campaigns,
    get_campaign,
    get_campaign_performance,
    get_ad_performance,
    get_ad_creatives,
    list_ad_groups,
    execute_gaql_query,
    run_gaql,
    get_keyword_performance,
    get_search_terms_report,
    get_budget_report,
    get_conversion_report,
)


def print_json(data: Any):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_table(data: list, fields: list = None):
    """Print data as a simple table."""
    if not data:
        print("No data found.")
        return

    if fields is None:
        fields = list(data[0].keys())

    # Calculate column widths
    widths = {f: len(f) for f in fields}
    for row in data:
        for f in fields:
            widths[f] = max(widths[f], len(str(row.get(f, ''))))

    # Print header
    header = " | ".join(f"{f:{widths[f]}}" for f in fields)
    print(header)
    print("-" * len(header))

    # Print rows
    for row in data:
        values = [f"{str(row.get(f, '')):{widths[f]}}" for f in fields]
        print(" | ".join(values))


async def cmd_accounts(args, client):
    """List accessible accounts."""
    accounts = await list_accounts(client)
    if args.json:
        print_json({'accounts': accounts})
    else:
        print("Accessible Google Ads Accounts:")
        print("-" * 40)
        for account_id in accounts:
            print(f"  {account_id}")


async def cmd_account_info(args, client):
    """Get account info."""
    info = await get_account_info(client, args.customer_id)
    if args.json:
        print_json(info)
    else:
        print(f"Account Information for {args.customer_id}:")
        print("-" * 40)
        for key, value in info.items():
            print(f"  {key}: {value}")


async def cmd_account_currency(args, client):
    """Get account currency."""
    currency = await get_account_currency(client, args.customer_id)
    if args.json:
        print_json({'currency': currency})
    else:
        print(f"Account {args.customer_id} currency: {currency}")


async def cmd_campaigns_list(args, client):
    """List campaigns."""
    campaigns = await list_campaigns(
        client,
        args.customer_id,
        status_filter=args.status,
        limit=args.limit or 50,
    )
    if args.json:
        print_json(campaigns)
    else:
        print_table(campaigns, ['id', 'name', 'status', 'channel_type'])


async def cmd_campaigns_get(args, client):
    """Get campaign details."""
    campaign = await get_campaign(client, args.customer_id, args.campaign_id)
    if args.json:
        print_json(campaign)
    else:
        print(f"Campaign {args.campaign_id}:")
        print("-" * 40)
        for key, value in campaign.items():
            print(f"  {key}: {value}")


async def cmd_performance(args, client):
    """Get campaign performance."""
    data = await get_campaign_performance(
        client,
        args.customer_id,
        days=args.days or 30,
        limit=args.limit or 50,
    )
    if args.json:
        print_json(data)
    else:
        print_table(data, ['name', 'status', 'impressions', 'clicks', 'cost_micros', 'conversions'])


async def cmd_ads_performance(args, client):
    """Get ad performance."""
    data = await get_ad_performance(
        client,
        args.customer_id,
        days=args.days or 30,
        limit=args.limit or 50,
    )
    if args.json:
        print_json(data)
    else:
        print_table(data, ['name', 'campaign_name', 'impressions', 'clicks', 'conversions'])


async def cmd_ads_creatives(args, client):
    """Get ad creatives."""
    data = await get_ad_creatives(client, args.customer_id, limit=args.limit or 50)
    if args.json:
        print_json(data)
    else:
        for ad in data:
            print(f"\nAd ID: {ad['id']}")
            print(f"  Campaign: {ad['campaign_name']}")
            print(f"  Ad Group: {ad['ad_group_name']}")
            print(f"  Status: {ad['status']}")
            if ad['headlines']:
                print(f"  Headlines: {', '.join(ad['headlines'][:3])}")
            if ad['descriptions']:
                print(f"  Descriptions: {', '.join(ad['descriptions'][:2])}")


async def cmd_ad_groups(args, client):
    """List ad groups."""
    data = await list_ad_groups(
        client,
        args.customer_id,
        campaign_id=args.campaign_id,
        limit=args.limit or 50,
    )
    if args.json:
        print_json(data)
    else:
        print_table(data, ['id', 'name', 'status', 'campaign_name'])


async def cmd_gaql(args, client):
    """Run GAQL query."""
    if args.format == 'json':
        result = await run_gaql(client, args.customer_id, args.query, 'json')
        print(result)
    elif args.format == 'csv':
        result = await run_gaql(client, args.customer_id, args.query, 'csv')
        print(result)
    elif args.format == 'table':
        result = await run_gaql(client, args.customer_id, args.query, 'table')
        print(result)
    else:
        result = await execute_gaql_query(client, args.customer_id, args.query)
        print_json(result)


async def cmd_keywords(args, client):
    """Get keyword performance."""
    data = await get_keyword_performance(
        client,
        args.customer_id,
        days=args.days or 30,
        limit=args.limit or 50,
    )
    if args.json:
        print_json(data)
    else:
        print_table(data, ['keyword', 'match_type', 'impressions', 'clicks', 'conversions'])


async def cmd_search_terms(args, client):
    """Get search terms report."""
    data = await get_search_terms_report(
        client,
        args.customer_id,
        days=args.days or 30,
        limit=args.limit or 100,
    )
    if args.json:
        print_json(data)
    else:
        print_table(data, ['search_term', 'campaign_name', 'impressions', 'clicks'])


async def cmd_budgets(args, client):
    """Get budget report."""
    data = await get_budget_report(client, args.customer_id)
    if args.json:
        print_json(data)
    else:
        print_table(data, ['campaign_name', 'campaign_status', 'daily_budget_micros'])


async def cmd_conversions(args, client):
    """Get conversion report."""
    data = await get_conversion_report(
        client,
        args.customer_id,
        days=args.days or 30,
        limit=args.limit or 50,
    )
    if args.json:
        print_json(data)
    else:
        print_table(data, ['campaign_name', 'conversions', 'conversions_value', 'cost_per_conversion'])


async def cmd_health(args, client):
    """Health check."""
    result = await health_check(client)
    if args.json:
        print_json(result)
    else:
        print(f"Status: {result['status']}")
        if result['status'] == 'healthy':
            print(f"Accounts accessible: {result['accounts_accessible']}")


def main():
    parser = argparse.ArgumentParser(
        description='Google Ads CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    google-ads accounts                              List all accessible accounts
    google-ads account 1234567890 info               Get account info
    google-ads campaigns list 1234567890             List campaigns
    google-ads performance 1234567890 --days 14      Get 14-day performance
    google-ads gaql 1234567890 "SELECT ..."          Run GAQL query
    google-ads health                                Check API health
        """
    )
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    subparsers = parser.add_subparsers(dest='command', help='Command')

    # accounts
    subparsers.add_parser('accounts', help='List accessible accounts')

    # account
    p = subparsers.add_parser('account', help='Account operations')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('action', choices=['info', 'currency'], help='Action')

    # campaigns
    p = subparsers.add_parser('campaigns', help='Campaign operations')
    p.add_argument('action', choices=['list', 'get'], help='Action')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--campaign-id', help='Campaign ID (for get)')
    p.add_argument('--status', help='Filter by status')
    p.add_argument('--limit', type=int, help='Max results')

    # performance
    p = subparsers.add_parser('performance', help='Campaign performance')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--days', type=int, default=30, help='Days to look back')
    p.add_argument('--limit', type=int, help='Max results')

    # ads
    p = subparsers.add_parser('ads', help='Ad operations')
    p.add_argument('action', choices=['performance', 'creatives'], help='Action')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--days', type=int, default=30, help='Days to look back')
    p.add_argument('--limit', type=int, help='Max results')

    # ad-groups
    p = subparsers.add_parser('ad-groups', help='Ad group operations')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--campaign-id', help='Filter by campaign')
    p.add_argument('--limit', type=int, help='Max results')

    # gaql
    p = subparsers.add_parser('gaql', help='Run GAQL query')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('query', help='GAQL query string')
    p.add_argument('--format', choices=['json', 'csv', 'table', 'dict'], default='dict')

    # keywords
    p = subparsers.add_parser('keywords', help='Keyword performance')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--days', type=int, default=30, help='Days to look back')
    p.add_argument('--limit', type=int, help='Max results')

    # search-terms
    p = subparsers.add_parser('search-terms', help='Search terms report')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--days', type=int, default=30, help='Days to look back')
    p.add_argument('--limit', type=int, help='Max results')

    # budgets
    p = subparsers.add_parser('budgets', help='Budget report')
    p.add_argument('customer_id', help='Customer ID')

    # conversions
    p = subparsers.add_parser('conversions', help='Conversion report')
    p.add_argument('customer_id', help='Customer ID')
    p.add_argument('--days', type=int, default=30, help='Days to look back')
    p.add_argument('--limit', type=int, help='Max results')

    # health
    subparsers.add_parser('health', help='Check API health')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Create client
    client = create_client()

    # Run command
    try:
        if args.command == 'accounts':
            asyncio.run(cmd_accounts(args, client))
        elif args.command == 'account':
            if args.action == 'info':
                asyncio.run(cmd_account_info(args, client))
            elif args.action == 'currency':
                asyncio.run(cmd_account_currency(args, client))
        elif args.command == 'campaigns':
            if args.action == 'list':
                asyncio.run(cmd_campaigns_list(args, client))
            elif args.action == 'get':
                if not args.campaign_id:
                    print("Error: --campaign-id required for 'get' action")
                    sys.exit(1)
                asyncio.run(cmd_campaigns_get(args, client))
        elif args.command == 'performance':
            asyncio.run(cmd_performance(args, client))
        elif args.command == 'ads':
            if args.action == 'performance':
                asyncio.run(cmd_ads_performance(args, client))
            elif args.action == 'creatives':
                asyncio.run(cmd_ads_creatives(args, client))
        elif args.command == 'ad-groups':
            asyncio.run(cmd_ad_groups(args, client))
        elif args.command == 'gaql':
            asyncio.run(cmd_gaql(args, client))
        elif args.command == 'keywords':
            asyncio.run(cmd_keywords(args, client))
        elif args.command == 'search-terms':
            asyncio.run(cmd_search_terms(args, client))
        elif args.command == 'budgets':
            asyncio.run(cmd_budgets(args, client))
        elif args.command == 'conversions':
            asyncio.run(cmd_conversions(args, client))
        elif args.command == 'health':
            asyncio.run(cmd_health(args, client))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
