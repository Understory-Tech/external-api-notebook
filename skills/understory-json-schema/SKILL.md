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

## OpenAPI Reference

For authoritative schema definitions, refer to the [OpenAPI specification](https://api.demo.understorytech.com/docs). Key schemas:

| Schema | Location |
|--------|----------|
| CompanyModel | `#/components/schemas/companyJsonModel` |
| Cell values | `#/components/schemas/cellValue` |
| Source metadata | `#/components/schemas/sourceMetadata` |
| Period/Duration | `#/components/schemas/period`, `#/components/schemas/duration` |
| Rows | `#/components/schemas/modelRow` |

See [openapi-reference.md](references/openapi-reference.md) for navigation guidance.

---

## Overview

The Understory API generates structured JSON representations of financial models extracted from PDF documents. A **CompanyModel** contains stitched financial data from multiple uploaded files (10-Ks, 10-Qs, etc.), organized into hierarchical tables with full traceability back to source PDFs.

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

See [data-model-hierarchy.md](references/data-model-hierarchy.md) for structural overview.

## Key Concepts

### Column Keys (DSL Format)

Column keys use a pipe-delimited DSL format unique to Understory:
```
pr=FY-2023|ed=12/31/2023|dr=12-months
```

Fields:
- `pr` - Period (FY-2023, Q1-2024, etc.)
- `ed` - End date
- `sd` - Start date (for ranges)
- `dr` - Duration (12-months, 3-months)
- `xtd` - Year-to-date indicator

See [column-key-dsl.md](references/column-key-dsl.md) for parsing details and implementation.

### Value Types

Cells can have these value types: `dollar`, `number`, `percent`, `formula`, `string`, `multiple`.

Key points:
- **Percentages** are stored as decimals (0.057 = 5.7%)
- **Formulas** contain recursive tree structures for calculations
- See OpenAPI `#/components/schemas/cellValue` for complete type definitions

See [cell-types-and-values.md](references/cell-types-and-values.md) for practical usage.

### Source Traceability

Every cell includes `sourceMeta` linking back to the source PDF with bounding box coordinates as **ratios of page dimensions** (0.0 to 1.0), not pixels.

To convert to pixels:
```python
pixel_x = left * page_width_px
pixel_y = top * page_height_px
```

See [source-meta-and-geometry.md](references/source-meta-and-geometry.md) for conversion utilities.

### Summary Sheet (Version 2.0.0+)

Models generated with summary configuration include a `summary` object with custom columns:
- `mrq` - Most Recent Quarter
- `mrqMinusOne` - Same quarter, previous year
- `ltm` - Last Twelve Months (trailing)
- `ltmMinusOne` - LTM from previous year

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

- [openapi-reference.md](references/openapi-reference.md) - OpenAPI spec navigation guide
- [data-model-hierarchy.md](references/data-model-hierarchy.md) - Structural overview
- [column-key-dsl.md](references/column-key-dsl.md) - Column key parsing (unique content)
- [cell-types-and-values.md](references/cell-types-and-values.md) - Value handling and formulas
- [source-meta-and-geometry.md](references/source-meta-and-geometry.md) - PDF traceability utilities
- [summary-sheet.md](references/summary-sheet.md) - Summary sheet custom columns

## Code Examples

- [python-parser.py](examples/python-parser.py) - Core parsing utilities
- [typescript-types.ts](examples/typescript-types.ts) - TypeScript type definitions (mirrors OpenAPI)
- [common-operations.py](examples/common-operations.py) - Common extraction patterns
- [summary-sheet.py](examples/summary-sheet.py) - Summary sheet utilities
