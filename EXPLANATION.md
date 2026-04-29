# Inventory Manager - Architecture and Working (Simple Explanation)

This document explains how the Inventory Manager app is built and how it works, in easy words.

## 1) What this app does (in one line)

It lets you add, view, update, and delete inventory items, and it stores everything in a local SQLite database.

## 2) Big-picture architecture

The app has three simple layers:

1) UI (Streamlit)

- Shows forms and tables in the browser.
- Collects user input and displays results.

1) Logic (Python functions in app.py)

- Validates input (like required name).
- Calls database functions to read or write data.

1) Database (SQLite file)

- A local file named inventory.db stored next to app.py.
- Holds a single table called items.

Simple flow:

User -> Streamlit UI -> Python logic -> SQLite database
         ^                                  |
         |----------------------------------|

## 3) Files and their roles

- app.py: The full Streamlit application and all DB functions.
- requirements.txt: Lists streamlit as the dependency.
- pyproject.toml: Project metadata and dependency list.
- inventory.db: SQLite database created automatically at first run.

## 4) Database design (items table)

When the app starts, it creates the items table if it does not exist.

Table: suppliers

- id: integer, auto-increment, primary key
- name: text, required
- city: text, optional
- created_at: text timestamp (UTC ISO format)
- updated_at: text timestamp (UTC ISO format)

Table: items

- id: integer, auto-increment, primary key
- name: text, required
- category: text, optional
- quantity: integer, default 0
- price: real number, default 0
- supplier_id: integer, optional (links to suppliers.id)
- created_at: text timestamp (UTC ISO format)
- updated_at: text timestamp (UTC ISO format)

Table: restock_requests

- id: integer, auto-increment, primary key
- item_id: integer, links to items.id
- item_name: text (snapshot of item name)
- current_qty: integer
- target_qty: integer
- suggested_qty: integer
- created_at: text timestamp (UTC ISO format)

Index:

- idx_items_name on name (faster name search)

Why this design is simple:

- One table is enough for basic inventory.
- Timestamps help track changes.

## 5) How the app works (step-by-step)

### A) App start

1) Streamlit runs app.py.
2) The app sets the page title and layout.
3) init_db() runs and creates the table if missing.
4) Sidebar shows the pages: View, Add, Update, Delete.

### B) View page

- Search box filters by name (uses SQL LIKE).
- Category dropdown filters by category.
- The table shows matching items, including supplier info.
- Three metrics are shown:
  - Total items count
  - Total quantity
  - Total inventory value (quantity * price)

### C) Add page

- A form collects: name, category, quantity, price.
- If name is empty, it shows an error.
- If valid, insert_item() adds a row.
- A success message appears.

### D) Update page

- User selects an item from a dropdown.
- A form shows the current values.
- On submit, update_item() updates the row and timestamp.

### E) Delete page

- User selects an item.
- Must tick a confirmation checkbox.
- On delete, delete_item() removes the row.

### F) Suppliers page

- Add suppliers (name, city).
- Shows all suppliers.
- Prevents deleting suppliers that are linked to items.

### G) Reports page

- Category summary using GROUP BY and HAVING.
- Supplier summary using JOIN + GROUP BY + HAVING.

### H) Joins page

- Compare INNER JOIN and LEFT JOIN results.
- Optional city filter shows join behavior with conditions.

### I) Procedures page

- Runs a restock procedure that uses a cursor to loop over low-stock items.
- Inserts rows into restock_requests to log suggested restocks.

### J) Subqueries page

- Items by supplier city using IN subqueries.
- Items priced above category average using a correlated subquery.

## 6) Important functions in app.py (simple words)

- get_connection(): Opens a SQLite connection.
- init_db(): Creates the items table and index if missing.
- query_all(): Runs a SELECT and returns all rows as dictionaries.
- query_one(): Runs a SELECT and returns one row.
- execute(): Runs INSERT/UPDATE/DELETE.
- insert_item(), update_item(), delete_item(): DB write helpers.
- insert_supplier(), delete_supplier(): Supplier write helpers.
- fetch_items(): Builds filters (search and category) and gets rows.
- fetch_categories(): Returns distinct categories for dropdown.
- fetch_totals(): Computes totals for the metrics row.
- fetch_category_summary(): GROUP BY + HAVING summary per category.
- fetch_supplier_summary(): JOIN + GROUP BY + HAVING summary per supplier.
- fetch_join_results(): INNER or LEFT JOIN output for the joins page.

## 7) Data flow example (adding an item)

1) User fills the Add form and clicks Add.
2) render_add() checks name is not empty.
3) insert_item() writes to SQLite.
4) Streamlit shows a success message.
5) The item appears in View page.

## 8) Why this is good for DBMS demo

- Shows a real database table with CRUD operations.
- Uses SQL queries and indexing.
- Shows how the UI connects to the database.
- Demonstrates filtering, aggregation with GROUP BY/HAVING, and joins.
- Demonstrates triggers that enforce data integrity rules.
- Demonstrates subqueries for cross-table filtering and analysis.
- Demonstrates a cursor-based procedure pattern for restocking.

## 9) Common questions (quick answers)

Q: Where is the data stored?
A: In inventory.db next to app.py.

Q: Does it need internet?
A: No. SQLite runs locally.

Q: What happens if I delete inventory.db?
A: A new empty database will be created on next run.

## 10) Short demo script (what to say)

1) "This app is a simple inventory manager built with Streamlit and SQLite."
2) "The UI lets us add, view, update, and delete items."
3) "All data is stored in a local SQLite database file."
4) "We can filter by name and category, and see totals like item count and value."
5) "This shows core DBMS concepts: tables, SQL queries, indexes, and CRUD."
