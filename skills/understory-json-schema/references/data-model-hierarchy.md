# Data Model Hierarchy

This document provides a structural overview of the Understory CompanyModel JSON. For complete field definitions, see the [OpenAPI spec](https://api.demo.understorytech.com/docs) → `#/components/schemas/companyJsonModel`.

## Hierarchy Overview

```
CompanyModel
├── companyModelId, companyId, companyName
├── meta (version, createdAt, modelType, withFigures)
├── columnGroups[]           → Time period definitions
│   └── columns[]            → Individual column with key, period, duration
├── tableGroups[]            → Financial data by category
│   └── tables[]
│       └── sections[]
│           └── data[]       → rows and nested sections
│               └── cells[]  → values with sourceMeta
├── summary                  → Summary sheet (v2.0.0+)
├── skippedTables[]          → Tables excluded from stitching
└── figures                  → Chart/graph data
```

## Column Groups

Column groups define time periods. See OpenAPI `companyJsonModel.columnGroups[].type` for the full enum of group types (e.g., `standardFyPeriods`, `standard3MonthPeriods`, `dateRanges`).

Each column has a `key` in DSL format (see [column-key-dsl.md](column-key-dsl.md)) used to match cells.

## Table Groups

Table groups organize data by category. See OpenAPI `companyJsonModel.tableGroups[].category` for valid categories (Income Statement, Balance Sheet, Cash Flow, etc.).

### Structure Flow

```
tableGroups[].tables[].sections[].data[] → rows with cells
```

The `data` array can contain:
- `{ "type": "row", ... }` - Data rows with label and cells
- `{ "type": "section", ... }` - Nested subsections

## Rows

Rows contain financial data. See OpenAPI `#/components/schemas/modelRow` for field definitions.

Key fields:
- `label.text` - Display text (e.g., "REVENUE")
- `label.definedName` - Unique identifier for formula references
- `label.style` - Row style (header, subheader, total, etc.)
- `cells[]` - Values for each time period

## Cells

Cells contain values with full metadata. Key fields:
- `value` - The data (see [openapi-reference.md](openapi-reference.md) for value types)
- `columnKey` - Matches a column definition
- `sourceMeta` - PDF source location (see [source-meta-and-geometry.md](source-meta-and-geometry.md))
- `isForecast`, `isDeprecated` - Status flags

## Skipped Tables

Tables parsed from PDFs but not included in the stitched model. Contains the original table data, document info, and position on page.
