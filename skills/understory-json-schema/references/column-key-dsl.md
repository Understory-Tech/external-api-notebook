# Column Key DSL Format

Column keys use a domain-specific language (DSL) to uniquely identify time periods. This document explains the format and how to parse it.

## Format Overview

Column keys are pipe-delimited strings with key-value pairs:

```
pr=FY-2023|ed=12/31/2023|dr=12-months
```

Each segment follows the pattern `key=value`, separated by `|`.

## Field Definitions

| Field | Name | Description | Examples |
|-------|------|-------------|----------|
| `pr` | Period | Fiscal period identifier | `FY-2023`, `Q1-2024`, `Q3-2025` |
| `ed` | End Date | Period end date (M/D/YYYY) | `12/31/2023`, `9/30/2025` |
| `sd` | Start Date | Period start date (M/D/YYYY) | `1/1/2023`, `7/1/2024` |
| `dr` | Duration | Period duration | `12-months`, `3-months`, `1-months` |
| `xtd` | Year-to-Date | YTD indicator | `ytd` |

## Common Patterns

### Fiscal Year
```
pr=FY-2023|ed=12/31/2023|dr=12-months
```
Full fiscal year ending December 31, 2023.

### Quarterly
```
pr=Q1-2024|ed=4/1/2024|dr=3-months
```
First quarter of fiscal 2024.

### Year-to-Date
```
pr=Q3-2024|ed=9/30/2024|dr=9-months|xtd=ytd
```
Nine months ending September 30, 2024.

### Date Range
```
pr=Q3-2023|sd=1/1/2023|ed=10/1/2023|dr=9-months
```
Custom range with explicit start and end dates.

### Point-in-Time (No Duration)
```
pr=null|ed=3/16/2020
```
Snapshot date without a duration period.

### Duration Only (No Period Label)
```
pr=null|ed=12/31/2017|dr=12-months
```
12-month duration ending on a specific date, no fiscal period label.

## Period Types

The `pr` field contains a period type and year:

| Pattern | Type | Duration |
|---------|------|----------|
| `FY-YYYY` | Fiscal Year | 12 months |
| `Q1-YYYY` | Quarter 1 | 3 months |
| `Q2-YYYY` | Quarter 2 | 3 months |
| `Q3-YYYY` | Quarter 3 | 3 months |
| `Q4-YYYY` | Quarter 4 | 3 months |
| `null` | No period | Varies |

For parsing implementations, see [common-operations.py](../examples/common-operations.py) and [company-model-parser-utils.py](../examples/company-model-parser-utils.py).

For summary sheet custom column keys (`mrq`, `ltm`, etc.), see [summary-sheet.md](summary-sheet.md).
