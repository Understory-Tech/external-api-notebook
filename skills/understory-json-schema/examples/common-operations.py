"""
Common Operations for Understory CompanyModel

Practical examples for common data extraction patterns from CompanyModel JSON.
"""

from typing import Any, Optional
from datetime import datetime


# =============================================================================
# Internal Helpers (duplicated from company-model-parser-utils.py for standalone usage)
# =============================================================================

def _parse_column_key(column_key: str) -> dict:
    """Parse a column key DSL string (internal helper)."""
    result = {
        'period': None,
        'period_type': None,
        'year': None,
        'end_date': None,
        'start_date': None,
        'duration_months': None,
        'is_ytd': False,
        'raw': column_key
    }

    if not column_key:
        return result

    for segment in column_key.split('|'):
        if '=' not in segment:
            continue
        key, value = segment.split('=', 1)
        if key == 'pr' and value != 'null':
            result['period'] = value
            if '-' in value:
                parts = value.split('-')
                result['period_type'] = parts[0]
                try:
                    result['year'] = int(parts[1])
                except (ValueError, IndexError):
                    pass
        elif key == 'ed' and value != 'null':
            result['end_date'] = value
        elif key == 'sd' and value != 'null':
            result['start_date'] = value
        elif key == 'dr':
            if '-' in value:
                try:
                    result['duration_months'] = int(value.split('-')[0])
                except ValueError:
                    pass
        elif key == 'xtd' and value == 'ytd':
            result['is_ytd'] = True

    return result


def _parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse a date string in M/D/YYYY format (internal helper)."""
    if not date_str:
        return None
    try:
        parts = date_str.split('/')
        return datetime(int(parts[2]), int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def _extract_value(cell: dict) -> tuple[Any, str]:
    """Extract value from cell (internal helper)."""
    if not cell or 'value' not in cell:
        return None, 'none'

    val = cell['value']
    val_type = val.get('type')

    if val_type == 'formula':
        if 'value' in val:
            return val['value'], val.get('unit', 'number')
        return None, 'formula'
    elif val_type in ('dollar', 'number', 'percent', 'multiple'):
        return val.get('value'), val_type
    elif val_type == 'string':
        return val.get('value'), 'string'

    return None, val_type or 'unknown'


def get_income_statement_data(model: dict) -> list[dict]:
    """
    Extract all income statement rows with their cells.

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of row dictionaries with label and cells
    """
    rows = []

    for table_group in model.get('tableGroups', []):
        if table_group.get('category') != 'Income Statement':
            continue

        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') == 'row':
                        rows.append({
                            'table_name': table.get('name'),
                            'label': item.get('label', {}).get('text', ''),
                            'defined_name': item.get('label', {}).get('definedName', ''),
                            'cells': item.get('cells', [])
                        })

    return rows


def get_balance_sheet_data(model: dict) -> list[dict]:
    """
    Extract all balance sheet rows with their cells.

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of row dictionaries with label and cells
    """
    rows = []

    for table_group in model.get('tableGroups', []):
        if table_group.get('category') != 'Balance Sheet':
            continue

        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') == 'row':
                        rows.append({
                            'table_name': table.get('name'),
                            'label': item.get('label', {}).get('text', ''),
                            'defined_name': item.get('label', {}).get('definedName', ''),
                            'cells': item.get('cells', [])
                        })

    return rows


def get_cells_by_period(
    model: dict,
    period_type: str = 'FY',
    year: Optional[int] = None
) -> list[dict]:
    """
    Filter cells by fiscal period type and optionally year.

    Args:
        model: The CompanyModel dictionary
        period_type: Period type to filter ('FY', 'Q1', 'Q2', 'Q3', 'Q4')
        year: Optional year to filter

    Returns:
        List of cell dictionaries with context
    """
    results = []

    for table_group in model.get('tableGroups', []):
        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') != 'row':
                        continue

                    row_label = item.get('label', {}).get('text', '')

                    for cell in item.get('cells', []):
                        col_key = cell.get('columnKey', '')
                        parsed = _parse_column_key(col_key)

                        if parsed['period_type'] != period_type:
                            continue

                        if year is not None and parsed['year'] != year:
                            continue

                        value, val_type = _extract_value(cell)

                        results.append({
                            'category': table_group.get('category'),
                            'table': table.get('name'),
                            'row_label': row_label,
                            'period': parsed['period'],
                            'end_date': parsed['end_date'],
                            'value': value,
                            'value_type': val_type,
                            'cell': cell
                        })

    return results


def build_time_series(row: dict) -> list[dict]:
    """
    Build a chronologically ordered time series from a row's cells.

    Args:
        row: Row dictionary with cells

    Returns:
        List of dictionaries with date, period, and value, sorted by date
    """
    series = []

    for cell in row.get('cells', []):
        col_key = cell.get('columnKey', '')
        parsed = _parse_column_key(col_key)
        value, val_type = _extract_value(cell)

        if value is None:
            continue

        end_date = _parse_date_string(parsed['end_date'])

        series.append({
            'end_date': end_date,
            'end_date_str': parsed['end_date'],
            'period': parsed['period'],
            'duration_months': parsed['duration_months'],
            'value': value,
            'value_type': val_type,
            'is_forecast': cell.get('isForecast', False)
        })

    # Sort by end date
    series.sort(key=lambda x: x['end_date'] or datetime.min)

    return series


def get_source_locations(model: dict) -> list[dict]:
    """
    Get all PDF source locations from the model.

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of source location dictionaries
    """
    locations = []

    for table_group in model.get('tableGroups', []):
        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') != 'row':
                        continue

                    row_label = item.get('label', {}).get('text', '')

                    for cell in item.get('cells', []):
                        source_meta = cell.get('sourceMeta')
                        if not source_meta:
                            continue

                        locations.append({
                            'category': table_group.get('category'),
                            'table': table.get('name'),
                            'row_label': row_label,
                            'column_key': cell.get('columnKey'),
                            'file_id': source_meta.get('fileId'),
                            'page_number': source_meta.get('pageNumber'),
                            'table_id': source_meta.get('tableId'),
                            'bounding_box': source_meta.get('boundingBox'),
                            'link': cell.get('link')
                        })

    return locations


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python common-operations.py <model.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        model = json.load(f)

    print(f"Company: {model.get('companyName')}")
