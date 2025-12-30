"""
Campaign Tools

Functions for Google Ads campaign operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Optional
from api_client import GoogleAdsClient, format_customer_id


def list_campaigns(
    client: GoogleAdsClient,
    customer_id: str,
    status_filter: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    List campaigns in an account.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        status_filter: Optional status filter (ENABLED, PAUSED, REMOVED)
        limit: Maximum number of campaigns to return

    Returns:
        List of campaign dicts
    """
    where_clause = ""
    if status_filter:
        where_clause = f"WHERE campaign.status = '{status_filter.upper()}'"

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.start_date,
            campaign.end_date
        FROM campaign
        {where_clause}
        ORDER BY campaign.name
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    campaigns = []
    for result in results.get('results', []):
        campaign = result.get('campaign', {})
        campaigns.append({
            'id': campaign.get('id'),
            'name': campaign.get('name'),
            'status': campaign.get('status'),
            'channel_type': campaign.get('advertisingChannelType'),
            'start_date': campaign.get('startDate'),
            'end_date': campaign.get('endDate')
        })

    return campaigns


def get_campaign(client: GoogleAdsClient, customer_id: str, campaign_id: str) -> Dict[str, Any]:
    """
    Get details for a specific campaign.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        campaign_id: The campaign ID

    Returns:
        Campaign dict
    """
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.start_date,
            campaign.end_date,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.id = {campaign_id}
        LIMIT 1
    """

    results = client.query(customer_id, query)

    if not results.get('results'):
        return {}

    result = results['results'][0]
    campaign = result.get('campaign', {})
    budget = result.get('campaignBudget', {})

    return {
        'id': campaign.get('id'),
        'name': campaign.get('name'),
        'status': campaign.get('status'),
        'channel_type': campaign.get('advertisingChannelType'),
        'start_date': campaign.get('startDate'),
        'end_date': campaign.get('endDate'),
        'bidding_strategy': campaign.get('biddingStrategyType'),
        'budget_micros': budget.get('amountMicros')
    }


def get_campaign_performance(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get campaign performance metrics.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum campaigns to return

    Returns:
        List of campaign performance dicts
    """
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    campaigns = []
    for result in results.get('results', []):
        campaign = result.get('campaign', {})
        metrics = result.get('metrics', {})
        campaigns.append({
            'id': campaign.get('id'),
            'name': campaign.get('name'),
            'status': campaign.get('status'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'conversions': float(metrics.get('conversions', 0)),
            'average_cpc': int(metrics.get('averageCpc', 0))
        })

    return campaigns
