# Cell Types and Values

This document describes the different value types found in Understory model cells and their metadata fields.

## Value Types

Every cell contains a `value` object with a `type` field indicating the data type.

### Dollar

Currency values representing monetary amounts.

```json
{
  "value": {
    "type": "dollar",
    "value": 918688,
    "format": "american",
    "decimalPlaces": 0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"dollar"` |
| `value` | number | Numeric value (typically in thousands) |
| `format` | string | Number format (`"american"`) |
| `decimalPlaces` | number | Decimal precision |

**Note:** Values are typically stored in the same scale as the source document. Check table context for whether values are in thousands, millions, etc.

### Number

Generic numeric values (shares, counts, ratios without units).

```json
{
  "value": {
    "type": "number",
    "value": 248152,
    "format": "american",
    "decimalPlaces": 0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"number"` |
| `value` | number | Numeric value |
| `format` | string | Number format |
| `decimalPlaces` | number | Decimal precision |

### Percent

Percentage values stored as decimals.

```json
{
  "value": {
    "type": "percent",
    "value": -0.057,
    "format": "american",
    "decimalPlaces": 1
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"percent"` |
| `value` | number | Decimal value (0.057 = 5.7%) |
| `format` | string | Number format |
| `decimalPlaces` | number | Decimal precision for display |

**Important:** Percentages are stored as decimals. Multiply by 100 for display:
```python
display_value = cell['value']['value'] * 100  # -0.057 → -5.7%
```

### Multiple

Multiplier values (e.g., P/E ratios, EBITDA multiples).

```json
{
  "value": {
    "type": "multiple",
    "value": 13.7,
    "format": "american",
    "decimalPlaces": 1
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"multiple"` |
| `value` | number | Multiplier value |
| `format` | string | Number format |
| `decimalPlaces` | number | Decimal precision |

### String

Text values that couldn't be parsed as numbers.

```json
{
  "value": {
    "type": "string",
    "value": "407,312,26"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"string"` |
| `value` | string | Raw text content |

String values often indicate parsing issues or complex formatting in the source.

### Formula

Calculated values with a formula tree structure.

```json
{
  "value": {
    "type": "formula",
    "formula": {
      "operator": "SUBTRACT",
      "left": {
        "value": {
          "rowDefinedName": "r_table_abc_section_none_row_revenue_1",
          "colKey": "pr=FY-2023|ed=12/31/2023|dr=12-months"
        }
      },
      "right": {
        "value": {
          "rowDefinedName": "r_table_abc_section_none_row_cost_1",
          "colKey": "pr=FY-2023|ed=12/31/2023|dr=12-months"
        }
      }
    },
    "unit": "dollar",
    "format": "american",
    "decimalPlaces": 0
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"formula"` |
| `formula` | object | Formula tree (see below) |
| `value` | number | Pre-computed result (sometimes present) |
| `unit` | string | Result unit type (`"dollar"`, `"number"`, etc.) |
| `format` | string | Number format |
| `decimalPlaces` | number | Decimal precision |

---

## Formula Tree Structure

Formula values contain a recursive tree structure representing calculations.

### Operators

| Operator | Description | Structure |
|----------|-------------|-----------|
| `ADD` | Addition | `{ left, right }` |
| `SUBTRACT` | Subtraction | `{ left, right }` |
| `MULTIPLY` | Multiplication | `{ left, right }` |
| `DIVIDE` | Division | `{ left, right }` |
| `NEGATE` | Negation | `{ operand }` |

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

| Field | Type | Description |
|-------|------|-------------|
| `rowDefinedName` | string | Target row's definedName |
| `colKey` | string | Target column key |

### Literal Values

Some formulas include literal values:

```json
{
  "value": 1000000
}
```

### Example Formula Tree

Revenue minus Cost of Revenue:

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

---

## Cell Metadata Fields

Beyond the value, cells contain rich metadata.

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `columnKey` | string | DSL key identifying the time period |
| `definedName` | string | Unique identifier for formula references |
| `isForecast` | boolean | Whether this is a projected/forecast value |
| `isDeprecated` | boolean | Whether this value has been superseded |
| `isCustom` | boolean | Whether this is a synthetic value (summary only) |

### Source Traceability

| Field | Type | Description |
|-------|------|-------------|
| `sourceMeta` | object | PDF source location (see [source-meta-and-geometry.md](source-meta-and-geometry.md)) |
| `sourceRowIds` | array | IDs of source FileModel rows |
| `link` | string | Relative URL to view in Understory UI |
| `outdatedCells` | array | Previous values if this cell was updated |

### Annotations

| Field | Type | Description |
|-------|------|-------------|
| `comment` | object | Rich text annotations |
| `fontColor` | string | Hex color code (summary sheet only) |

### Comment Structure

```json
{
  "comment": {
    "texts": [
      {
        "text": "Filename: ",
        "font": { "bold": true }
      },
      {
        "text": "2023-12-31 - 10-K - 10-K.pdf"
      },
      {
        "text": " Page #: ",
        "font": { "bold": true }
      },
      {
        "text": "80"
      }
    ]
  }
}
```

Each text segment can have font styling:

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Text content |
| `font` | object | Font styling |
| `font.bold` | boolean | Bold text |
| `font.italic` | boolean | Italic text |
| `font.underline` | boolean | Underlined text |
| `font.color` | string | Text color (hex) |

---

## Extracting Values

### Python Helper

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
