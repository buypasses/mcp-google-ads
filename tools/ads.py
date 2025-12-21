"""
Ad Tools

Pure functions for Google Ads ad and ad group operations.
"""

from typing import Dict, List, Any

from .client import GoogleAdsClient


async def get_ad_performance(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get ad performance metrics.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of ad performance data
    """
    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.status,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM ad_group_ad
        WHERE segments.date DURING LAST_{days}DAYS
        ORDER BY metrics.impressions DESC
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    ads = []
    for row in result.get('results', []):
        ad = row.get('adGroupAd', {}).get('ad', {})
        ad_status = row.get('adGroupAd', {}).get('status')
        campaign = row.get('campaign', {})
        ad_group = row.get('adGroup', {})
        metrics = row.get('metrics', {})

        ads.append({
            'id': ad.get('id'),
            'name': ad.get('name'),
            'status': ad_status,
            'campaign_name': campaign.get('name'),
            'ad_group_name': ad_group.get('name'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'conversions': float(metrics.get('conversions', 0)),
        })

    return ads


async def get_ad_creatives(
    client: GoogleAdsClient,
    customer_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get ad creative details including headlines and descriptions.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        limit: Maximum number of results

    Returns:
        List of ad creative data
    """
    query = f"""
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad.ad.name,
            ad_group_ad.ad.type,
            ad_group_ad.ad.final_urls,
            ad_group_ad.status,
            ad_group_ad.ad.responsive_search_ad.headlines,
            ad_group_ad.ad.responsive_search_ad.descriptions,
            ad_group.name,
            campaign.name
        FROM ad_group_ad
        WHERE ad_group_ad.status != 'REMOVED'
        ORDER BY campaign.name, ad_group.name
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    creatives = []
    for row in result.get('results', []):
        ad = row.get('adGroupAd', {}).get('ad', {})
        ad_status = row.get('adGroupAd', {}).get('status')
        campaign = row.get('campaign', {})
        ad_group = row.get('adGroup', {})
        rsa = ad.get('responsiveSearchAd', {})

        headlines = []
        if rsa.get('headlines'):
            headlines = [h.get('text', '') for h in rsa['headlines']]

        descriptions = []
        if rsa.get('descriptions'):
            descriptions = [d.get('text', '') for d in rsa['descriptions']]

        creatives.append({
            'id': ad.get('id'),
            'name': ad.get('name'),
            'type': ad.get('type'),
            'status': ad_status,
            'campaign_name': campaign.get('name'),
            'ad_group_name': ad_group.get('name'),
            'final_urls': ad.get('finalUrls', []),
            'headlines': headlines,
            'descriptions': descriptions,
        })

    return creatives


async def list_ad_groups(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    List ad groups, optionally filtered by campaign.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        campaign_id: Optional campaign ID to filter by
        limit: Maximum number of results

    Returns:
        List of ad group data
    """
    where_clause = ""
    if campaign_id:
        where_clause = f"WHERE campaign.id = {campaign_id}"

    query = f"""
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            campaign.id,
            campaign.name
        FROM ad_group
        {where_clause}
        ORDER BY campaign.name, ad_group.name
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    ad_groups = []
    for row in result.get('results', []):
        ad_group = row.get('adGroup', {})
        campaign = row.get('campaign', {})

        ad_groups.append({
            'id': ad_group.get('id'),
            'name': ad_group.get('name'),
            'status': ad_group.get('status'),
            'type': ad_group.get('type'),
            'campaign_id': campaign.get('id'),
            'campaign_name': campaign.get('name'),
        })

    return ad_groups
