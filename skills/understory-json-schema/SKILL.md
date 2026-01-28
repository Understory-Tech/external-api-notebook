# Understory JSON Schema Documentation

Provides comprehensive documentation for the Understory API's CompanyModel JSON structure, enabling developers to build downstream applications that consume financial model data.

## Trigger Phrases

- "Understory model JSON"
- "parse company model data"
- "CompanyModel structure"
- "Understory API response format"
- "financial model JSON schema"
- "extract data from Understory model"
- "Understory cell types"
- "columnKey format"
- "boundingBox coordinates"

---

## Overview

The Understory API generates structured JSON representations of financial models extracted from PDF documents. A **CompanyModel** contains stitched financial data from multiple uploaded files (10-Ks, 10-Qs, etc.), organized into hierarchical tables with full traceability back to source PDFs.

## Top-Level Structure

```json
{
  "companyModelId": "string",    // Unique model identifier
  "companyId": "uuid",           // Parent company UUID
  "companyName": "string",       // Display name
  "columnGroups": [...],         // Time period definitions
  "tableGroups": [...],          // Financial data (Income Statement, Balance Sheet, etc.)
  "summary": {...},              // Summary sheet (optional, version >= 2.0.0)
  "skippedTables": [...],        // Tables excluded from stitching
  "figures": {...},              // Chart/graph data
  "meta": {                      // Generation metadata
    "createdAt": "ISO-8601",
    "version": "2.0.0",
    "modelType": "json-condensed",
    "withFigures": true
  }
}
```

## Data Hierarchy

The primary data hierarchy flows:

```
tableGroups → tables → sections → rows → cells
```

Each **cell** contains:
- `value` - The data value with type information
- `columnKey` - DSL string identifying the time period
- `sourceMeta` - Traceability back to the source PDF location
- Metadata flags (`isForecast`, `isDeprecated`, etc.)

## Key Concepts

### Column Keys (DSL Format)

Column keys use a pipe-delimited DSL format:
```
pr=FY-2023|ed=12/31/2023|dr=12-months
```

Fields:
- `pr` - Period (FY-2023, Q1-2024, etc.)
- `ed` - End date
- `sd` - Start date (for ranges)
- `dr` - Duration (12-months, 3-months)
- `xtd` - Year-to-date indicator

See [column-key-dsl.md](references/column-key-dsl.md) for parsing details.

### Value Types

Cells can have these value types:
- `dollar` - Currency values with format and decimal places
- `number` - Numeric values (counts, shares, etc.)
- `percent` - Percentage values (stored as decimals, e.g., 0.057 = 5.7%)
- `formula` - Calculated values with recursive formula trees
- `string` - Text values
- `multiple` - Multiplier values (e.g., 13.7x)

See [cell-types-and-values.md](references/cell-types-and-values.md) for complete details.

### Source Traceability

Every cell includes `sourceMeta` linking back to the source PDF:
```json
{
  "sourceMeta": {
    "fileId": "uuid",
    "pageId": "uuid",
    "pageNumber": 80,
    "tableId": "string",
    "rowIndex": 3,
    "columnIndex": 4,
    "boundingBox": {
      "top": 0.172,      // Ratio from top (0.0 to 1.0)
      "left": 0.826,     // Ratio from left
      "width": 0.124,
      "height": 0.014
    }
  }
}
```

Bounding box coordinates are **ratios of page dimensions**, not pixels. To convert:
```python
pixel_x = left * page_width_px
pixel_y = top * page_height_px
```

See [source-meta-and-geometry.md](references/source-meta-and-geometry.md) for details.

### Summary Sheet (Version 2.0.0+)

Models generated with summary configuration include a `summary` object:
```json
{
  "summary": {
    "table": {...},           // Same structure: sections → rows → cells
    "columnGroups": [...],    // Period definitions for summary
    "customColumns": [        // Synthetic columns (MRQ, LTM, etc.)
      {
        "key": "mrq",
        "label": "MRQ",
        "syntheticColumnKey": "pr=Q3-2025|ed=9/30/2025"
      }
    ]
  }
}
```

Summary cells include `isCustom: true` for synthetic columns and `fontColor` for styling.

See [summary-sheet.md](references/summary-sheet.md) for details.

## Common Use Cases

### 1. Extract Income Statement Data
Navigate `tableGroups` to find `category: "Income Statement"`, then iterate rows.
See [common-operations.py](examples/common-operations.py) for `get_income_statement_data()`.

### 2. Build Time Series
Collect cells across a row, parse `columnKey` to order by date.
See [common-operations.py](examples/common-operations.py) for `build_time_series()`.

### 3. Link to Source PDFs
Use `sourceMeta.fileId` and `boundingBox` to highlight source cells.
See [source-meta-and-geometry.md](references/source-meta-and-geometry.md).

### 4. Evaluate Formulas
Formula values contain recursive tree structures with operators and cell references.
See [python-parser.py](examples/python-parser.py) for `evaluate_formula()`.

### 5. Access Summary Metrics
Extract MRQ, LTM values from the summary sheet's custom columns.
See [summary-sheet.py](examples/summary-sheet.py).

## Reference Documentation

- [data-model-hierarchy.md](references/data-model-hierarchy.md) - Complete hierarchy documentation
- [column-key-dsl.md](references/column-key-dsl.md) - Column key parsing guide
- [cell-types-and-values.md](references/cell-types-and-values.md) - Value type documentation
- [source-meta-and-geometry.md](references/source-meta-and-geometry.md) - PDF traceability
- [summary-sheet.md](references/summary-sheet.md) - Summary sheet structure

## Code Examples

- [python-parser.py](examples/python-parser.py) - Core parsing utilities
- [typescript-types.ts](examples/typescript-types.ts) - TypeScript type definitions
- [common-operations.py](examples/common-operations.py) - Common extraction patterns
- [summary-sheet.py](examples/summary-sheet.py) - Summary sheet utilities
