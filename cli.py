#!/usr/bin/env python3
"""
Google Ads CLI

Command-line interface for Google Ads operations.
Uses the same tools as the MCP server.

Usage:
    google-ads accounts                    List accessible accounts
    google-ads account <id>                Get account info
    google-ads campaigns list <id>         List campaigns
    google-ads campaigns get <id> <cid>    Get campaign details
    google-ads ad-groups list <id>         List ad groups
    google-ads assets list <id>            List image assets
    google-ads assets violating <id>       List assets with policy violations
    google-ads assets linked <id>          List linked assets
    google-ads performance <id>            Get campaign performance
    google-ads health                      Check API connection
"""

import argparse
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from api_client import create_client
from tools import accounts, campaigns, ad_groups, assets


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))


def print_table(data, columns):
    """Print data as a simple table."""
    if not data:
        print("No results found.")
        return

    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in data:
        for col in columns:
            val = str(row.get(col, ''))
            widths[col] = max(widths[col], len(val))

    # Print header
    header = " | ".join(f"{col:<{widths[col]}}" for col in columns)
    print(header)
    print("-" * len(header))

    # Print rows
    for row in data:
        line = " | ".join(f"{str(row.get(col, '')):<{widths[col]}}" for col in columns)
        print(line)


def cmd_accounts(args):
    """List accessible accounts."""
    client = create_client()
    account_list = accounts.list_accounts(client)

    if args.json:
        print_json(account_list)
    else:
        print("Accessible Google Ads Accounts:")
        print("-" * 40)
        for acc in account_list:
            print(f"  {acc}")
        print(f"\nTotal: {len(account_list)} accounts")


def cmd_account_info(args):
    """Get account info."""
    client = create_client()
    info = accounts.get_account_info(client, args.customer_id)

    if args.json:
        print_json(info)
    else:
        print(f"Account: {info.get('name', 'N/A')}")
        print(f"ID: {info.get('id', 'N/A')}")
        print(f"Currency: {info.get('currency', 'N/A')}")
        print(f"Timezone: {info.get('timezone', 'N/A')}")
        print(f"Manager: {info.get('is_manager', False)}")


def cmd_campaigns_list(args):
    """List campaigns."""
    client = create_client()
    campaign_list = campaigns.list_campaigns(
        client,
        args.customer_id,
        status_filter=args.status,
        limit=args.limit
    )

    if args.json:
        print_json(campaign_list)
    else:
        print_table(campaign_list, ['id', 'name', 'status', 'channel_type'])


def cmd_campaigns_get(args):
    """Get campaign details."""
    client = create_client()
    campaign = campaigns.get_campaign(client, args.customer_id, args.campaign_id)

    if args.json:
        print_json(campaign)
    else:
        for key, value in campaign.items():
            print(f"{key}: {value}")


def cmd_campaigns_performance(args):
    """Get campaign performance."""
    client = create_client()
    perf = campaigns.get_campaign_performance(
        client,
        args.customer_id,
        days=args.days,
        limit=args.limit
    )

    if args.json:
        print_json(perf)
    else:
        print_table(perf, ['id', 'name', 'status', 'impressions', 'clicks', 'cost_micros', 'conversions'])


def cmd_ad_groups_list(args):
    """List ad groups."""
    client = create_client()
    ag_list = ad_groups.list_ad_groups(
        client,
        args.customer_id,
        campaign_id=args.campaign_id,
        status_filter=args.status,
        limit=args.limit
    )

    if args.json:
        print_json(ag_list)
    else:
        print_table(ag_list, ['id', 'name', 'status', 'type', 'campaign_name'])


def cmd_ad_groups_get(args):
    """Get ad group details."""
    client = create_client()
    ag = ad_groups.get_ad_group(client, args.customer_id, args.ad_group_id)

    if args.json:
        print_json(ag)
    else:
        for key, value in ag.items():
            print(f"{key}: {value}")


def cmd_assets_list(args):
    """List image assets."""
    client = create_client()
    asset_list = assets.get_image_assets(client, args.customer_id, limit=args.limit)

    if args.json:
        print_json(asset_list)
    else:
        print_table(asset_list, ['id', 'name', 'width', 'height'])


def cmd_assets_violating(args):
    """List assets with policy violations."""
    client = create_client()
    asset_list = assets.get_violating_assets(
        client,
        args.customer_id,
        asset_type=args.type,
        limit=args.limit
    )

    if args.json:
        print_json(asset_list)
    else:
        if not asset_list:
            print("No assets with policy violations found.")
        else:
            print_table(asset_list, ['id', 'name', 'type', 'approval_status', 'review_status'])


def cmd_assets_linked(args):
    """List linked assets."""
    client = create_client()
    linked = assets.get_linked_assets(
        client,
        args.customer_id,
        asset_type=args.type,
        link_level=args.level
    )

    if args.json:
        print_json(linked)
    else:
        if linked.get('campaign'):
            print("\nCampaign-Level Assets:")
            print_table(linked['campaign'], ['asset_id', 'asset_name', 'asset_type', 'campaign_name', 'field_type', 'status'])

        if linked.get('ad_group'):
            print("\nAd Group-Level Assets:")
            print_table(linked['ad_group'], ['asset_id', 'asset_name', 'asset_type', 'ad_group_name', 'field_type', 'status'])


