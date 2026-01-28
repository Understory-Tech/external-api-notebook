# Data Model Hierarchy

This document describes the complete hierarchy of the Understory CompanyModel JSON structure.

## Top-Level Keys

| Key | Type | Description |
|-----|------|-------------|
| `companyModelId` | string | Unique identifier for this model |
| `companyId` | UUID | Parent company identifier |
| `companyName` | string | Display name (includes filing types) |
| `columnGroups` | array | Time period column definitions |
| `tableGroups` | array | Financial data organized by category |
| `summary` | object | Summary sheet (optional, version >= 2.0.0) |
| `skippedTables` | array | Tables excluded from the stitched model |
| `figures` | object | Chart and graph data |
| `meta` | object | Generation metadata |

---

## Column Groups

Column groups define the time periods (columns) available in the model. Each group has a specific type and contains column definitions.

### Structure

```json
{
  "columnGroups": [
    {
      "type": "standardFyPeriods",
      "columns": [
        {
          "period": {
            "term": {
              "type": "FY",
              "standardDurationInMonths": 12
            },
            "year": { "year": 2023 }
          },
          "endDate": "2023-12-31T00:00:00.000Z",
          "duration": {
            "numberOfMonths": 12,
            "number": 12,
            "unit": "months"
          },
          "stub": false,
          "key": "pr=FY-2023|ed=12/31/2023|dr=12-months"
        }
      ]
    }
  ]
}
```

### Column Group Types

| Type | Description |
|------|-------------|
| `standardFyPeriods` | Fiscal year periods (FY-2023, FY-2022, etc.) |
| `standard3MonthPeriods` | Quarterly periods (Q1-2024, Q2-2024, etc.) |
| `standard1MonthDurations` | Monthly periods |
| `standardFyDurations` | Annual durations without specific period labels |
| `dateRanges` | Custom date ranges with start and end dates |
| `ytdDates` | Year-to-date periods |
| `endDatesNoDuration` | Point-in-time dates without duration |

### Column Fields

| Field | Type | Description |
|-------|------|-------------|
| `period` | object | Period information (term type, year) |
| `period.term.type` | string | "FY" or "Q" with optional number |
| `period.year.year` | number | Fiscal year |
| `endDate` | ISO-8601 | Period end date |
| `startDate` | ISO-8601 | Period start date (for ranges) |
| `duration` | object | Duration specification |
| `stub` | boolean | Whether this is a stub period |
| `key` | string | DSL key for matching cells |

---

## Table Groups

Table groups organize financial data by category. Each group contains one or more tables.

### Structure

```json
{
  "tableGroups": [
    {
      "category": "Income Statement",
      "tables": [
        {
          "id": "ddsprc5a",
          "tableType": "incomeStatement",
          "name": "Income Statement",
          "textractTitle": "Consolidated Statements of Operations",
          "description": "...",
          "index": 0,
          "sourceTableIds": ["abc123", "def456"],
          "sections": [...]
        }
      ]
    }
  ]
}
```

### Common Categories

- Income Statement
- Balance Sheet
- Cash Flow Statement
- Comprehensive Income
- Stockholders' Equity
- Revenue Segmentation
- Geographic Segmentation
- Operating Expenses
- Debt Schedule
- Other

### Table Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique table identifier |
| `tableType` | string | Semantic type (incomeStatement, balanceSheet, etc.) |
| `name` | string | Display name |
| `textractTitle` | string | Title from source PDF |
| `description` | string | AI-generated description |
| `index` | number | Sort order within group |
| `sourceTableIds` | array | IDs of source FileModel tables |
| `sections` | array | Table sections containing rows |

---

## Sections

Sections organize rows within a table. A section contains a data array with rows and potentially nested subsections.

### Structure

```json
{
  "sections": [
    {
      "type": "rbfSection",
      "name": "none",
      "isMainSection": true,
      "data": [
        { "type": "row", ... },
        { "type": "section", ... }
      ]
    }
  ]
}
```

### Section Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always "rbfSection" |
| `name` | string | Section name (or "none") |
| `isMainSection` | boolean | Whether this is the primary section |
| `data` | array | Array of rows and nested sections |

### Data Item Types

The `data` array can contain:
- `{ "type": "row", ... }` - Data rows with cells
- `{ "type": "section", ... }` - Nested subsections

