# Source Meta and Geometry

This document provides utilities for working with source traceability and bounding box coordinates. For the `sourceMetadata` schema definition, see [OpenAPI spec](https://api.demo.understorytech.com/docs) → `#/components/schemas/sourceMetadata`.

## Source Meta Overview

Every cell with a source PDF location includes a `sourceMeta` object with:
- `fileId` - Source file UUID
- `pageId` - Page UUID
- `tableId` - Table identifier
- `pageNumber` - 1-based page number
- `rowIndex`, `columnIndex` - Position in source table
- `boundingBox` - Visual coordinates

## Bounding Box Coordinate System

Bounding boxes use **ratio coordinates** (0.0 to 1.0) relative to page dimensions, not pixels.

```json
{
  "boundingBox": {
    "top": 0.172,     // 17.2% from top of page
    "left": 0.826,    // 82.6% from left edge
    "width": 0.124,   // 12.4% of page width
    "height": 0.014   // 1.4% of page height
  }
}
```

## Converting to Pixel Coordinates

```python
def bbox_to_pixels(bbox: dict, page_width: int, page_height: int) -> dict:
    """
    Convert bounding box ratios to pixel coordinates.

    Args:
        bbox: Bounding box with top, left, width, height ratios
        page_width: Page width in pixels
        page_height: Page height in pixels

    Returns:
        Dictionary with pixel coordinates
    """
    return {
        'x': int(bbox['left'] * page_width),
        'y': int(bbox['top'] * page_height),
        'width': int(bbox['width'] * page_width),
        'height': int(bbox['height'] * page_height),
        'x2': int((bbox['left'] + bbox['width']) * page_width),
        'y2': int((bbox['top'] + bbox['height']) * page_height)
    }


# Example: Standard letter-size PDF at 150 DPI
page_width = 1275   # 8.5 inches * 150 DPI
page_height = 1650  # 11 inches * 150 DPI

pixels = bbox_to_pixels(bbox, page_width, page_height)
```

## Drawing Highlights

### Python with PIL/Pillow

```python
from PIL import Image, ImageDraw

def highlight_cell(image_path: str, bbox: dict, output_path: str):
    """Draw a highlight rectangle on a PDF page image."""
    img = Image.open(image_path)
    page_width, page_height = img.size

    x = int(bbox['left'] * page_width)
    y = int(bbox['top'] * page_height)
    w = int(bbox['width'] * page_width)
    h = int(bbox['height'] * page_height)

    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + w, y + h], outline='red', width=2)
    img.save(output_path)
```

### JavaScript with Canvas

```javascript
function highlightCell(ctx, bbox, pageWidth, pageHeight) {
  const x = bbox.left * pageWidth;
  const y = bbox.top * pageHeight;
  const width = bbox.width * pageWidth;
  const height = bbox.height * pageHeight;

  ctx.strokeStyle = 'red';
  ctx.lineWidth = 2;
  ctx.strokeRect(x, y, width, height);
}
```

### CSS Positioning

For overlay elements:

```javascript
function getCellStyle(bbox) {
  return {
    position: 'absolute',
    left: `${bbox.left * 100}%`,
    top: `${bbox.top * 100}%`,
    width: `${bbox.width * 100}%`,
    height: `${bbox.height * 100}%`,
    border: '2px solid red',
    pointerEvents: 'none'
  };
}
```

## Building Source Links

The `link` field provides a relative path to the Understory UI:

```python
def build_source_url(source_meta: dict, company_id: str, base_url: str) -> str:
    """Build a URL to view the source cell in Understory."""
    return (
        f"{base_url}/company/{company_id}"
        f"/files/{source_meta['fileId']}"
        f"?page={source_meta['pageNumber']}"
        f"&table={source_meta['tableId']}"
    )
```

## Collecting All Source Locations

```python
def get_all_source_locations(model: dict) -> list:
    """Extract all source locations from a model."""
    locations = []

    for table_group in model.get('tableGroups', []):
        for table in table_group.get('tables', []):
            for section in table.get('sections', []):
                for item in section.get('data', []):
                    if item.get('type') != 'row':
                        continue

                    row_label = item.get('label', {}).get('text', '')

                    for cell in item.get('cells', []):
                        if cell.get('sourceMeta'):
                            locations.append({
                                'table': table.get('name'),
                                'category': table_group.get('category'),
                                'row_label': row_label,
                                'column_key': cell.get('columnKey'),
                                'source_meta': cell['sourceMeta']
                            })

    return locations
```

## FileModel API for Detailed Geometry

For more detailed geometry (word positions, cell polygons), use the FileModel API:

```
GET /companies/{companyId}/files/{fileId}/fileModel
```

FileModel cells may include `polygon` arrays for irregular shapes (also ratio coordinates 0.0-1.0).
