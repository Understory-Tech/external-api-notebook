"""
Understory CompanyModel JSON Parser Utilities

Core utilities for parsing and extracting data from Understory API CompanyModel JSON.
"""

from typing import Any, Generator, Optional
from dataclasses import dataclass
from datetime import datetime


# =============================================================================
# Column Key Parsing
# =============================================================================

def parse_column_key(column_key: str) -> dict:
    """
    Parse a column key DSL string into a structured dictionary.

    Args:
        column_key: DSL string like "pr=FY-2023|ed=12/31/2023|dr=12-months"

    Returns:
        Dictionary with parsed fields:
        - period: Full period string (e.g., "FY-2023")
        - period_type: Period type (e.g., "FY", "Q1", "Q2")
        - year: Fiscal year as integer
        - end_date: End date string (M/D/YYYY)
        - start_date: Start date string (M/D/YYYY)
        - duration_months: Duration in months
        - is_ytd: Whether this is a year-to-date period
        - raw: Original column key string
    """
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
                    num = int(value.split('-')[0])
                    result['duration_months'] = num
                except ValueError:
                    pass

        elif key == 'xtd' and value == 'ytd':
            result['is_ytd'] = True

    return result


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse a date string in M/D/YYYY format.

    Args:
        date_str: Date string like "12/31/2023"

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None
    try:
        parts = date_str.split('/')
        return datetime(int(parts[2]), int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def column_key_to_sort_key(column_key: str) -> tuple:
    """
    Convert a column key to a sortable tuple for chronological ordering.

    Returns:
        Tuple of (end_date, duration_months, period) for sorting
    """
    parsed = parse_column_key(column_key)
    end_date = parse_date_string(parsed['end_date']) or datetime.min
    duration = parsed['duration_months'] or 0
    period = parsed['period'] or ''
    return (end_date, duration, period)


# =============================================================================
# Bounding Box Utilities
# =============================================================================

@dataclass
class BoundingBox:
    """Represents a bounding box with ratio coordinates."""
    top: float
    left: float
    width: float
    height: float

    @classmethod
    def from_dict(cls, data: dict) -> 'BoundingBox':
        """Create from a dictionary."""
        return cls(
            top=data.get('top', 0),
            left=data.get('left', 0),
            width=data.get('width', 0),
            height=data.get('height', 0)
        )

    def to_pixels(self, page_width: int, page_height: int) -> dict:
        """
        Convert ratio coordinates to pixel coordinates.

        Args:
            page_width: Page width in pixels
            page_height: Page height in pixels

        Returns:
            Dictionary with x, y, width, height, x2, y2 in pixels
        """
        return {
            'x': int(self.left * page_width),
            'y': int(self.top * page_height),
            'width': int(self.width * page_width),
            'height': int(self.height * page_height),
            'x2': int((self.left + self.width) * page_width),
            'y2': int((self.top + self.height) * page_height)
        }

    def to_css_percent(self) -> dict:
        """
        Convert to CSS percentage values for overlay positioning.

        Returns:
            Dictionary with left, top, width, height as percentage strings
        """
        return {
            'left': f'{self.left * 100:.4f}%',
            'top': f'{self.top * 100:.4f}%',
            'width': f'{self.width * 100:.4f}%',
            'height': f'{self.height * 100:.4f}%'
        }


# =============================================================================
# Model Traversal
# =============================================================================

@dataclass
class CellContext:
    """Context information for a cell during traversal."""
    table_group_category: str
    table_name: str
    table_id: str
    section_name: str
    row_label: str
    row_defined_name: str
    cell: dict


def traverse_model(model: dict) -> Generator[CellContext, None, None]:
    """
    Traverse all cells in a CompanyModel, yielding each with context.

    Args:
        model: The CompanyModel dictionary

    Yields:
        CellContext objects for each cell
    """
    for table_group in model.get('tableGroups', []):
        category = table_group.get('category', '')

        for table in table_group.get('tables', []):
            table_name = table.get('name', '')
            table_id = table.get('id', '')

            for section in table.get('sections', []):
                section_name = section.get('name', '')

                for item in section.get('data', []):
                    if item.get('type') != 'row':
                        continue

                    label_obj = item.get('label', {})
                    row_label = label_obj.get('text', '')
                    row_defined_name = label_obj.get('definedName', '')

                    for cell in item.get('cells', []):
                        yield CellContext(
                            table_group_category=category,
                            table_name=table_name,
                            table_id=table_id,
                            section_name=section_name,
                            row_label=row_label,
                            row_defined_name=row_defined_name,
                            cell=cell
                        )


def traverse_summary(model: dict) -> Generator[CellContext, None, None]:
    """
    Traverse all cells in the summary sheet.

    Args:
        model: The CompanyModel dictionary

    Yields:
        CellContext objects for each summary cell
    """
    if 'summary' not in model or not model['summary']:
        return

    table = model['summary'].get('table', {})

    for section in table.get('sections', []):
        section_name = section.get('name', '')

        for item in section.get('data', []):
            if item.get('type') != 'row':
                continue

            label_obj = item.get('label', {})
            row_label = label_obj.get('text', '')
            row_defined_name = label_obj.get('definedName', '')

            for cell in item.get('cells', []):
                yield CellContext(
                    table_group_category='Summary',
                    table_name='Summary Sheet',
                    table_id=table.get('id', ''),
                    section_name=section_name,
                    row_label=row_label,
                    row_defined_name=row_defined_name,
                    cell=cell
                )


# =============================================================================
# Value Extraction
# =============================================================================

def extract_value(cell: dict) -> tuple[Any, str]:
    """
    Extract the numeric value and type from a cell.

    Args:
        cell: Cell dictionary

    Returns:
        Tuple of (value, type_str) where value may be a number, string, or None
    """
    if not cell or 'value' not in cell:
        return None, 'none'

    val = cell['value']
    val_type = val.get('type')

    if val_type == 'formula':
        # Use pre-computed value if available
        if 'value' in val:
            return val['value'], val.get('unit', 'number')
        return None, 'formula'

    elif val_type in ('dollar', 'number', 'percent', 'multiple'):
        return val.get('value'), val_type

    elif val_type == 'string':
        return val.get('value'), 'string'

    return None, val_type or 'unknown'


# =============================================================================
# Column Matching
# =============================================================================

def find_column_for_cell(cell: dict, column_groups: list) -> Optional[dict]:
    """
    Find the matching column definition for a cell.

    Args:
        cell: Cell dictionary
        column_groups: List of column group dictionaries

    Returns:
        Column definition dict or None
    """
    cell_key = cell.get('columnKey')
    if not cell_key:
        return None

    for group in column_groups:
        for column in group.get('columns', []):
            if column.get('key') == cell_key:
                return column

    return None


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python company-model-parser-utils.py <model.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        model = json.load(f)

    print(f"Company: {model.get('companyName')}")
    print(f"Model ID: {model.get('companyModelId')}")
    print(f"Table Groups: {len(model.get('tableGroups', []))}")
    print()

    # Count cells by type
    type_counts: dict[str, int] = {}
    for ctx in traverse_model(model):
        _, val_type = extract_value(ctx.cell)
        type_counts[val_type] = type_counts.get(val_type, 0) + 1

    print("Cell value types:")
    for val_type, count in sorted(type_counts.items()):
        print(f"  {val_type}: {count}")