---

## Rows

Rows contain the actual financial data. Each row has a label and an array of cells.

### Structure

```json
{
  "type": "row",
  "label": {
    "definedName": "r_table_ddsprc5a_section_none_row_revenue_1",
    "text": "REVENUE",
    "style": "header",
    "comment": {
      "texts": [
        {
          "text": "2 row label variations found...",
          "font": { "bold": true }
        }
      ]
    }
  },
  "cells": [...]
}
```

### Row Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always "row" |
| `label` | object | Row label information |
| `label.definedName` | string | Unique identifier for formulas |
| `label.text` | string | Display text |
| `label.style` | string | "header", "subheader", "total", etc. |
| `label.comment` | object | Rich text annotations |
| `cells` | array | Cell values for each period |

---

## Cells

Cells contain the actual data values with full metadata and source traceability.

### Structure

```json
{
  "value": {
    "type": "dollar",
    "value": 918688,
    "format": "american",
    "decimalPlaces": 0
  },
  "columnKey": "pr=FY-2021|ed=12/31/2021|dr=12-months",
  "isForecast": false,
  "isDeprecated": false,
  "definedName": "table_zihiurdn_row_3_column_4",
  "link": "company/{companyId}/files/{fileId}?page=80&table=zihiurdn",
  "comment": {
    "texts": [
      { "text": "Filename: ", "font": { "bold": true } },
      { "text": "2023-12-31 - 10-K - 10-K.pdf" }
    ]
  },
  "sourceMeta": {
    "fileId": "02d399ee-aa37-4aca-b3a5-ee8cf057228a",
    "pageId": "cfa0039a-9716-4590-b9b8-52e8c452d8d9",
    "tableId": "zihiurdn",
    "pageNumber": 80,
    "rowIndex": 3,
    "columnIndex": 4,
    "boundingBox": {
      "top": 0.172,
      "left": 0.826,
      "width": 0.124,
      "height": 0.014
    }
  },
  "sourceRowIds": ["table_zihiurdn_row_3", "table_r7xz3ylr_row_3"],
  "outdatedCells": null
}
```

### Cell Fields

| Field | Type | Description |
|-------|------|-------------|
| `value` | object | The data value (see Value Types) |
| `columnKey` | string | DSL key matching a column definition |
| `isForecast` | boolean | Whether this is a forecast value |
| `isDeprecated` | boolean | Whether this value is outdated |
| `isCustom` | boolean | Whether this is a synthetic value (summary only) |
| `definedName` | string | Unique identifier for formula references |
| `link` | string | Relative URL to view source |
| `comment` | object | Rich text annotations |
| `sourceMeta` | object | PDF source location |
| `sourceRowIds` | array | IDs of source FileModel rows |
| `outdatedCells` | array | Previous values if updated |
| `fontColor` | string | Hex color code (summary only) |

---

## Skipped Tables

Tables that were parsed from source PDFs but not included in the stitched model.

### Structure

```json
{
  "skippedTables": [
    {
      "id": "kfhkkryy",
      "title": "Table of Contents",
      "description": "...",
      "document": {
        "filename": "2025-06-30 - 10-Q - 10-Q.pdf",
        "id": "uuid"
      },
      "source": "table",
      "firstPageNumber": 2,
      "firstPageTopPosition": 0.21,
      "textractTitle": "...",
      "data": [...],
      "levenshteinId": "...",
      "usedRbfCount": 0,
      "densityScore": 0.5,
      "rowCount": 15
    }
  ]
}
```

---

## Figures

Chart and graph data extracted from source PDFs.

### Structure

```json
{
  "figures": {
    "columnGroups": [...],
    "tableGroups": [...]
  }
}
```

Figures follow a similar structure to the main model but contain data points extracted from charts rather than tables.

---

## Meta

Model generation metadata.

### Structure

```json
{
  "meta": {
    "createdAt": "2026-01-28T00:36:26.809Z",
    "version": "2.0.0",
    "modelType": "json-condensed",
    "withFigures": true
  }
}
```

### Meta Fields

| Field | Type | Description |
|-------|------|-------------|
| `createdAt` | ISO-8601 | Generation timestamp |
| `version` | string | Model schema version |
| `modelType` | string | Output format type |
| `withFigures` | boolean | Whether figures are included |
