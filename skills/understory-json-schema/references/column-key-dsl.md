# Column Key DSL Format

Column keys use a domain-specific language (DSL) to uniquely identify time periods. This document explains the format and how to parse it.

## Format Overview

Column keys are pipe-delimited strings with key-value pairs:

```
pr=FY-2023|ed=12/31/2023|dr=12-months
```

Each segment follows the pattern `key=value`, separated by `|`.

## Field Definitions

| Field | Name | Description | Examples |
|-------|------|-------------|----------|
| `pr` | Period | Fiscal period identifier | `FY-2023`, `Q1-2024`, `Q3-2025` |
| `ed` | End Date | Period end date (M/D/YYYY) | `12/31/2023`, `9/30/2025` |
| `sd` | Start Date | Period start date (M/D/YYYY) | `1/1/2023`, `7/1/2024` |
| `dr` | Duration | Period duration | `12-months`, `3-months`, `1-months` |
| `xtd` | Year-to-Date | YTD indicator | `ytd` |

## Common Patterns

### Fiscal Year
```
pr=FY-2023|ed=12/31/2023|dr=12-months
```
Full fiscal year ending December 31, 2023.

### Quarterly
```
pr=Q1-2024|ed=4/1/2024|dr=3-months
```
First quarter of fiscal 2024.

### Year-to-Date
```
pr=Q3-2024|ed=9/30/2024|dr=9-months|xtd=ytd
```
Nine months ending September 30, 2024.

### Date Range
```
pr=Q3-2023|sd=1/1/2023|ed=10/1/2023|dr=9-months
```
Custom range with explicit start and end dates.

### Point-in-Time (No Duration)
```
pr=null|ed=3/16/2020
```
Snapshot date without a duration period.

### Duration Only (No Period Label)
```
pr=null|ed=12/31/2017|dr=12-months
```
12-month duration ending on a specific date, no fiscal period label.

## Period Types

The `pr` field contains a period type and year:

| Pattern | Type | Duration |
|---------|------|----------|
| `FY-YYYY` | Fiscal Year | 12 months |
| `Q1-YYYY` | Quarter 1 | 3 months |
| `Q2-YYYY` | Quarter 2 | 3 months |
| `Q3-YYYY` | Quarter 3 | 3 months |
| `Q4-YYYY` | Quarter 4 | 3 months |
| `null` | No period | Varies |

## Parsing Algorithm

### Python Implementation

```python
def parse_column_key(column_key: str) -> dict:
    """
    Parse a column key DSL string into a structured dictionary.

    Args:
        column_key: DSL string like "pr=FY-2023|ed=12/31/2023|dr=12-months"

    Returns:
        Dictionary with parsed fields
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

    # Split by pipe and parse each segment
    for segment in column_key.split('|'):
        if '=' not in segment:
            continue

        key, value = segment.split('=', 1)

        if key == 'pr' and value != 'null':
            result['period'] = value
            # Parse period type and year
            if '-' in value:
                parts = value.split('-')
                result['period_type'] = parts[0]  # FY, Q1, Q2, etc.
                result['year'] = int(parts[1])

        elif key == 'ed' and value != 'null':
            result['end_date'] = value

        elif key == 'sd' and value != 'null':
            result['start_date'] = value

        elif key == 'dr':
            # Parse duration like "12-months" or "3-months"
            if '-' in value:
                num = int(value.split('-')[0])
                result['duration_months'] = num

        elif key == 'xtd' and value == 'ytd':
            result['is_ytd'] = True

    return result


def parse_date(date_str: str) -> tuple:
    """
    Parse a date string in M/D/YYYY format.

    Returns:
        Tuple of (month, day, year)
    """
    parts = date_str.split('/')
    return (int(parts[0]), int(parts[1]), int(parts[2]))
```

### Usage Examples

```python
# Fiscal year
key = "pr=FY-2023|ed=12/31/2023|dr=12-months"
parsed = parse_column_key(key)
# {
#   'period': 'FY-2023',
#   'period_type': 'FY',
#   'year': 2023,
#   'end_date': '12/31/2023',
#   'duration_months': 12,
#   ...
# }

# Quarter
key = "pr=Q3-2024|ed=9/30/2024|dr=3-months"
parsed = parse_column_key(key)
# {
#   'period': 'Q3-2024',
#   'period_type': 'Q3',
#   'year': 2024,
#   'end_date': '9/30/2024',
#   'duration_months': 3,
#   ...
# }

# Year-to-date
key = "pr=Q3-2024|ed=9/30/2024|dr=9-months|xtd=ytd"
parsed = parse_column_key(key)
# {
#   'period': 'Q3-2024',
#   'is_ytd': True,
#   'duration_months': 9,
#   ...
# }
```

## Matching Cells to Columns

To find the column definition for a cell:

```python
def find_column_for_cell(cell, column_groups):
    """Find the matching column definition for a cell."""
    cell_key = cell.get('columnKey')
    if not cell_key:
        return None

    for group in column_groups:
        for column in group.get('columns', []):
            if column.get('key') == cell_key:
                return column

    return None
```

## Summary Sheet Custom Column Keys

In summary sheets, `customColumns` use special keys:

| Key | Label | Description |
|-----|-------|-------------|
| `mrq` | MRQ | Most Recent Quarter |
| `mrqMinusOne` | MRQ-1 | Previous year's same quarter |
| `ltm` | LTM | Last Twelve Months |
| `ltmMinusOne` | LTM-1 | Previous year's LTM |

These map to `syntheticColumnKey` values:
```json
{
  "key": "mrq",
  "label": "MRQ",
  "syntheticColumnKey": "pr=Q3-2025|ed=9/30/2025"
}
```

When a cell has `columnKey: "mrq"`, use the `syntheticColumnKey` to understand the actual period.
