# Understory API Playground

A Jupyter notebook for exploring and testing the Understory API. This project demonstrates how to interact with Understory's document processing and financial model generation services.

## Setup

1. Clone this repository
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy the environment template and add your credentials:
   ```bash
   cp .env.copy .env
   ```
4. Edit `.env` and add:
   - `API_KEY` - Your Understory API key
   - `DOMAIN` - Your API domain (e.g., `api.yourcompanydomain.understorytech.com`)

## Support

Feel free to reach out to us at support@understorytech.com if you encounter any issues

## Usage

Open `api-test.ipynb` in Jupyter or VSCode and run the cells to explore the API.

## Key Concepts

- **Model** - The stitched/joined financial model generated from multiple files
- **FileModel** - Extracted data from a single uploaded file, including geometry data for tables and cells
- **boundingBox** - Coordinates (as ratios of page dimensions) that locate objects within PDFs
