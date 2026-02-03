# OpenAPI Specification Reference

This document explains how the skill documentation relates to the [Understory OpenAPI specification](https://api.demo.understorytech.com/docs) and where to find authoritative schema definitions.

## Relationship to Skill Documentation

The OpenAPI spec at https://api.demo.understorytech.com/docs is the **authoritative source** for schema definitions. The skill documentation in this folder provides:

1. **Practical guidance** - How to work with the data (parsing, transformations, utilities)
2. **Unique concepts** - Features not captured in OpenAPI (Column Key DSL, formula evaluation)
3. **Code examples** - Working implementations for common tasks
4. **Workflow patterns** - Step-by-step guides for extracting data

For detailed field definitions and type constraints, refer to the OpenAPI spec directly.

## Key Schema Locations

| Concept | OpenAPI Location | Skill Doc |
|---------|-----------------|-----------|
| CompanyModel (top-level) | `#/components/schemas/companyJsonModel` | [data-model-hierarchy.md](data-model-hierarchy.md) |
| Cell value types | `#/components/schemas/cellValue` | [cell-types-and-values.md](cell-types-and-values.md) |
| Source metadata | `#/components/schemas/sourceMetadata` | [source-meta-and-geometry.md](source-meta-and-geometry.md) |
| Period definition | `#/components/schemas/period` | [column-key-dsl.md](column-key-dsl.md) |
| Duration definition | `#/components/schemas/duration` | [column-key-dsl.md](column-key-dsl.md) |
| Row structure | `#/components/schemas/modelRow` | [data-model-hierarchy.md](data-model-hierarchy.md) |
| Comments/Rich text | `#/components/schemas/comment` | [cell-types-and-values.md](cell-types-and-values.md) |

## Navigating the OpenAPI Spec

### Finding Schema Definitions

All reusable schemas are under `components.schemas`:

```json
{
  "components": {
    "schemas": {
      "cellValue": { ... },
      "sourceMetadata": { ... },
      "companyJsonModel": { ... }
    }
  }
}
```

### Understanding $ref References

The spec uses JSON References to reuse schemas:

```json
{
  "sourceMeta": {
    "$ref": "#/components/schemas/sourceMetadata"
  }
}
```

This means the `sourceMeta` field follows the `sourceMetadata` schema definition.

### Column Group Types

The `companyJsonModel.columnGroups[].type` enum defines all valid column group types:

- `standardFyPeriods` - Fiscal year periods
- `standard3MonthPeriods` - Quarterly periods
- `standard6MonthPeriods` - Semi-annual periods
- `standard1MonthDurations` - Monthly periods
- `standardFyDurations` - Annual durations
- `dateRanges` - Custom date ranges
- `endDatesNoDuration` - Point-in-time dates
- Various non-standard period types

### Table Categories

The `companyJsonModel.tableGroups[].category` enum defines valid categories:

- Income Statement
- Balance Sheet
- Cash Flow
- EBITDA
- Free Cash Flow
- Earnings Per Share
- Other Consolidated Financial Metrics & Adjustments
- Segments
- Operational Data & KPIs
- Capitalization, Liquidity, and Covenant Metrics
- Other

### Cell Value Types

The `cellValue` schema uses `anyOf` to define the possible value types:

- **Numeric Cell** - `type`: `number`, `dollar`, `percent`, `multiple`
- **Formula Cell** - `type`: `formula` with a formula tree
- **String Cell** - `type`: `string`
- **Null Cell** - Empty cells
- **Error Cell** - Cells with parsing errors

## Content NOT in OpenAPI

The following concepts are documented in skill docs but **not** defined in the OpenAPI spec:

### Column Key DSL (Unique)

The pipe-delimited format `pr=FY-2023|ed=12/31/2023|dr=12-months` is a runtime format not defined in OpenAPI. See [column-key-dsl.md](column-key-dsl.md) for parsing.

### Formula Tree Evaluation (Unique)

The formula tree structure (`ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`, `NEGATE` operators) and evaluation logic is documented in [cell-types-and-values.md](cell-types-and-values.md).

### Bounding Box Pixel Conversion (Unique)

Utility functions for converting ratio coordinates to pixels are in [source-meta-and-geometry.md](source-meta-and-geometry.md).

### Summary Sheet Custom Columns (Unique)

The `mrq`, `mrqMinusOne`, `ltm`, `ltmMinusOne` semantics for summary sheets are documented in [summary-sheet.md](summary-sheet.md).

## Generating Types from OpenAPI

TypeScript types can be generated from the OpenAPI spec using tools like:

- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [openapi-generator](https://openapi-generator.tech/)

Example with openapi-typescript:

```bash
# Download the spec and generate types
curl -o api.json https://api.demo.understorytech.com/docs-json
npx openapi-typescript api.json -o types/api.ts
```

Types can also be auto-generated from the OpenAPI spec using the command above.
