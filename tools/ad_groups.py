"""
Ad Group Tools

Functions for Google Ads ad group operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Optional
from api_client import GoogleAdsClient


def list_ad_groups(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    List ad groups in an account.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        campaign_id: Optional campaign ID to filter by
        status_filter: Optional status filter (ENABLED, PAUSED, REMOVED)
        limit: Maximum number of ad groups to return

    Returns:
        List of ad group dicts
    """
    where_conditions = []
    if campaign_id:
        where_conditions.append(f"campaign.id = {campaign_id}")
    if status_filter:
        where_conditions.append(f"ad_group.status = '{status_filter.upper()}'")

    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)

    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            campaign.id,
            campaign.name,
            campaign.status
        FROM ad_group
        {where_clause}
        ORDER BY campaign.name, ad_group.name
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    ad_groups = []
    for result in results.get('results', []):
        ad_group = result.get('adGroup', {})
        campaign = result.get('campaign', {})
        ad_groups.append({
            'id': ad_group.get('id'),
            'name': ad_group.get('name'),
            'status': ad_group.get('status'),
            'type': ad_group.get('type'),
            'campaign_id': campaign.get('id'),
            'campaign_name': campaign.get('name'),
            'campaign_status': campaign.get('status')
        })

    return ad_groups


def get_ad_group(
    client: GoogleAdsClient,
    customer_id: str,
    ad_group_id: str
) -> Dict[str, Any]:
    """
    Get details for a specific ad group.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        ad_group_id: The ad group ID

    Returns:
        Ad group dict
    """
    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            ad_group.cpc_bid_micros,
            campaign.id,
            campaign.name
        FROM ad_group
        WHERE ad_group.id = {ad_group_id}
        LIMIT 1
    """

    results = client.query(customer_id, query)

    if not results.get('results'):
        return {}

    result = results['results'][0]
    ad_group = result.get('adGroup', {})
    campaign = result.get('campaign', {})

    return {
        'id': ad_group.get('id'),
        'name': ad_group.get('name'),
        'status': ad_group.get('status'),
        'type': ad_group.get('type'),
        'cpc_bid_micros': ad_group.get('cpcBidMicros'),
        'campaign_id': campaign.get('id'),
        'campaign_name': campaign.get('name')
    }


def get_ad_group_performance(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    campaign_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get ad group performance metrics.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        days: Number of days to look back
        campaign_id: Optional campaign ID filter
        limit: Maximum ad groups to return

    Returns:
        List of ad group performance dicts
    """
    where_clause = f"segments.date DURING LAST_{days}_DAYS"
    if campaign_id:
        where_clause += f" AND campaign.id = {campaign_id}"

    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM ad_group
        WHERE {where_clause}
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    ad_groups = []
    for result in results.get('results', []):
        ad_group = result.get('adGroup', {})
        campaign = result.get('campaign', {})
        metrics = result.get('metrics', {})
        ad_groups.append({
            'id': ad_group.get('id'),
            'name': ad_group.get('name'),
            'status': ad_group.get('status'),
            'campaign_name': campaign.get('name'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'conversions': float(metrics.get('conversions', 0))
        })

    return ad_groups
