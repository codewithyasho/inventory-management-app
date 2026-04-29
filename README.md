# Inventory Manager (Streamlit + SQLite)

A simple inventory management app built with Streamlit and SQLite. It lets you add, view, update, and delete inventory items, plus filter by name and category.

## Features

- Add, update, delete inventory items
- Manage suppliers and link items to suppliers
- Search by item name
- Filter by category
- Automatic totals (items, quantity, value)
- Aggregation reports using GROUP BY and HAVING
- Join reports (INNER JOIN and LEFT JOIN)
- Local SQLite database stored alongside the app

## Tech Stack

- Python
- Streamlit
- SQLite (built in)

## Project Structure

- app.py: Streamlit application
- requirements.txt: Python dependencies
- inventory.db: SQLite database (auto-created on first run)

## Setup

1. Create and activate a virtual environment.
   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1
   - macOS/Linux:
     - python3 -m venv .venv
     - source .venv/bin/activate
2. Install dependencies:
   - pip install -r requirements.txt

## Run

- streamlit run app.py

The app will open in your browser. The database file (inventory.db) is created automatically next to app.py.

## Notes

- All timestamps are stored in UTC ISO 8601 format.
- Categories are optional; only non-empty categories appear in the filter list.

## Troubleshooting

- If Streamlit is not found, ensure your virtual environment is active and dependencies are installed.
- If the app cannot write the database, check folder permissions.
