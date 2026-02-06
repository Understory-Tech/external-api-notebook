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
| Cell value types | `#/components/schemas/cellValue` | See `anyOf` variants: `number`, `dollar`, `percent`, `multiple`, `formula`, `string` |
| Source metadata | `#/components/schemas/sourceMetadata` | [source-meta-and-geometry.md](source-meta-and-geometry.md) |
| Period definition | `#/components/schemas/period` | [column-key-dsl.md](column-key-dsl.md) |
| Duration definition | `#/components/schemas/duration` | [column-key-dsl.md](column-key-dsl.md) |
| Row structure | `#/components/schemas/modelRow` | [data-model-hierarchy.md](data-model-hierarchy.md) |
| Comments/Rich text | `#/components/schemas/comment` | — |
| Column group types | `companyJsonModel.columnGroups[].type` enum | — |
| Table categories | `companyJsonModel.tableGroups[].category` enum | — |

## Content NOT in OpenAPI

The following concepts are documented in skill docs but **not** defined in the OpenAPI spec:

### Column Key DSL (Unique)

The pipe-delimited format `pr=FY-2023|ed=12/31/2023|dr=12-months` is a runtime format not defined in OpenAPI. See [column-key-dsl.md](column-key-dsl.md) for parsing.

### Formula Tree Structure (Unique)

Formula values contain a recursive tree structure for calculations.

#### Operators

| Operator | Description | Structure |
|----------|-------------|-----------|
| `ADD` | Addition | `{ operator, left, right }` |
| `SUBTRACT` | Subtraction | `{ operator, left, right }` |
| `MULTIPLY` | Multiplication | `{ operator, left, right }` |
| `DIVIDE` | Division | `{ operator, left, right }` |
| `NEGATE` | Negation | `{ operator, operand }` |

#### Cell References

Leaf nodes reference other cells:

```json
{
  "value": {
    "rowDefinedName": "r_table_abc_section_none_row_revenue_1",
    "colKey": "pr=FY-2023|ed=12/31/2023|dr=12-months"
  }
}
```

#### Literal Values

Some formulas include literal numeric values:

```json
{
  "value": 1000000
}
```

#### Example: Revenue minus Cost

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

### Bounding Box Pixel Conversion (Unique)

Utility functions for converting ratio coordinates to pixels are in [source-meta-and-geometry.md](source-meta-and-geometry.md).

### Summary Sheet Custom Columns (Unique)

The `mrq`, `mrqMinusOne`, `ltm`, `ltmMinusOne` semantics for summary sheets are documented in [summary-sheet.md](summary-sheet.md).
