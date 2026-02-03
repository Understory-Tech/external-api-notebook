# Summary Sheet Structure

Models generated with summary configuration (version >= 2.0.0) include a `summary` object with curated financial metrics and synthetic columns for common analysis periods.

For base schema structure, see [OpenAPI spec](https://api.demo.understorytech.com/docs) → `#/components/schemas/companyJsonModel`. The summary sheet structure follows the same patterns as the main model but with additional custom column semantics documented here.

## When Summary is Available

Summary sheets are included when:
- Model version is 2.0.0 or higher
- Model was generated with summary configuration enabled
- Request included `version: "2.0.0"` in download options

```python
if 'summary' in model and model['summary']:
    summary = model['summary']
```

## Summary Structure Overview

```
summary
├── table              → Same structure as main tables: sections → rows → cells
├── columnGroups[]     → Period definitions specific to summary
└── customColumns[]    → Synthetic columns (MRQ, LTM, etc.)
```

## Custom Columns (Unique Content)

Custom columns are synthetic periods computed by Understory. **This is unique content not defined in the OpenAPI spec.**

| Key | Label | Description |
|-----|-------|-------------|
| `mrq` | MRQ | Most Recent Quarter |
| `mrqMinusOne` | MRQ-1 | Same quarter, previous year |
| `ltm` | LTM | Last Twelve Months (trailing 12) |
| `ltmMinusOne` | LTM-1 | LTM from previous year |

Each custom column includes a `syntheticColumnKey` mapping to the actual period:

```json
{
  "key": "ltm",
  "label": "LTM",
  "syntheticColumnKey": "pr=Q3-2025|ed=9/30/2025|dr=12-months"
}
```

## Summary Cell Differences

Summary cells have additional fields:

- `isCustom: true` - Indicates a synthetic/computed column
- `fontColor` - Hex color code for display styling
- `columnKey` - May be a custom key like `"mrq"` instead of standard DSL

## Extracting Summary Data

### Get All Summary Rows

```python
def get_summary_rows(model: dict) -> list:
    """Extract all rows from the summary table."""
    if 'summary' not in model or not model['summary']:
        return []

    rows = []
    table = model['summary'].get('table', {})

    for section in table.get('sections', []):
        for item in section.get('data', []):
            if item.get('type') == 'row':
                rows.append(item)

    return rows
```

### Get Custom Column Mapping

```python
def get_custom_column_mapping(model: dict) -> dict:
    """
    Get mapping of custom column keys to their definitions.

    Returns:
        Dict mapping key (e.g., 'mrq') to column definition
    """
    if 'summary' not in model or not model['summary']:
        return {}

    return {
        col['key']: col
        for col in model['summary'].get('customColumns', [])
    }
```

### Find Metric by Label

```python
def find_summary_metric(model: dict, label_text: str) -> dict:
    """Find a summary row by its label text (case-insensitive)."""
    for row in get_summary_rows(model):
        row_text = row.get('label', {}).get('text', '')
        if label_text.lower() in row_text.lower():
            return row
    return None
```

### Extract MRQ/LTM Values

```python
def get_custom_column_value(row: dict, column_key: str) -> dict:
    """
    Get the cell value for a custom column (mrq, ltm, etc.).

    Args:
        row: A summary row
        column_key: Custom column key ('mrq', 'mrqMinusOne', 'ltm', 'ltmMinusOne')

    Returns:
        The cell dict or None
    """
    for cell in row.get('cells', []):
        if cell.get('columnKey') == column_key:
            return cell
    return None


# Example: Get LTM Revenue
revenue_row = find_summary_metric(model, 'Revenue')
if revenue_row:
    ltm_cell = get_custom_column_value(revenue_row, 'ltm')
    if ltm_cell and 'value' in ltm_cell:
        # Extract value from formula or direct value
        pass
```

## Common Summary Metrics

Summary sheets typically include:

- **Balance Sheet Items:** Cash, Total Assets, Total Debt, Shareholders' Equity
- **Income Statement Items:** Revenue, Gross Profit, Operating Income, Net Income
- **Per Share Data:** EPS, Dividends
- **Ratios:** Margins, Growth Rates
