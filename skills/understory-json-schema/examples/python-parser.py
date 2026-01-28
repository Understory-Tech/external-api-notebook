"""
Understory CompanyModel JSON Parser Utilities

Core utilities for parsing and extracting data from Understory API CompanyModel JSON.
"""

from typing import Any, Callable, Generator, Optional
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


def format_value(value: Any, value_type: str, decimal_places: int = 0) -> str:
    """
    Format a value for display.

    Args:
        value: The numeric value
        value_type: Type string (dollar, percent, number, multiple)
        decimal_places: Number of decimal places

    Returns:
        Formatted string
    """
    if value is None:
        return ''

    try:
        if value_type == 'percent':
            return f"{value * 100:.{decimal_places}f}%"
        elif value_type == 'dollar':
            return f"${value:,.{decimal_places}f}"
        elif value_type == 'multiple':
            return f"{value:.{decimal_places}f}x"
        else:
            return f"{value:,.{decimal_places}f}"
    except (TypeError, ValueError):
        return str(value)


# =============================================================================
# Formula Evaluation
# =============================================================================

def evaluate_formula(
    formula: Optional[dict],
    cell_lookup: Callable[[str, str], Optional[float]]
) -> Optional[float]:
    """
    Recursively evaluate a formula tree.

    Args:
        formula: Formula tree dictionary
        cell_lookup: Function that takes (row_defined_name, column_key) and
                     returns the numeric value

    Returns:
        Computed value or None if evaluation fails
    """
    if formula is None:
        return None

    # Check for operator
    operator = formula.get('operator')

    if operator:
        # Binary operators
        if operator in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'):
            left = evaluate_formula(formula.get('left'), cell_lookup)
            right = evaluate_formula(formula.get('right'), cell_lookup)

            if left is None or right is None:
                return None

            if operator == 'ADD':
                return left + right
            elif operator == 'SUBTRACT':
                return left - right
            elif operator == 'MULTIPLY':
                return left * right
            elif operator == 'DIVIDE':
                return left / right if right != 0 else None

        # Unary operators
        elif operator == 'NEGATE':
            operand = evaluate_formula(formula.get('operand'), cell_lookup)
            return -operand if operand is not None else None

    # Cell reference
    if 'value' in formula:
        ref = formula['value']
        if isinstance(ref, dict):
            row_name = ref.get('rowDefinedName')
            col_key = ref.get('colKey')
            if row_name and col_key:
                return cell_lookup(row_name, col_key)
        elif isinstance(ref, (int, float)):
            return float(ref)

    return None


def build_cell_lookup(model: dict) -> Callable[[str, str], Optional[float]]:
    """
    Build a cell lookup function from a model.

    Args:
        model: The CompanyModel dictionary

    Returns:
        Function that takes (row_defined_name, column_key) and returns value
    """
    # Build index of all cells
    cell_index: dict[tuple[str, str], float] = {}

    for ctx in traverse_model(model):
        cell = ctx.cell
        col_key = cell.get('columnKey')
        if not col_key:
            continue

        value, _ = extract_value(cell)
        if value is not None and isinstance(value, (int, float)):
            cell_index[(ctx.row_defined_name, col_key)] = float(value)

    def lookup(row_defined_name: str, column_key: str) -> Optional[float]:
        return cell_index.get((row_defined_name, column_key))

    return lookup


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


def get_column_end_date(column: dict) -> Optional[datetime]:
    """
    Extract the end date from a column definition.

    Args:
        column: Column definition dictionary

    Returns:
        datetime object or None
    """
    end_date_str = column.get('endDate')
    if not end_date_str:
        return None

    try:
        # Handle ISO format: 2023-12-31T00:00:00.000Z
        return datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    except ValueError:
        return None


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python python-parser.py <model.json>")
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
