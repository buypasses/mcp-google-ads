"""
Reporting Tools

Pure functions for Google Ads reporting and analytics.
"""

from typing import Dict, List, Any

from .client import GoogleAdsClient
from .mock_data import MOCK_KEYWORDS, MOCK_SEARCH_TERMS, MOCK_BUDGETS, MOCK_CONVERSIONS


async def get_keyword_performance(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get keyword performance metrics.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of keyword performance data
    """
    if client.using_mock_data:
        keywords = []
        for row in MOCK_KEYWORDS[:limit]:
            keyword = row.get('adGroupCriterion', {}).get('keyword', {})
            campaign = row.get('campaign', {})
            ad_group = row.get('adGroup', {})
            metrics = row.get('metrics', {})
            keywords.append({
                'keyword': keyword.get('text'),
                'match_type': keyword.get('matchType'),
                'campaign_name': campaign.get('name'),
                'ad_group_name': ad_group.get('name'),
                'impressions': int(metrics.get('impressions', 0)),
                'clicks': int(metrics.get('clicks', 0)),
                'cost_micros': int(metrics.get('costMicros', 0)),
                'conversions': float(metrics.get('conversions', 0)),
                'ctr': float(metrics.get('ctr', 0)),
                'average_cpc': int(metrics.get('averageCpc', 0)),
            })
        return keywords

    query = f"""
        SELECT
            keyword_view.resource_name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group.name,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr,
            metrics.average_cpc
        FROM keyword_view
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    keywords = []
    for row in result.get('results', []):
        keyword = row.get('adGroupCriterion', {}).get('keyword', {})
        campaign = row.get('campaign', {})
        ad_group = row.get('adGroup', {})
        metrics = row.get('metrics', {})

        keywords.append({
            'keyword': keyword.get('text'),
            'match_type': keyword.get('matchType'),
            'campaign_name': campaign.get('name'),
            'ad_group_name': ad_group.get('name'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'conversions': float(metrics.get('conversions', 0)),
            'ctr': float(metrics.get('ctr', 0)),
            'average_cpc': int(metrics.get('averageCpc', 0)),
        })

    return keywords


async def get_search_terms_report(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get search terms report showing actual search queries.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of search term data
    """
    if client.using_mock_data:
        search_terms = []
        for row in MOCK_SEARCH_TERMS[:limit]:
            stv = row.get('searchTermView', {})
            campaign = row.get('campaign', {})
            ad_group = row.get('adGroup', {})
            metrics = row.get('metrics', {})
            search_terms.append({
                'search_term': stv.get('searchTerm'),
                'status': stv.get('status'),
                'campaign_name': campaign.get('name'),
                'ad_group_name': ad_group.get('name'),
                'impressions': int(metrics.get('impressions', 0)),
                'clicks': int(metrics.get('clicks', 0)),
                'cost_micros': int(metrics.get('costMicros', 0)),
                'conversions': float(metrics.get('conversions', 0)),
            })
        return search_terms

    query = f"""
        SELECT
            search_term_view.search_term,
            search_term_view.status,
            campaign.name,
            ad_group.name,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM search_term_view
        WHERE segments.date DURING LAST_{days}_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    search_terms = []
    for row in result.get('results', []):
        stv = row.get('searchTermView', {})
        campaign = row.get('campaign', {})
        ad_group = row.get('adGroup', {})
        metrics = row.get('metrics', {})

        search_terms.append({
            'search_term': stv.get('searchTerm'),
            'status': stv.get('status'),
            'campaign_name': campaign.get('name'),
            'ad_group_name': ad_group.get('name'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'conversions': float(metrics.get('conversions', 0)),
        })

    return search_terms


async def get_budget_report(
    client: GoogleAdsClient,
    customer_id: str,
) -> List[Dict[str, Any]]:
    """
    Get budget utilization report.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID

    Returns:
        List of budget data
    """
    if client.using_mock_data:
        budgets = []
        for row in MOCK_BUDGETS:
            campaign = row.get('campaign', {})
            budget = row.get('campaignBudget', {})
            budgets.append({
                'campaign_id': campaign.get('id'),
                'campaign_name': campaign.get('name'),
                'campaign_status': campaign.get('status'),
                'daily_budget_micros': int(budget.get('amountMicros', 0)),
                'total_budget_micros': budget.get('totalAmountMicros'),
                'budget_status': budget.get('status'),
                'delivery_method': budget.get('deliveryMethod'),
            })
        return budgets

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign_budget.amount_micros,
            campaign_budget.total_amount_micros,
            campaign_budget.status,
            campaign_budget.delivery_method
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
        LIMIT 50
    """

    result = client.search(customer_id, query)

    budgets = []
    for row in result.get('results', []):
        campaign = row.get('campaign', {})
        budget = row.get('campaignBudget', {})

        budgets.append({
            'campaign_id': campaign.get('id'),
            'campaign_name': campaign.get('name'),
            'campaign_status': campaign.get('status'),
            'daily_budget_micros': int(budget.get('amountMicros', 0)),
            'total_budget_micros': budget.get('totalAmountMicros'),
            'budget_status': budget.get('status'),
            'delivery_method': budget.get('deliveryMethod'),
        })

    return budgets


async def get_conversion_report(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get conversion performance report.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of conversion data by campaign
    """
    if client.using_mock_data:
        conversions = []
        for row in MOCK_CONVERSIONS[:limit]:
            campaign = row.get('campaign', {})
            metrics = row.get('metrics', {})
            conversions.append({
                'campaign_id': campaign.get('id'),
                'campaign_name': campaign.get('name'),
                'conversions': float(metrics.get('conversions', 0)),
                'conversions_value': float(metrics.get('conversionsValue', 0)),
                'cost_micros': int(metrics.get('costMicros', 0)),
                'cost_per_conversion': float(metrics.get('costPerConversion', 0)),
                'conversion_rate': float(metrics.get('conversionsFromInteractionsRate', 0)),
            })
        return conversions

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_micros,
            metrics.cost_per_conversion,
            metrics.conversions_from_interactions_rate
        FROM campaign
        WHERE segments.date DURING LAST_{days}_DAYS
            AND metrics.conversions > 0
        ORDER BY metrics.conversions DESC
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    conversions = []
    for row in result.get('results', []):
        campaign = row.get('campaign', {})
        metrics = row.get('metrics', {})

        conversions.append({
            'campaign_id': campaign.get('id'),
            'campaign_name': campaign.get('name'),
            'conversions': float(metrics.get('conversions', 0)),
            'conversions_value': float(metrics.get('conversionsValue', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'cost_per_conversion': float(metrics.get('costPerConversion', 0)),
            'conversion_rate': float(metrics.get('conversionsFromInteractionsRate', 0)),
        })

    return conversions
