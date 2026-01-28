# Source Meta and Geometry

This document explains how to trace CompanyModel cells back to their source PDF locations using `sourceMeta` and bounding box coordinates.

## Source Meta Structure

Every cell with a source PDF location includes a `sourceMeta` object:

```json
{
  "sourceMeta": {
    "fileId": "02d399ee-aa37-4aca-b3a5-ee8cf057228a",
    "pageId": "cfa0039a-9716-4590-b9b8-52e8c452d8d9",
    "tableId": "zihiurdn",
    "pageNumber": 80,
    "rowIndex": 3,
    "columnIndex": 4,
    "boundingBox": {
      "top": 0.1720634251832962,
      "left": 0.8256401419639587,
      "width": 0.12356248497962952,
      "height": 0.014005137607455254
    }
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `fileId` | UUID | Source file identifier (use with Files API) |
| `pageId` | UUID | Specific page identifier |
| `tableId` | string | Table identifier within the page |
| `pageNumber` | number | 1-based page number |
| `rowIndex` | number | 0-based row index within the table |
| `columnIndex` | number | 0-based column index within the table |
| `boundingBox` | object | Visual coordinates on the page |

---

## Bounding Box Coordinate System

Bounding boxes use **ratio coordinates** relative to page dimensions, not pixels.

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

### Coordinate Ranges

All values are ratios between 0.0 and 1.0:

| Field | Range | Description |
|-------|-------|-------------|
| `top` | 0.0 - 1.0 | Distance from top edge (0 = top, 1 = bottom) |
| `left` | 0.0 - 1.0 | Distance from left edge (0 = left, 1 = right) |
| `width` | 0.0 - 1.0 | Width as fraction of page width |
| `height` | 0.0 - 1.0 | Height as fraction of page height |

### Converting to Pixel Coordinates

To convert ratios to pixel coordinates, multiply by page dimensions:

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


# Example usage
bbox = {
    "top": 0.172,
    "left": 0.826,
    "width": 0.124,
    "height": 0.014
}

# Standard letter-size PDF at 150 DPI
page_width = 1275   # 8.5 inches * 150 DPI
page_height = 1650  # 11 inches * 150 DPI

pixels = bbox_to_pixels(bbox, page_width, page_height)
# {
#   'x': 1053,
#   'y': 283,
#   'width': 158,
#   'height': 23,
#   'x2': 1211,
#   'y2': 306
# }
```

---

## Drawing Highlights

### Python with PIL/Pillow

```python
from PIL import Image, ImageDraw

def highlight_cell(image_path: str, bbox: dict, output_path: str):
    """Draw a highlight rectangle on a PDF page image."""
    img = Image.open(image_path)
    page_width, page_height = img.size

    # Convert to pixels
    x = int(bbox['left'] * page_width)
    y = int(bbox['top'] * page_height)
    w = int(bbox['width'] * page_width)
    h = int(bbox['height'] * page_height)

    # Draw rectangle
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        [x, y, x + w, y + h],
        outline='red',
        width=2
    )

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
function getCellStyle(bbox, containerWidth, containerHeight) {
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

---

## Accessing Detailed Geometry via FileModel API

For more detailed geometry data (individual word positions, cell polygons), use the FileModel API.

### API Endpoint

```
GET /companies/{companyId}/files/{fileId}/fileModel
```

### FileModel Structure

```json
{
  "fileModelId": "string",
  "fileId": "uuid",
  "pages": [
    {
      "pageId": "uuid",
      "pageNumber": 1,
      "tables": [
        {
          "tableId": "string",
          "boundingBox": {...},
          "rows": [
            {
              "rowIndex": 0,
              "cells": [
                {
                  "columnIndex": 0,
                  "boundingBox": {...},
                  "polygon": [
                    {"x": 0.1, "y": 0.2},
                    {"x": 0.3, "y": 0.2},
                    {"x": 0.3, "y": 0.25},
                    {"x": 0.1, "y": 0.25}
                  ],
                  "words": [
                    {
                      "text": "$918,688",
                      "boundingBox": {...},
                      "confidence": 99.5
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Polygon Coordinates

FileModel cells may include `polygon` arrays for irregular shapes:

```json
{
  "polygon": [
    {"x": 0.1, "y": 0.2},
    {"x": 0.3, "y": 0.2},
    {"x": 0.3, "y": 0.25},
    {"x": 0.1, "y": 0.25}
  ]
}
```

Polygons are also ratio coordinates (0.0 to 1.0).

---

## Building Source Links

### Understory UI Link

The `link` field provides a relative path:

```json
{
  "link": "company/05017094-d232-4162-8d97-8be6326db968/files/02d399ee-aa37-4aca-b3a5-ee8cf057228a?page=80&table=zihiurdn"
}
```

Construct full URL:
```python
base_url = "https://yourcompany.understorytech.com"
full_url = f"{base_url}/{cell['link']}"
```

### Building from sourceMeta

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

---

## Collecting All Source Locations

```python
def get_all_source_locations(model: dict) -> list:
    """
    Extract all source locations from a model.

    Returns:
        List of dicts with row info and sourceMeta
    """
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
