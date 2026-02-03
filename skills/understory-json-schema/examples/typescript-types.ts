/**
 * Understory CompanyModel TypeScript Type Definitions
 *
 * Complete type definitions for the Understory API CompanyModel JSON structure.
 *
 * NOTE: These types mirror the OpenAPI specification.
 * Types can also be auto-generated from the OpenAPI spec using tools like:
 * - openapi-typescript: `npx openapi-typescript api.json -o types/api.ts`
 * - openapi-generator: https://openapi-generator.tech/
 *
 * This hand-written file is provided as a reference implementation and may
 * include additional utility types not present in the OpenAPI spec.
 *
 * See: https://api.demo.understorytech.com/docs → #/components/schemas/companyJsonModel
 */

// =============================================================================
// Top-Level Model
// =============================================================================

export interface CompanyModel {
  companyModelId: string;
  companyId: string;
  companyName: string;
  columnGroups: ColumnGroup[];
  tableGroups: TableGroup[];
  summary?: Summary;
  skippedTables: SkippedTable[];
  figures: Figures;
  meta: ModelMeta;
}

export interface ModelMeta {
  createdAt: string; // ISO-8601 datetime
  version: string;
  modelType: string;
  withFigures: boolean;
}

// =============================================================================
// Column Groups
// =============================================================================

export type ColumnGroupType =
  | 'standardFyPeriods'
  | 'standard3MonthPeriods'
  | 'standard1MonthDurations'
  | 'standardFyDurations'
  | 'dateRanges'
  | 'ytdDates'
  | 'endDatesNoDuration';

export interface ColumnGroup {
  type: ColumnGroupType;
  columns: Column[];
}

export interface Column {
  period?: Period;
  endDate: string; // ISO-8601 datetime
  startDate?: string; // ISO-8601 datetime
  duration?: Duration;
  stub: boolean;
  key: string; // DSL format: pr=FY-2023|ed=12/31/2023|dr=12-months
}

export interface Period {
  term: PeriodTerm;
  year: { year: number };
}

export interface PeriodTerm {
  type: 'FY' | 'Q';
  number?: number; // Quarter number (1-4)
  standardDurationInMonths: number;
}

export interface Duration {
  numberOfMonths: number;
  number: number;
  unit: 'months';
}

// =============================================================================
// Table Groups
// =============================================================================

export type TableCategory =
  | 'Income Statement'
  | 'Balance Sheet'
  | 'Cash Flow Statement'
  | 'Comprehensive Income'
  | "Stockholders' Equity"
  | 'Revenue Segmentation'
  | 'Geographic Segmentation'
  | 'Operating Expenses'
  | 'Debt Schedule'
  | 'Other';

export interface TableGroup {
  category: TableCategory | string;
  tables: Table[];
}

export interface Table {
  id: string;
  tableType: string;
  name: string;
  textractTitle: string;
  description: string;
  index: number;
  sourceTableIds: string[];
  sections: Section[];
}

// =============================================================================
// Sections and Rows
// =============================================================================

export interface Section {
  type: 'rbfSection';
  name: string;
  isMainSection: boolean;
  data: SectionDataItem[];
}

export type SectionDataItem = Row | NestedSection;

export interface Row {
  type: 'row';
  label: RowLabel;
  cells: Cell[];
}

export interface NestedSection {
  type: 'section';
  name: string;
  data: SectionDataItem[];
}

export interface RowLabel {
  definedName: string;
  text: string;
  style?: 'header' | 'subheader' | 'total' | string;
  comment?: RichTextComment;
}

// =============================================================================
// Cells
// =============================================================================

export interface Cell {
  value: CellValue;
  columnKey: string;
  isForecast: boolean;
  isDeprecated: boolean;
  isCustom?: boolean; // Summary sheet only
  definedName?: string;
  link?: string | null;
  comment?: RichTextComment;
  sourceMeta?: SourceMeta | null;
  sourceRowIds?: string[];
  outdatedCells?: Cell[] | null;
  fontColor?: string; // Summary sheet only, hex color
}

// =============================================================================
// Cell Value Types
// =============================================================================

export type CellValue =
  | DollarValue
  | NumberValue
  | PercentValue
  | MultipleValue
  | StringValue
  | FormulaValue;

export interface DollarValue {
  type: 'dollar';
  value: number;
  format: 'american' | string;
  decimalPlaces: number;
}

export interface NumberValue {
  type: 'number';
  value: number;
  format: 'american' | string;
  decimalPlaces: number;
}

export interface PercentValue {
  type: 'percent';
  value: number; // Stored as decimal (0.057 = 5.7%)
  format: 'american' | string;
  decimalPlaces: number;
}

