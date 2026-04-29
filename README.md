# 📦 Inventory Management System

A complete **Inventory Management System** built using **Python, SQLite, and Streamlit**.
This project not only performs CRUD operations but also demonstrates **real DBMS concepts like Joins, Subqueries, Aggregations, and Triggers**.

---

# 🚀 What This Project Does (Simple Understanding)

👉 This system helps you:

* Store product data (items)
* Manage suppliers
* Track stock quantity and price
* Calculate total inventory value
* Generate reports
* Suggest restocking automatically

---

# ⚙️ How The Project Works (Step-by-Step)

## 🧠 Step 1: App Starts

* `main()` function runs
* `init_db()` is called
* Database (`inventory.db`) is created automatically

---

## 🗄️ Step 2: Database Creation

Three tables are created:

### 📄 1. Suppliers Table

Stores supplier details

```sql
id, name, city
```

### 📄 2. Items Table

Stores product details

```sql
id, name, category, quantity, price, supplier_id
```

👉 `supplier_id` links item → supplier (**Foreign Key**)

### 📄 3. Restock Requests Table

Stores low-stock alerts

```sql
item_id, current_qty, target_qty, suggested_qty
```

---

## 🔒 Step 3: Data Safety (Triggers)

Automatic rules are applied:

* ❌ Quantity < 0 → Not allowed
* ❌ Price < 0 → Not allowed
* ❌ Empty supplier name → Not allowed
* ❌ Cannot delete supplier if items exist

👉 These rules run automatically inside the database.

---

## 🔌 Step 4: Database Connection

```python
get_connection()
```

👉 Connects Python with SQLite database.

---

## 🔄 Step 5: CRUD Operations

### ➕ Add Item

```python
insert_item()
```

### 👀 View Items

```python
fetch_items()
```

### ✏️ Update Item

```python
update_item()
```

### ❌ Delete Item

```python
delete_item()
```

👉 These are basic **Create, Read, Update, Delete** operations.

---

# 🖥️ UI Explanation (Page by Page)

---

## 👀 1. View Page (Dashboard)

👉 Shows:

* Total Items
* Total Quantity
* Total Inventory Value

### 🧮 Calculation

```
Total Value = quantity × price
```

### 📋 Table Displays

* Item name
* Category
* Quantity
* Price
* Supplier

👉 Uses:

```sql
LEFT JOIN (items + suppliers)
```

---

## ➕ 2. Add Page

👉 User enters:

* Item name
* Category
* Supplier
* Quantity
* Price

👉 Data is inserted into database.

---

## ✏️ 3. Update Page

👉 Select item → edit details → save

👉 Updates database using:

```sql
UPDATE items SET ...
```

---

## ❌ 4. Delete Page

👉 Select item → confirm → delete

👉 Uses:

```sql
DELETE FROM items
```

---

## 👨‍💼 5. Suppliers Page

👉 Add new supplier
👉 View all suppliers
👉 Delete supplier (only if not linked to items)

---

# 📊 Advanced SQL Features

---

## 📈 6. Reports (Aggregation)

### 🔹 Category Summary

* Total items per category
* Total quantity
* Total value
* Average price

### 🔹 Supplier Summary

* Items per supplier
* Total stock value

👉 Uses:

```sql
GROUP BY + HAVING
```

---

## 🔗 7. Joins

### INNER JOIN

👉 Shows only matching data

### LEFT JOIN

👉 Shows all items (even without supplier)

---

## 🔍 8. Subqueries

### Example 1

👉 Get items from suppliers in a specific city

### Example 2

👉 Get items priced above category average

👉 Uses:

```sql
SELECT inside SELECT (nested query)
```

---

## 🤖 9. Restock System (Procedure)

👉 Checks low stock items

### How it works

1. Find items where quantity < minimum
2. Calculate required stock
3. Save suggestion

### 🧮 Formula

```
suggested_qty = target_qty - current_qty
```

---

## 📁 Project Structure

```
inventory-management/
│
├── app.py              # Main application
├── inventory.db        # Database (auto-created)
└── README.md
```

---

## 🛠️ Tech Stack

* Python
* SQLite
* Streamlit

---

## ⚙️ Setup Instructions

### 1. Install dependencies

```
pip install streamlit
```

### 2. Run the app

```
streamlit run app.py
```

---

## 💡 Example Flow

1. Add supplier
2. Add item (linked to supplier)
3. View inventory
4. Update or delete item
5. Generate reports
6. Run restock system

---

## 🎯 What You Learn From This Project

* CRUD operations
* SQL queries
* Joins (INNER, LEFT)
* Subqueries
* Aggregations (GROUP BY)
* Data integrity (Triggers)
* Real-world database design

---

## 👨‍💻 Contributors

* Namarata Gilbile (A-50)
* Divya Giri (A-38)
* Yashodeep Hundiwale (A-55)

---

## ⭐ Final Summary

👉 This is a complete **DBMS-based real-world project** that manages inventory, suppliers, and stock efficiently while demonstrating advanced SQL concepts.

---

⭐ *Perfect for college projects, viva, and resume!*
