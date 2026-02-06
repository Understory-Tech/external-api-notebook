"""
Summary Sheet Utilities for Understory CompanyModel

Utilities for extracting and working with summary sheet data from CompanyModel JSON.
"""

from typing import Any, Optional
from datetime import datetime


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


def get_summary_sheet(model: dict) -> Optional[dict]:
    """
    Extract the summary sheet from a model if available.

    Args:
        model: The CompanyModel dictionary

    Returns:
        Summary dictionary or None if not available
    """
    return model.get('summary')


def has_summary_sheet(model: dict) -> bool:
    """
    Check if a model has a summary sheet.

    Args:
        model: The CompanyModel dictionary

    Returns:
        True if summary sheet is available
    """
    summary = model.get('summary')
    return summary is not None and 'table' in summary


def get_summary_rows(model: dict) -> list[dict]:
    """
    Extract all rows from the summary table.

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of row dictionaries
    """
    summary = model.get('summary')
    if not summary:
        return []

    rows = []
    table = summary.get('table', {})

    for section in table.get('sections', []):
        for item in section.get('data', []):
            if item.get('type') == 'row':
                rows.append(item)

    return rows


def get_custom_columns(model: dict) -> list[dict]:
    """
    Get the custom column definitions (MRQ, LTM, etc.).

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of custom column definitions
    """
    summary = model.get('summary')
    if not summary:
        return []

    return summary.get('customColumns', [])


def get_custom_column_mapping(model: dict) -> dict[str, dict]:
    """
    Get a mapping of custom column keys to their definitions.

    Args:
        model: The CompanyModel dictionary

    Returns:
        Dictionary mapping key (e.g., 'mrq') to column definition
    """
    return {
        col['key']: col
        for col in get_custom_columns(model)
    }


def find_summary_row_by_label(
    model: dict,
    label_text: str,
    exact: bool = False
) -> Optional[dict]:
    """
    Find a summary row by its label text.

    Args:
        model: The CompanyModel dictionary
        label_text: Text to search for
        exact: If True, require exact match; if False, partial match (case-insensitive)

    Returns:
        Row dictionary or None if not found
    """
    label_lower = label_text.lower()

    for row in get_summary_rows(model):
        row_text = row.get('label', {}).get('text', '')

        if exact:
            if row_text == label_text:
                return row
        else:
            if label_lower in row_text.lower():
                return row

    return None


def get_custom_column_value(row: dict, column_key: str) -> Optional[dict]:
    """
    Get the cell for a custom column (mrq, ltm, etc.) from a row.

    Args:
        row: Summary row dictionary
        column_key: Custom column key ('mrq', 'mrqMinusOne', 'ltm', 'ltmMinusOne')

    Returns:
        Cell dictionary or None if not found
    """
    for cell in row.get('cells', []):
        if cell.get('columnKey') == column_key:
            return cell
    return None


def extract_summary_value(cell: dict) -> tuple[Any, str]:
    """
    Extract the numeric value from a summary cell.

    Summary cells often have formula values with pre-computed results.

    Args:
        cell: Cell dictionary

    Returns:
        Tuple of (value, unit/type) or (None, 'none')
    """
    if not cell or 'value' not in cell:
        return None, 'none'

    val = cell['value']
    val_type = val.get('type')

    if val_type == 'formula':
        # Check for pre-computed value
        if 'value' in val:
            return val['value'], val.get('unit', 'number')
        # Formula without pre-computed value
        return None, 'formula'

    elif val_type in ('dollar', 'number', 'percent', 'multiple'):
        return val.get('value'), val_type

    elif val_type == 'string':
        return val.get('value'), 'string'

    return None, val_type or 'unknown'


def get_metric_values(
    model: dict,
    metric_label: str
) -> dict[str, Any]:
    """
    Get all values for a metric across all columns.

    Args:
        model: The CompanyModel dictionary
        metric_label: Label text to search for

    Returns:
        Dictionary mapping column keys to values
    """
    row = find_summary_row_by_label(model, metric_label)
    if not row:
        return {}

    values = {}
    for cell in row.get('cells', []):
        col_key = cell.get('columnKey', '')
        value, _ = extract_summary_value(cell)
        if value is not None:
            values[col_key] = value

    return values


