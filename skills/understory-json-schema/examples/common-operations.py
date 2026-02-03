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


def group_by_category(model: dict) -> dict[str, list[dict]]:
    """
    Group all tables by their category.

    Args:
        model: The CompanyModel dictionary

    Returns:
        Dictionary mapping category names to lists of table info
    """
    grouped: dict[str, list[dict]] = {}

    for table_group in model.get('tableGroups', []):
        category = table_group.get('category', 'Other')

        if category not in grouped:
            grouped[category] = []

        for table in table_group.get('tables', []):
            row_count = sum(
                1 for section in table.get('sections', [])
                for item in section.get('data', [])
                if item.get('type') == 'row'
            )

            grouped[category].append({
                'id': table.get('id'),
                'name': table.get('name'),
                'table_type': table.get('tableType'),
                'description': table.get('description'),
                'row_count': row_count,
                'section_count': len(table.get('sections', []))
            })

    return grouped


def find_row_by_label(
    model: dict,
    label_text: str,
    category: Optional[str] = None
) -> Optional[dict]:
    """
    Find a row by its label text (case-insensitive partial match).

    Args:
        model: The CompanyModel dictionary
        label_text: Text to search for
        category: Optional category to filter by

    Returns:
        Row dictionary or None if not found
    """
    label_lower = label_text.lower()

    for table_group in model.get('tableGroups', []):
        if category and table_group.get('category') != category:
            continue

        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') != 'row':
                        continue

                    row_label = item.get('label', {}).get('text', '')
                    if label_lower in row_label.lower():
                        return {
                            'category': table_group.get('category'),
                            'table_name': table.get('name'),
                            'label': row_label,
                            'defined_name': item.get('label', {}).get('definedName'),
                            'cells': item.get('cells', []),
                            'row': item
                        }

    return None


def get_available_periods(model: dict) -> list[dict]:
    """
    Get all available time periods from column groups.

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of period dictionaries sorted by date
    """
    periods = []

    for group in model.get('columnGroups', []):
        for column in group.get('columns', []):
            period_info = column.get('period', {})
            term = period_info.get('term', {})

            end_date_str = column.get('endDate', '')
            # Parse ISO date (strip timezone for consistent sorting)
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except ValueError:
                end_date = None

            periods.append({
                'key': column.get('key'),
                'type': group.get('type'),
                'period_type': term.get('type'),
                'year': period_info.get('year', {}).get('year'),
                'end_date': end_date,
                'end_date_str': end_date_str,
                'duration_months': column.get('duration', {}).get('numberOfMonths'),
                'is_stub': column.get('stub', False)
            })

    # Sort by end date
    periods.sort(key=lambda x: x['end_date'] or datetime.min)

    return periods


def calculate_yoy_growth(
    model: dict,
    row_defined_name: str,
    base_year: int
) -> Optional[float]:
    """
    Calculate year-over-year growth for a specific row.

    Args:
        model: The CompanyModel dictionary
        row_defined_name: The definedName of the row
        base_year: The year to calculate growth for

    Returns:
        Growth rate as decimal (0.15 = 15%) or None
    """
    current_value = None
    prior_value = None

    for table_group in model.get('tableGroups', []):
        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') != 'row':
                        continue

                    if item.get('label', {}).get('definedName') != row_defined_name:
                        continue

                    for cell in item.get('cells', []):
                        parsed = _parse_column_key(cell.get('columnKey', ''))

                        if parsed['period_type'] != 'FY':
                            continue

                        value, _ = _extract_value(cell)
                        if value is None:
                            continue

                        if parsed['year'] == base_year:
                            current_value = value
                        elif parsed['year'] == base_year - 1:
                            prior_value = value

    if current_value is not None and prior_value is not None and prior_value != 0:
        return (current_value - prior_value) / abs(prior_value)

    return None


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
    print()

    # Show categories
    categories = group_by_category(model)
    print("Categories:")
    for cat, tables in categories.items():
        print(f"  {cat}: {len(tables)} tables")

    print()

    # Show available periods
    periods = get_available_periods(model)
    fy_periods = [p for p in periods if p['period_type'] == 'FY']
    print(f"Fiscal years available: {len(fy_periods)}")
    for p in fy_periods[-5:]:
        print(f"  {p['year']}: {p['end_date_str'][:10]}")
