# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jupyter notebook project for exploring and testing the Understory API, which handles document processing and financial model generation services. The main entry point is `api-test.ipynb`.

## Setup Commands

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
cp .env.copy .env
# Then edit .env to add API_KEY and DOMAIN
```

## Required Environment Variables

- `API_KEY` - Understory API key
- `DOMAIN` - API domain (e.g., `api.yourcompanydomain.understorytech.com`)

## Key Concepts

- **Model (CompanyModel)** - The stitched/joined financial model generated from multiple files
- **FileModel** - Extracted data from a single uploaded file, including geometry data for tables and cells
- **boundingBox** - Coordinates as ratios of page dimensions (e.g., `top: 0.10` means 10% from top)
- **polygon** - Array of X/Y coordinates for complex shapes

## API Workflow

1. **Create a company** - `POST /companies`
2. **Create file entries** - `POST /companies/{companyId}/files` (returns `uploadUrl`)
3. **Upload files** - PUT to the signed `uploadUrl` (15-minute expiration)
4. **Wait for file processing** - Files must reach `parsing_completed` status
5. **Generate model** - `POST /companies/{companyId}/models` with `includedFileIds`
6. **Poll for completion** - `GET /companies/{companyId}/models/{modelId}` until `status: completed`
7. **Download model** - `POST /companies/{companyId}/models/{modelId}/download`

## Status Values

**File statuses:** created, uploaded, pending, empty, importing_started, importing_completed, textract_started, textract_completed, textract_disabled, parsing_started, parsing_completed, failed

**Model statuses:** created, preparing, running, joining, organizing, summarizing, printing, completed, failed

## Authentication

All API requests require `x-api-key` header with the API key.

## Notes

- Model generation can take 2-40 minutes depending on input size
- Use `version: "2.0.0"` in download request to include summary sheets
- FileModel bounding boxes are ratios relative to PDF page dimensions
- Sample PDFs are included in `pdfs/` directory for testing
