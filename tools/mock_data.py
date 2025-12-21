"""
Mock Data for Google Ads

Provides realistic mock data for development and testing
without requiring actual Google Ads API credentials.

TODO: Update mock data with real API response structure when credentials available
"""

from typing import Dict, List, Any

MOCK_ACCOUNTS = [
    '1234567890',
    '0987654321',
]

MOCK_ACCOUNT_INFO = {
    'id': '1234567890',
    'name': 'Demo Google Ads Account',
    'currency': 'USD',
    'timezone': 'America/Los_Angeles',
    'auto_tagging': True,
    'is_manager': False,
}

MOCK_CAMPAIGNS = [
    {
        'campaign': {
            'id': '12345678901',
            'name': 'Search - Brand Terms',
            'status': 'ENABLED',
            'advertisingChannelType': 'SEARCH',
            'biddingStrategyType': 'TARGET_CPA',
        },
        'metrics': {
            'impressions': '125000',
            'clicks': '8500',
            'costMicros': '4250000000',  # $4,250.00
            'conversions': '425',
        },
    },
    {
        'campaign': {
            'id': '12345678902',
            'name': 'Display - Remarketing',
            'status': 'ENABLED',
            'advertisingChannelType': 'DISPLAY',
            'biddingStrategyType': 'TARGET_ROAS',
        },
        'metrics': {
            'impressions': '850000',
            'clicks': '12000',
            'costMicros': '3600000000',  # $3,600.00
            'conversions': '180',
        },
    },
    {
        'campaign': {
            'id': '12345678903',
            'name': 'Shopping - All Products',
            'status': 'PAUSED',
            'advertisingChannelType': 'SHOPPING',
            'biddingStrategyType': 'MAXIMIZE_CONVERSIONS',
        },
        'metrics': {
            'impressions': '450000',
            'clicks': '6200',
            'costMicros': '2100000000',  # $2,100.00
            'conversions': '280',
        },
    },
]

MOCK_AD_GROUPS = [
    {
        'adGroup': {
            'id': '23456789001',
            'name': 'Brand - Exact Match',
            'status': 'ENABLED',
            'type': 'SEARCH_STANDARD',
        },
        'campaign': {
            'id': '12345678901',
            'name': 'Search - Brand Terms',
        },
    },
    {
        'adGroup': {
            'id': '23456789002',
            'name': 'Brand - Phrase Match',
            'status': 'ENABLED',
            'type': 'SEARCH_STANDARD',
        },
        'campaign': {
            'id': '12345678901',
            'name': 'Search - Brand Terms',
        },
    },
]

MOCK_ADS = [
    {
        'adGroupAd': {
            'ad': {
                'id': '34567890001',
                'name': 'RSA - Main Ad',
            },
            'status': 'ENABLED',
        },
        'campaign': {
            'name': 'Search - Brand Terms',
        },
        'adGroup': {
            'name': 'Brand - Exact Match',
        },
        'metrics': {
            'impressions': '75000',
            'clicks': '5200',
            'costMicros': '2600000000',
            'conversions': '260',
        },
    },
    {
        'adGroupAd': {
            'ad': {
                'id': '34567890002',
                'name': 'RSA - Promo Ad',
                'responsiveSearchAd': {
                    'headlines': [
                        {'text': 'Save 20% Today'},
                        {'text': 'Free Shipping'},
                        {'text': 'Limited Time Offer'},
                    ],
                    'descriptions': [
                        {'text': 'Shop now and save big on your favorite products.'},
                        {'text': 'Get free shipping on orders over $50.'},
                    ],
                },
            },
            'status': 'ENABLED',
        },
        'campaign': {
            'name': 'Search - Brand Terms',
        },
        'adGroup': {
            'name': 'Brand - Phrase Match',
        },
        'metrics': {
            'impressions': '50000',
            'clicks': '3300',
            'costMicros': '1650000000',
            'conversions': '165',
        },
    },
]

MOCK_KEYWORDS = [
    {
        'adGroupCriterion': {
            'keyword': {
                'text': 'buy product online',
                'matchType': 'EXACT',
            },
        },
        'campaign': {
            'name': 'Search - Brand Terms',
        },
        'adGroup': {
            'name': 'Brand - Exact Match',
        },
        'metrics': {
            'impressions': '25000',
            'clicks': '2100',
            'costMicros': '1050000000',
            'conversions': '105',
            'ctr': '0.084',
            'averageCpc': '500000',
        },
    },
    {
        'adGroupCriterion': {
            'keyword': {
                'text': 'best deals',
                'matchType': 'PHRASE',
            },
        },
        'campaign': {
            'name': 'Search - Brand Terms',
        },
        'adGroup': {
            'name': 'Brand - Phrase Match',
        },
        'metrics': {
            'impressions': '18000',
            'clicks': '1400',
            'costMicros': '700000000',
            'conversions': '70',
            'ctr': '0.078',
            'averageCpc': '500000',
        },
    },
]

MOCK_SEARCH_TERMS = [
    {
        'searchTermView': {
            'searchTerm': 'buy product online free shipping',
            'status': 'NONE',
        },
        'campaign': {
            'name': 'Search - Brand Terms',
        },
        'adGroup': {
            'name': 'Brand - Exact Match',
        },
        'metrics': {
            'impressions': '1200',
            'clicks': '98',
            'costMicros': '49000000',
            'conversions': '12',
        },
    },
    {
        'searchTermView': {
            'searchTerm': 'best deals near me',
            'status': 'NONE',
        },
        'campaign': {
            'name': 'Search - Brand Terms',
        },
        'adGroup': {
            'name': 'Brand - Phrase Match',
        },
        'metrics': {
            'impressions': '850',
            'clicks': '65',
            'costMicros': '32500000',
            'conversions': '8',
        },
    },
]

MOCK_BUDGETS = [
    {
        'campaign': {
            'id': '12345678901',
            'name': 'Search - Brand Terms',
            'status': 'ENABLED',
        },
        'campaignBudget': {
            'amountMicros': '10000000000',  # $100.00/day
            'status': 'ENABLED',
            'deliveryMethod': 'STANDARD',
        },
    },
    {
        'campaign': {
            'id': '12345678902',
            'name': 'Display - Remarketing',
            'status': 'ENABLED',
        },
        'campaignBudget': {
            'amountMicros': '5000000000',  # $50.00/day
            'status': 'ENABLED',
            'deliveryMethod': 'STANDARD',
        },
    },
]

MOCK_CONVERSIONS = [
    {
        'campaign': {
            'id': '12345678901',
            'name': 'Search - Brand Terms',
        },
        'metrics': {
            'conversions': '425',
            'conversionsValue': '21250.00',
            'costMicros': '4250000000',
            'costPerConversion': '10000000',
            'conversionsFromInteractionsRate': '0.05',
        },
    },
    {
        'campaign': {
            'id': '12345678902',
            'name': 'Display - Remarketing',
        },
        'metrics': {
            'conversions': '180',
            'conversionsValue': '9000.00',
            'costMicros': '3600000000',
            'costPerConversion': '20000000',
            'conversionsFromInteractionsRate': '0.015',
        },
    },
]


def wrap_results(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrap data in Google Ads API response format."""
    return {'results': data}
