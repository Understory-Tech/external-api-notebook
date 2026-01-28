# Summary Sheet Structure

Models generated with summary configuration (version >= 2.0.0) include a `summary` object containing curated financial metrics with synthetic columns for common analysis periods.

## When Summary is Available

Summary sheets are included when:
- Model version is 2.0.0 or higher
- Model was generated with summary configuration enabled
- Request included `version: "2.0.0"` in download options

Check for summary:
```python
if 'summary' in model and model['summary']:
    # Summary sheet is available
    summary = model['summary']
```

---

## Summary Structure

```json
{
  "summary": {
    "table": {
      "id": "string",
      "index": 0,
      "sections": [...]
    },
    "columnGroups": [...],
    "customColumns": [
      {
        "key": "mrq",
        "label": "MRQ",
        "syntheticColumnKey": "pr=Q3-2025|ed=9/30/2025"
      },
      {
        "key": "mrqMinusOne",
        "label": "MRQ-1",
        "syntheticColumnKey": "pr=Q3-2024|ed=9/30/2024|dr=3-months"
      },
      {
        "key": "ltmMinusOne",
        "label": "LTM-1",
        "syntheticColumnKey": "pr=Q3-2024|ed=9/30/2024|dr=12-months"
      },
      {
        "key": "ltm",
        "label": "LTM",
        "syntheticColumnKey": "pr=Q3-2025|ed=9/30/2025|dr=12-months"
      }
    ]
  }
}
```

---

## Table Structure

The summary `table` follows the same hierarchy as tableGroups: sections → rows → cells.

```json
{
  "table": {
    "id": "summary_table_id",
    "index": 0,
    "sections": [
      {
        "type": "rbfSection",
        "name": "none",
        "isMainSection": true,
        "data": [
          {
            "type": "row",
            "label": {
              "definedName": "metric_cash_4lnb",
              "text": "Cash",
              "style": "header"
            },
            "cells": [...]
          }
        ]
      }
    ]
  }
}
```

### Row Labels

Summary rows have descriptive labels with optional styling:

| Field | Type | Description |
|-------|------|-------------|
| `definedName` | string | Unique identifier (e.g., `metric_cash_4lnb`) |
| `text` | string | Display text |
| `style` | string | Row style (`"header"`, `"subheader"`, etc.) |

---

## Custom Columns

Custom columns are synthetic periods computed by Understory:

| Key | Label | Description |
|-----|-------|-------------|
| `mrq` | MRQ | Most Recent Quarter |
| `mrqMinusOne` | MRQ-1 | Same quarter, previous year |
| `ltm` | LTM | Last Twelve Months (trailing) |
| `ltmMinusOne` | LTM-1 | LTM from previous year |

Each custom column includes a `syntheticColumnKey` that maps to the actual period:

```json
{
  "key": "ltm",
  "label": "LTM",
  "syntheticColumnKey": "pr=Q3-2025|ed=9/30/2025|dr=12-months"
}
```

---

## Summary Cell Structure

Summary cells are similar to regular cells but may include additional fields:

```json
{
  "value": {
    "type": "formula",
    "formula": {
      "value": {
        "rowDefinedName": "metric_cash_4lnb",
        "colKey": "pr=Q3-2025|ed=9/30/2025|dr=3-months"
      }
    },
    "unit": "dollar",
    "format": "american",
    "decimalPlaces": 0
  },
  "columnKey": "mrq",
  "isForecast": false,
  "isCustom": true,
  "link": null,
  "sourceMeta": null,
  "fontColor": "000000",
  "outdatedCells": null
}
```

### Summary-Specific Fields

| Field | Type | Description |
|-------|------|-------------|
| `isCustom` | boolean | `true` for synthetic/computed columns |
| `fontColor` | string | Hex color code for display styling |
| `columnKey` | string | May be a custom column key like `"mrq"` |

### Identifying Custom Column Cells

```python
def is_custom_column_cell(cell: dict) -> bool:
    """Check if a cell is from a custom/synthetic column."""
    return cell.get('isCustom', False)
```

---

## Column Groups

Summary sheets have their own `columnGroups` array defining available periods:

```json
{
  "columnGroups": [
    {
      "type": "standardFyPeriods",
      "columns": [
        {
          "period": {...},
          "endDate": "2023-12-31T00:00:00.000Z",
          "duration": {...},
          "key": "pr=FY-2023|ed=12/31/2023|dr=12-months"
        }
      ]
    }
  ]
}
```

These column groups apply specifically to the summary table and may differ from the main model's column groups.

---

## Common Summary Metrics

Summary sheets typically include:

- **Balance Sheet Items:** Cash, Total Assets, Total Debt, Shareholders' Equity
- **Income Statement Items:** Revenue, Gross Profit, Operating Income, Net Income
- **Per Share Data:** EPS, Dividends
- **Ratios:** Margins, Growth Rates

---

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
    """
    Find a summary row by its label text.

    Args:
        model: The CompanyModel
        label_text: Text to search for (case-insensitive)

    Returns:
        The matching row or None
    """
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