def get_mrq_ltm_values(
    model: dict,
    metric_label: str
) -> dict[str, Any]:
    """
    Get MRQ and LTM values for a specific metric.

    Args:
        model: The CompanyModel dictionary
        metric_label: Label text to search for

    Returns:
        Dictionary with 'mrq', 'mrq_minus_one', 'ltm', 'ltm_minus_one' keys
    """
    row = find_summary_row_by_label(model, metric_label)
    if not row:
        return {}

    result = {}
    key_mapping = {
        'mrq': 'mrq',
        'mrqMinusOne': 'mrq_minus_one',
        'ltm': 'ltm',
        'ltmMinusOne': 'ltm_minus_one'
    }

    for cell_key, result_key in key_mapping.items():
        cell = get_custom_column_value(row, cell_key)
        if cell:
            value, _ = extract_summary_value(cell)
            result[result_key] = value

    return result


def build_summary_time_series(
    model: dict,
    metric_label: str
) -> list[dict]:
    """
    Build a time series for a summary metric.

    Args:
        model: The CompanyModel dictionary
        metric_label: Label text to search for

    Returns:
        List of dictionaries with period info and values, sorted chronologically
    """

    row = find_summary_row_by_label(model, metric_label)
    if not row:
        return []

    custom_mapping = get_custom_column_mapping(model)
    series = []

    for cell in row.get('cells', []):
        col_key = cell.get('columnKey', '')
        is_custom = cell.get('isCustom', False)

        # For custom columns, use the syntheticColumnKey
        actual_key = col_key
        custom_label = None
        if is_custom and col_key in custom_mapping:
            custom_def = custom_mapping[col_key]
            actual_key = custom_def.get('syntheticColumnKey', col_key)
            custom_label = custom_def.get('label')

        parsed = _parse_column_key(actual_key)
        value, val_type = extract_summary_value(cell)

        if value is None:
            continue

        end_date = _parse_date_string(parsed['end_date'])

        series.append({
            'column_key': col_key,
            'end_date': end_date,
            'end_date_str': parsed['end_date'],
            'period': parsed['period'],
            'duration_months': parsed['duration_months'],
            'value': value,
            'value_type': val_type,
            'is_custom': is_custom,
            'custom_label': custom_label
        })

    # Sort by end date, putting custom columns at the end
    series.sort(key=lambda x: (
        x['is_custom'],  # Non-custom first
        x['end_date'] or datetime.min
    ))

    return series


def get_all_summary_metrics(model: dict) -> list[dict]:
    """
    Get all summary metrics with their MRQ and LTM values.

    Args:
        model: The CompanyModel dictionary

    Returns:
        List of metric dictionaries with label and values
    """
    metrics = []

    for row in get_summary_rows(model):
        label = row.get('label', {}).get('text', '')
        defined_name = row.get('label', {}).get('definedName', '')
        style = row.get('label', {}).get('style', '')

        values = {}
        for cell in row.get('cells', []):
            col_key = cell.get('columnKey', '')
            value, val_type = extract_summary_value(cell)
            values[col_key] = {
                'value': value,
                'type': val_type,
                'is_custom': cell.get('isCustom', False)
            }

        metrics.append({
            'label': label,
            'defined_name': defined_name,
            'style': style,
            'values': values
        })

    return metrics


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python summary-sheet.py <model.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        model = json.load(f)

    print(f"Company: {model.get('companyName')}")
    print()

    if not has_summary_sheet(model):
        print("No summary sheet available in this model.")
        sys.exit(0)

    # Show custom columns
    custom_cols = get_custom_columns(model)
    print("Custom columns:")
    for col in custom_cols:
        print(f"  {col['label']}: {col['syntheticColumnKey']}")
    print()

    # Show summary rows
    rows = get_summary_rows(model)
    print(f"Summary rows: {len(rows)}")
    print()

    # Show sample metrics
    print("Sample metrics (first 5):")
    for row in rows[:5]:
        label = row.get('label', {}).get('text', '')
        mrq_ltm = get_mrq_ltm_values(model, label)
        print(f"  {label}:")
        if 'mrq' in mrq_ltm:
            print(f"    MRQ: {mrq_ltm['mrq']:,.0f}" if mrq_ltm['mrq'] else "    MRQ: N/A")
        if 'ltm' in mrq_ltm:
            print(f"    LTM: {mrq_ltm['ltm']:,.0f}" if mrq_ltm['ltm'] else "    LTM: N/A")
