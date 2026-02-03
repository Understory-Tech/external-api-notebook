# Cell Types and Values

This document covers practical guidance for working with cell values. For complete type definitions, see [OpenAPI spec](https://api.demo.understorytech.com/docs) → `#/components/schemas/cellValue`.

## Value Types Overview

| Type | Description | Key Consideration |
|------|-------------|-------------------|
| `dollar` | Currency values | Check table context for scale (thousands, millions) |
| `number` | Generic numeric | Shares, counts, ratios |
| `percent` | Percentages | **Stored as decimals** (0.057 = 5.7%) |
| `multiple` | Multipliers | P/E ratios, EBITDA multiples |
| `string` | Text values | Often indicates parsing issues |
| `formula` | Calculated values | Contains formula tree (see below) |

## Percentage Handling

Percentages are stored as decimals. Always multiply by 100 for display:

```python
display_value = cell['value']['value'] * 100  # -0.057 → -5.7%
```

## Formula Tree Structure

Formula values contain a recursive tree structure for calculations. This is **unique content not fully defined in OpenAPI**.

### Operators

| Operator | Description | Structure |
|----------|-------------|-----------|
| `ADD` | Addition | `{ operator, left, right }` |
| `SUBTRACT` | Subtraction | `{ operator, left, right }` |
| `MULTIPLY` | Multiplication | `{ operator, left, right }` |
| `DIVIDE` | Division | `{ operator, left, right }` |
| `NEGATE` | Negation | `{ operator, operand }` |

### Cell References

Leaf nodes reference other cells:

```json
{
  "value": {
    "rowDefinedName": "r_table_abc_section_none_row_revenue_1",
    "colKey": "pr=FY-2023|ed=12/31/2023|dr=12-months"
  }
}
```

### Literal Values

Some formulas include literal numeric values:

```json
{
  "value": 1000000
}
```

### Example: Revenue minus Cost

```json
{
  "operator": "SUBTRACT",
  "left": {
    "value": {
      "rowDefinedName": "r_table_abc_row_revenue_1",
      "colKey": "pr=FY-2023|ed=12/31/2023|dr=12-months"
    }
  },
  "right": {
    "value": {
      "rowDefinedName": "r_table_abc_row_cost_1",
      "colKey": "pr=FY-2023|ed=12/31/2023|dr=12-months"
    }
  }
}
```

## Extracting Values

```python
def extract_value(cell: dict) -> tuple:
    """
    Extract the numeric value and type from a cell.

    Returns:
        Tuple of (value, type_str) or (None, None) if no value
    """
    if not cell or 'value' not in cell:
        return None, None

    val = cell['value']
    val_type = val.get('type')

    if val_type == 'formula':
        # Use pre-computed value if available
        if 'value' in val:
            return val['value'], val.get('unit', 'number')
        # Otherwise need to evaluate formula tree
        return None, 'formula'

    elif val_type in ('dollar', 'number', 'percent', 'multiple'):
        return val.get('value'), val_type

    elif val_type == 'string':
        return val.get('value'), 'string'

    return None, None


def format_value(value, value_type: str, decimal_places: int = 0) -> str:
    """Format a value for display."""
    if value is None:
        return ''

    if value_type == 'percent':
        return f"{value * 100:.{decimal_places}f}%"
    elif value_type == 'dollar':
        return f"${value:,.{decimal_places}f}"
    elif value_type == 'multiple':
        return f"{value:.{decimal_places}f}x"
    else:
        return f"{value:,.{decimal_places}f}"
```

## Cell Metadata

Beyond the value, cells contain metadata. See OpenAPI `#/components/schemas/modelRow` → `cells[]` for complete field list. Key fields:

- `columnKey` - DSL key identifying time period
- `definedName` - Unique identifier for formula references
- `isForecast` - Whether this is a projected value
- `isDeprecated` - Whether this value has been superseded
- `isCustom` - Whether this is a synthetic value (summary only)
- `sourceMeta` - PDF source location (see [source-meta-and-geometry.md](source-meta-and-geometry.md))
- `comment` - Rich text annotations
