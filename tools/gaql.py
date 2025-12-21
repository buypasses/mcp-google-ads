"""
GAQL Query Tools

Pure functions for executing Google Ads Query Language queries.
"""

from typing import Dict, List, Any
import json

from .client import GoogleAdsClient, format_customer_id


async def execute_gaql_query(
    client: GoogleAdsClient,
    customer_id: str,
    query: str,
) -> List[Dict[str, Any]]:
    """
    Execute a custom GAQL query and return raw results.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        query: Valid GAQL query string

    Returns:
        List of result rows as dictionaries
    """
    result = client.search(customer_id, query)
    return result.get('results', [])


async def run_gaql(
    client: GoogleAdsClient,
    customer_id: str,
    query: str,
    output_format: str = "dict",
) -> Any:
    """
    Execute a GAQL query with flexible output formatting.

    Args:
        client: Google Ads client instance
        customer_id: The customer ID
        query: Valid GAQL query string
        output_format: Output format ('dict', 'json', 'csv', 'table')

    Returns:
        Query results in the requested format
    """
    result = client.search(customer_id, query)
    results = result.get('results', [])

    if not results:
        if output_format == 'json':
            return '[]'
        elif output_format == 'csv':
            return ''
        elif output_format == 'table':
            return 'No results found.'
        return []

    if output_format == 'json':
        return json.dumps(results, indent=2)

    elif output_format == 'csv':
        # Extract fields from first result
        fields = _extract_fields(results[0])
        csv_lines = [','.join(fields)]

        for row in results:
            row_data = []
            for field in fields:
                value = _get_nested_value(row, field)
                value = str(value).replace(',', ';')
                row_data.append(value)
            csv_lines.append(','.join(row_data))

        return '\n'.join(csv_lines)

    elif output_format == 'table':
        fields = _extract_fields(results[0])
        field_widths = {f: len(f) for f in fields}

        # Calculate max widths
        for row in results:
            for field in fields:
                value = str(_get_nested_value(row, field))
                field_widths[field] = max(field_widths[field], len(value))

        # Build table
        formatted_id = format_customer_id(customer_id)
        lines = [f"Query Results for Account {formatted_id}:"]
        lines.append("-" * 100)

        header = " | ".join(f"{f:{field_widths[f]}}" for f in fields)
        lines.append(header)
        lines.append("-" * len(header))

        for row in results:
            row_values = []
            for field in fields:
                value = str(_get_nested_value(row, field))
                row_values.append(f"{value:{field_widths[field]}}")
            lines.append(" | ".join(row_values))

        return '\n'.join(lines)

    # Default: return as dict
    return results


def _extract_fields(row: Dict) -> List[str]:
    """Extract field paths from a result row."""
    fields = []

    def _extract(obj, prefix=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    _extract(value, new_prefix)
                elif isinstance(value, list):
                    # For lists, just note the field exists
                    fields.append(new_prefix)
                else:
                    fields.append(new_prefix)
        return fields

    return _extract(row)


def _get_nested_value(obj: Dict, path: str) -> Any:
    """Get a nested value from a dict using dot notation."""
    keys = path.split('.')
    value = obj

    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, '')
        else:
            return ''

    return value if value is not None else ''