def cmd_health(args):
    """Check API health."""
    client = create_client()
    result = accounts.health_check(client)

    if args.json:
        print_json(result)
    else:
        if result['status'] == 'ok':
            print(f"Status: OK")
            print(f"Accessible accounts: {result['accessible_accounts']}")
        else:
            print(f"Status: ERROR")
            print(f"Error: {result.get('error', 'Unknown')}")


def main():
    parser = argparse.ArgumentParser(
        description='Google Ads CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # accounts
    accounts_parser = subparsers.add_parser('accounts', help='List accessible accounts')
    accounts_parser.set_defaults(func=cmd_accounts)

    # account
    account_parser = subparsers.add_parser('account', help='Get account info')
    account_parser.add_argument('customer_id', help='Customer ID')
    account_parser.set_defaults(func=cmd_account_info)

    # campaigns
    campaigns_parser = subparsers.add_parser('campaigns', help='Campaign operations')
    campaigns_sub = campaigns_parser.add_subparsers(dest='campaigns_command')

    campaigns_list = campaigns_sub.add_parser('list', help='List campaigns')
    campaigns_list.add_argument('customer_id', help='Customer ID')
    campaigns_list.add_argument('--status', choices=['ENABLED', 'PAUSED', 'REMOVED'], help='Filter by status')
    campaigns_list.add_argument('--limit', type=int, default=100, help='Maximum results')
    campaigns_list.set_defaults(func=cmd_campaigns_list)

    campaigns_get = campaigns_sub.add_parser('get', help='Get campaign details')
    campaigns_get.add_argument('customer_id', help='Customer ID')
    campaigns_get.add_argument('campaign_id', help='Campaign ID')
    campaigns_get.set_defaults(func=cmd_campaigns_get)

    campaigns_perf = campaigns_sub.add_parser('performance', help='Get campaign performance')
    campaigns_perf.add_argument('customer_id', help='Customer ID')
    campaigns_perf.add_argument('--days', type=int, default=30, help='Days to look back')
    campaigns_perf.add_argument('--limit', type=int, default=50, help='Maximum results')
    campaigns_perf.set_defaults(func=cmd_campaigns_performance)

    # ad-groups
    ad_groups_parser = subparsers.add_parser('ad-groups', help='Ad group operations')
    ad_groups_sub = ad_groups_parser.add_subparsers(dest='ad_groups_command')

    ad_groups_list = ad_groups_sub.add_parser('list', help='List ad groups')
    ad_groups_list.add_argument('customer_id', help='Customer ID')
    ad_groups_list.add_argument('--campaign-id', help='Filter by campaign ID')
    ad_groups_list.add_argument('--status', choices=['ENABLED', 'PAUSED', 'REMOVED'], help='Filter by status')
    ad_groups_list.add_argument('--limit', type=int, default=100, help='Maximum results')
    ad_groups_list.set_defaults(func=cmd_ad_groups_list)

    ad_groups_get = ad_groups_sub.add_parser('get', help='Get ad group details')
    ad_groups_get.add_argument('customer_id', help='Customer ID')
    ad_groups_get.add_argument('ad_group_id', help='Ad Group ID')
    ad_groups_get.set_defaults(func=cmd_ad_groups_get)

    # assets
    assets_parser = subparsers.add_parser('assets', help='Asset operations')
    assets_sub = assets_parser.add_subparsers(dest='assets_command')

    assets_list = assets_sub.add_parser('list', help='List image assets')
    assets_list.add_argument('customer_id', help='Customer ID')
    assets_list.add_argument('--limit', type=int, default=50, help='Maximum results')
    assets_list.set_defaults(func=cmd_assets_list)

    assets_violating = assets_sub.add_parser('violating', help='List assets with policy violations')
    assets_violating.add_argument('customer_id', help='Customer ID')
    assets_violating.add_argument('--type', choices=['IMAGE', 'TEXT', 'VIDEO'], help='Filter by asset type')
    assets_violating.add_argument('--limit', type=int, default=100, help='Maximum results')
    assets_violating.set_defaults(func=cmd_assets_violating)

    assets_linked = assets_sub.add_parser('linked', help='List linked assets')
    assets_linked.add_argument('customer_id', help='Customer ID')
    assets_linked.add_argument('--type', choices=['IMAGE', 'TEXT', 'VIDEO'], help='Filter by asset type')
    assets_linked.add_argument('--level', choices=['campaign', 'ad_group', 'all'], default='all', help='Link level')
    assets_linked.set_defaults(func=cmd_assets_linked)

    # health
    health_parser = subparsers.add_parser('health', help='Check API connection')
    health_parser.set_defaults(func=cmd_health)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if hasattr(args, 'func'):
        try:
            args.func(args)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
