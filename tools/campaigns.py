"""
Campaign Tools

Pure functions for Google Ads campaign operations.
"""

from typing import Dict, List, Any, Optional

from .client import GoogleAdsClient, format_customer_id


async def list_campaigns(
    client: GoogleAdsClient,
    customer_id: str,
    status_filter: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    List campaigns for a customer.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        status_filter: Optional filter (ENABLED, PAUSED, REMOVED)
        limit: Maximum number of results

    Returns:
        List of campaign data
    """
    where_clause = ""
    if status_filter:
        where_clause = f"WHERE campaign.status = '{status_filter}'"

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign.start_date,
            campaign.end_date
        FROM campaign
        {where_clause}
        ORDER BY campaign.name
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    campaigns = []
    for row in result.get('results', []):
        campaign = row.get('campaign', {})
        campaigns.append({
            'id': campaign.get('id'),
            'name': campaign.get('name'),
            'status': campaign.get('status'),
            'channel_type': campaign.get('advertisingChannelType'),
            'bidding_strategy': campaign.get('biddingStrategyType'),
            'start_date': campaign.get('startDate'),
            'end_date': campaign.get('endDate'),
        })

    return campaigns


async def get_campaign(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
) -> Dict[str, Any]:
    """
    Get details for a specific campaign.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        campaign_id: The campaign ID

    Returns:
        Campaign details
    """
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign.start_date,
            campaign.end_date,
            campaign.campaign_budget
        FROM campaign
        WHERE campaign.id = {campaign_id}
    """

    result = client.search(customer_id, query)

    if not result.get('results'):
        raise Exception(f"Campaign not found: {campaign_id}")

    campaign = result['results'][0].get('campaign', {})
    return {
        'id': campaign.get('id'),
        'name': campaign.get('name'),
        'status': campaign.get('status'),
        'channel_type': campaign.get('advertisingChannelType'),
        'bidding_strategy': campaign.get('biddingStrategyType'),
        'start_date': campaign.get('startDate'),
        'end_date': campaign.get('endDate'),
        'budget': campaign.get('campaignBudget'),
    }


async def get_campaign_performance(
    client: GoogleAdsClient,
    customer_id: str,
    days: int = 30,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Get campaign performance metrics.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of campaign performance data
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
        WHERE segments.date DURING LAST_{days}DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
    """

    result = client.search(customer_id, query)

    campaigns = []
    for row in result.get('results', []):
        campaign = row.get('campaign', {})
        metrics = row.get('metrics', {})
        campaigns.append({
            'id': campaign.get('id'),
            'name': campaign.get('name'),
            'status': campaign.get('status'),
            'impressions': int(metrics.get('impressions', 0)),
            'clicks': int(metrics.get('clicks', 0)),
            'cost_micros': int(metrics.get('costMicros', 0)),
            'conversions': float(metrics.get('conversions', 0)),
            'average_cpc': int(metrics.get('averageCpc', 0)),
        })

    return campaigns


async def create_campaign(
    client: GoogleAdsClient,
    customer_id: str,
    name: str,
    budget_amount_micros: int,
    advertising_channel_type: str = "SEARCH",
    status: str = "PAUSED",
) -> Dict[str, Any]:
    """
    Create a new campaign.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        name: Campaign name
        budget_amount_micros: Daily budget in micros
        advertising_channel_type: Channel type (SEARCH, DISPLAY, etc.)
        status: Initial status (ENABLED, PAUSED)

    Returns:
        Created campaign details
    """
    formatted_id = format_customer_id(customer_id)

    # First create a budget
    budget_operation = {
        "campaignBudgetOperation": {
            "create": {
                "name": f"{name} Budget",
                "amountMicros": str(budget_amount_micros),
                "deliveryMethod": "STANDARD"
            }
        }
    }

    budget_result = client.mutate(customer_id, [budget_operation])
    budget_resource = budget_result['mutateOperationResponses'][0]['campaignBudgetResult']['resourceName']

    # Then create the campaign
    campaign_operation = {
        "campaignOperation": {
            "create": {
                "name": name,
                "status": status,
                "advertisingChannelType": advertising_channel_type,
                "campaignBudget": budget_resource,
                "manualCpc": {}
            }
        }
    }

    campaign_result = client.mutate(customer_id, [campaign_operation])
    campaign_resource = campaign_result['mutateOperationResponses'][0]['campaignResult']['resourceName']
    campaign_id = campaign_resource.split('/')[-1]

    return {
        'id': campaign_id,
        'name': name,
        'status': status,
        'budget_resource': budget_resource,
        'resource_name': campaign_resource,
    }


async def update_campaign_status(
    client: GoogleAdsClient,
    customer_id: str,
    campaign_id: str,
    status: str,
) -> Dict[str, Any]:
    """
    Update a campaign's status.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        campaign_id: The campaign ID
        status: New status (ENABLED, PAUSED, REMOVED)

    Returns:
        Updated campaign info
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/campaigns/{campaign_id}"

    operation = {
        "campaignOperation": {
            "update": {
                "resourceName": resource_name,
                "status": status
            },
            "updateMask": "status"
        }
    }

    result = client.mutate(customer_id, [operation])

    return {
        'id': campaign_id,
        'status': status,
        'updated': True,
    }
