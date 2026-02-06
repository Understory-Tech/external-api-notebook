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

For extraction utilities, see [summary-sheet.py](../examples/summary-sheet.py).