export interface MultipleValue {
  type: 'multiple';
  value: number;
  format: 'american' | string;
  decimalPlaces: number;
}

export interface StringValue {
  type: 'string';
  value: string;
}

export interface FormulaValue {
  type: 'formula';
  formula: FormulaNode;
  value?: number; // Pre-computed result
  unit?: 'dollar' | 'number' | 'percent' | string;
  format?: 'american' | string;
  decimalPlaces?: number;
}

// =============================================================================
// Formula Tree
// =============================================================================

export type FormulaNode =
  | BinaryOperatorNode
  | UnaryOperatorNode
  | CellReferenceNode
  | LiteralValueNode;

export interface BinaryOperatorNode {
  operator: 'ADD' | 'SUBTRACT' | 'MULTIPLY' | 'DIVIDE';
  left: FormulaNode;
  right: FormulaNode;
}

export interface UnaryOperatorNode {
  operator: 'NEGATE';
  operand: FormulaNode;
}

export interface CellReferenceNode {
  value: {
    rowDefinedName: string;
    colKey: string;
  };
}

export interface LiteralValueNode {
  value: number;
}

// =============================================================================
// Source Traceability
// =============================================================================

export interface SourceMeta {
  fileId: string; // UUID
  pageId: string; // UUID
  tableId: string;
  pageNumber: number;
  rowIndex: number;
  columnIndex: number;
  boundingBox: BoundingBox;
}

export interface BoundingBox {
  top: number; // Ratio 0.0 - 1.0
  left: number; // Ratio 0.0 - 1.0
  width: number; // Ratio 0.0 - 1.0
  height: number; // Ratio 0.0 - 1.0
}

// =============================================================================
// Comments and Rich Text
// =============================================================================

export interface RichTextComment {
  texts: RichTextSegment[];
}

export interface RichTextSegment {
  text: string;
  font?: FontStyle;
}

export interface FontStyle {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  color?: string; // Hex color
}

// =============================================================================
// Summary Sheet
// =============================================================================

export interface Summary {
  table: SummaryTable;
  columnGroups: ColumnGroup[];
  customColumns: CustomColumn[];
}

export interface SummaryTable {
  id: string;
  index: number;
  sections: Section[];
}

export interface CustomColumn {
  key: 'mrq' | 'mrqMinusOne' | 'ltm' | 'ltmMinusOne' | string;
  label: string;
  syntheticColumnKey: string;
}

// =============================================================================
// Skipped Tables
// =============================================================================

export interface SkippedTable {
  id: string;
  title: string;
  description: string;
  document: {
    filename: string;
    id: string;
  };
  source: string;
  firstPageNumber: number;
  firstPageTopPosition: number;
  textractTitle: string;
  data: SkippedTableCell[][];
  levenshteinId: string;
  usedRbfCount: number;
  densityScore: number;
  rowCount: number;
}

export interface SkippedTableCell {
  confidence: number;
  parsedValue: { value: unknown };
  originalText: string;
  isColumnHeader: boolean;
  words: Word[];
  sourceMeta: SourceMeta;
}

export interface Word {
  text: string;
  boundingBox: BoundingBox;
  confidence: number;
}

// =============================================================================
// Figures
// =============================================================================

export interface Figures {
  columnGroups: ColumnGroup[];
  tableGroups?: TableGroup[];
}

// =============================================================================
// Utility Types
// =============================================================================

/** Parsed column key structure */
export interface ParsedColumnKey {
  period: string | null;
  periodType: 'FY' | 'Q1' | 'Q2' | 'Q3' | 'Q4' | null;
  year: number | null;
  endDate: string | null;
  startDate: string | null;
  durationMonths: number | null;
  isYtd: boolean;
  raw: string;
}

/** Pixel coordinates converted from bounding box ratios */
export interface PixelCoordinates {
  x: number;
  y: number;
  width: number;
  height: number;
  x2: number;
  y2: number;
}

// =============================================================================
// Type Guards
// =============================================================================

export function isRow(item: SectionDataItem): item is Row {
  return item.type === 'row';
}

export function isNestedSection(item: SectionDataItem): item is NestedSection {
  return item.type === 'section';
}

export function isDollarValue(value: CellValue): value is DollarValue {
  return value.type === 'dollar';
}

export function isNumberValue(value: CellValue): value is NumberValue {
  return value.type === 'number';
}

export function isPercentValue(value: CellValue): value is PercentValue {
  return value.type === 'percent';
}

export function isMultipleValue(value: CellValue): value is MultipleValue {
  return value.type === 'multiple';
}

export function isStringValue(value: CellValue): value is StringValue {
  return value.type === 'string';
}

export function isFormulaValue(value: CellValue): value is FormulaValue {
  return value.type === 'formula';
}
