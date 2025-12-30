"""
Asset Tools

Functions for Google Ads asset operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any, Optional
from api_client import GoogleAdsClient


def get_image_assets(
    client: GoogleAdsClient,
    customer_id: str,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get image assets in an account.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        limit: Maximum assets to return

    Returns:
        List of image asset dicts
    """
    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.type,
            asset.image_asset.full_size.url,
            asset.image_asset.full_size.height_pixels,
            asset.image_asset.full_size.width_pixels,
            asset.image_asset.file_size
        FROM asset
        WHERE asset.type = 'IMAGE'
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    assets = []
    for result in results.get('results', []):
        asset = result.get('asset', {})
        image_asset = asset.get('imageAsset', {})
        full_size = image_asset.get('fullSize', {})

        assets.append({
            'id': asset.get('id'),
            'name': asset.get('name'),
            'type': asset.get('type'),
            'url': full_size.get('url'),
            'width': full_size.get('widthPixels'),
            'height': full_size.get('heightPixels'),
            'file_size': image_asset.get('fileSize')
        })

    return assets


def get_violating_assets(
    client: GoogleAdsClient,
    customer_id: str,
    asset_type: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get assets with policy violations.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        asset_type: Optional asset type filter (IMAGE, TEXT, VIDEO)
        limit: Maximum assets to return

    Returns:
        List of violating asset dicts
    """
    where_conditions = ["asset.policy_summary.approval_status != 'APPROVED'"]
    if asset_type:
        where_conditions.append(f"asset.type = '{asset_type.upper()}'")

    where_clause = " AND ".join(where_conditions)

    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.type,
            asset.policy_summary.approval_status,
            asset.policy_summary.review_status
        FROM asset
        WHERE {where_clause}
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    assets = []
    for result in results.get('results', []):
        asset = result.get('asset', {})
        policy_summary = asset.get('policySummary', {})

        assets.append({
            'id': asset.get('id'),
            'name': asset.get('name'),
            'type': asset.get('type'),
            'approval_status': policy_summary.get('approvalStatus'),
            'review_status': policy_summary.get('reviewStatus')
        })

    return assets


def get_linked_assets(
    client: GoogleAdsClient,
    customer_id: str,
    asset_type: Optional[str] = None,
    link_level: str = "all"
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get assets linked to campaigns and ad groups.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        asset_type: Optional asset type filter
        link_level: 'campaign', 'ad_group', or 'all'

    Returns:
        Dict with 'campaign' and 'ad_group' level assets
    """
    result = {'campaign': [], 'ad_group': []}

    where_clause = ""
    if asset_type:
        where_clause = f"WHERE asset.type = '{asset_type.upper()}'"

    # Campaign-level assets
    if link_level in ["campaign", "all"]:
        campaign_query = f"""
            SELECT
                asset.id,
                asset.name,
                asset.type,
                campaign.id,
                campaign.name,
                campaign_asset.field_type,
                campaign_asset.status
            FROM campaign_asset
            {where_clause}
            LIMIT 200
        """

        try:
            results = client.query(customer_id, campaign_query)
            for r in results.get('results', []):
                asset = r.get('asset', {})
                campaign = r.get('campaign', {})
                campaign_asset = r.get('campaignAsset', {})

                result['campaign'].append({
                    'asset_id': asset.get('id'),
                    'asset_name': asset.get('name'),
                    'asset_type': asset.get('type'),
                    'campaign_id': campaign.get('id'),
                    'campaign_name': campaign.get('name'),
                    'field_type': campaign_asset.get('fieldType'),
                    'status': campaign_asset.get('status')
                })
        except Exception:
            pass  # Campaign assets query failed

    # Ad group-level assets
    if link_level in ["ad_group", "all"]:
        ad_group_query = f"""
            SELECT
                asset.id,
                asset.name,
                asset.type,
                ad_group.id,
                ad_group.name,
                ad_group_asset.field_type,
                ad_group_asset.status
            FROM ad_group_asset
            {where_clause}
            LIMIT 200
        """

        try:
            results = client.query(customer_id, ad_group_query)
            for r in results.get('results', []):
                asset = r.get('asset', {})
                ad_group = r.get('adGroup', {})
                ad_group_asset = r.get('adGroupAsset', {})

                result['ad_group'].append({
                    'asset_id': asset.get('id'),
                    'asset_name': asset.get('name'),
                    'asset_type': asset.get('type'),
                    'ad_group_id': ad_group.get('id'),
                    'ad_group_name': ad_group.get('name'),
                    'field_type': ad_group_asset.get('fieldType'),
                    'status': ad_group_asset.get('status')
                })
        except Exception:
            pass  # Ad group assets query failed

    return result


def get_asset_performance(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 200
) -> List[Dict[str, Any]]:
    """
    Get image asset performance metrics.

    Args:
        client: Google Ads client
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum assets to return

    Returns:
        List of asset performance dicts
    """
    query = f"""
        SELECT
            asset.id,
            asset.name,
            asset.image_asset.full_size.url,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM campaign_asset
        WHERE
            asset.type = 'IMAGE'
            AND segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT {limit}
    """

    results = client.query(customer_id, query)

    assets = []
    for result in results.get('results', []):
        asset = result.get('asset', {})
        campaign = result.get('campaign', {})
        metrics = result.get('metrics', {})

        assets.append({
            'id': asset.get('id'),
            'name': asset.get('name'),
            'url': asset.get('imageAsset', {}).get('fullSize', {}).get('url'),
            'campaign_name': campaign.get('name'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'conversions': float(metrics.get('conversions', 0)),
            'cost_micros': int(metrics.get('costMicros', 0))
        })

    return assets
