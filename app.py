import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).with_name("inventory.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0,
                supplier_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
            """
        )
        columns = [row["name"]
                   for row in conn.execute("PRAGMA table_info(items)")]
        if "supplier_id" not in columns:
            conn.execute("ALTER TABLE items ADD COLUMN supplier_id INTEGER")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_items_supplier_id ON items(supplier_id)"
        )
        conn.commit()
    finally:
        conn.close()


def query_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def query_one(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def insert_item(name, category, quantity, price, supplier_id):
    now = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO items (
            name, category, quantity, price, supplier_id, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, category, quantity, price, supplier_id, now, now),
    )


def update_item(item_id, name, category, quantity, price, supplier_id):
    now = datetime.now(timezone.utc).isoformat()
    execute(
        """
        UPDATE items
        SET name = ?, category = ?, quantity = ?, price = ?, supplier_id = ?, updated_at = ?
        WHERE id = ?
        """,
        (name, category, quantity, price, supplier_id, now, item_id),
    )


def delete_item(item_id):
    execute("DELETE FROM items WHERE id = ?", (item_id,))


def insert_supplier(name, city):
    now = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO suppliers (name, city, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (name, city, now, now),
    )


def supplier_in_use(supplier_id):
    row = query_one(
        "SELECT COUNT(*) AS usage_count FROM items WHERE supplier_id = ?",
        (supplier_id,),
    )
    return row["usage_count"] > 0


def delete_supplier(supplier_id):
    if supplier_in_use(supplier_id):
        return False
    execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
    return True


def fetch_suppliers():
    return query_all("SELECT id, name, city FROM suppliers ORDER BY name ASC")


def fetch_supplier_cities():
    rows = query_all(
        "SELECT DISTINCT city FROM suppliers WHERE city IS NOT NULL AND city != ''"
    )
    return [row["city"] for row in rows]


def fetch_items(search_text, category):
    sql = (
        "SELECT items.*, suppliers.name AS supplier_name, "
        "suppliers.city AS supplier_city "
        "FROM items LEFT JOIN suppliers ON items.supplier_id = suppliers.id"
    )
    params = []
    filters = []

    if search_text:
        filters.append("items.name LIKE ?")
        params.append(f"%{search_text}%")

    if category and category != "All":
        filters.append("items.category = ?")
        params.append(category)

    if filters:
        sql += " WHERE " + " AND ".join(filters)

    sql += " ORDER BY items.name ASC"
    return query_all(sql, params)


def fetch_categories():
    rows = query_all(
        "SELECT DISTINCT category FROM items WHERE category IS NOT NULL AND category != ''"
    )
    return [row["category"] for row in rows]


def fetch_totals():
    row = query_one(
        "SELECT COUNT(*) AS item_count, COALESCE(SUM(quantity), 0) AS total_qty, "
        "COALESCE(SUM(quantity * price), 0) AS total_value FROM items"
    )
    return row


def fetch_category_summary(min_total_value, min_item_count):
    sql = """
        SELECT
            COALESCE(NULLIF(category, ''), 'Uncategorized') AS category_label,
            COUNT(*) AS item_count,
            COALESCE(SUM(quantity), 0) AS total_qty,
            COALESCE(SUM(quantity * price), 0) AS total_value,
            COALESCE(AVG(price), 0) AS avg_price
        FROM items
        GROUP BY COALESCE(NULLIF(category, ''), 'Uncategorized')
        HAVING COALESCE(SUM(quantity * price), 0) >= ? AND COUNT(*) >= ?
        ORDER BY total_value DESC, category_label ASC
    """
    return query_all(sql, (min_total_value, min_item_count))


def fetch_supplier_summary(min_total_value, min_item_count):
    sql = """
        SELECT
            suppliers.name AS supplier_name,
            suppliers.city AS supplier_city,
            COUNT(items.id) AS item_count,
            COALESCE(SUM(items.quantity), 0) AS total_qty,
            COALESCE(SUM(items.quantity * items.price), 0) AS total_value
        FROM suppliers
        LEFT JOIN items ON items.supplier_id = suppliers.id
        GROUP BY suppliers.id, suppliers.name, suppliers.city
        HAVING COALESCE(SUM(items.quantity * items.price), 0) >= ?
            AND COUNT(items.id) >= ?
        ORDER BY total_value DESC, supplier_name ASC
    """
    return query_all(sql, (min_total_value, min_item_count))


def fetch_join_results(join_type, city_filter):
    join_type = join_type.upper()
    if join_type not in {"INNER", "LEFT"}:
        join_type = "LEFT"

    params = []
    if join_type == "LEFT" and city_filter:
        on_clause = "items.supplier_id = suppliers.id AND suppliers.city = ?"
        params.append(city_filter)
        where_clause = ""
    else:
        on_clause = "items.supplier_id = suppliers.id"
        if city_filter:
            where_clause = " WHERE suppliers.city = ?"
            params.append(city_filter)
        else:
            where_clause = ""

    sql = (
        "SELECT items.id, items.name, items.category, items.quantity, items.price, "
        "suppliers.name AS supplier_name, suppliers.city AS supplier_city "
        f"FROM items {join_type} JOIN suppliers ON {on_clause}{where_clause} "
        "ORDER BY items.name ASC"
    )
    return query_all(sql, params)


def format_item_label(item):
    return f"{item['name']} (ID: {item['id']})"


def render_view():
    st.subheader("Inventory")

    col1, col2 = st.columns([2, 1])
    with col1:
        search_text = st.text_input("Search by name")
    with col2:
        categories = ["All"] + fetch_categories()
        category = st.selectbox("Category", categories)

    items = fetch_items(search_text.strip(), category)
    totals = fetch_totals()

    metric_cols = st.columns(3)
    metric_cols[0].metric("Items", totals["item_count"])
    metric_cols[1].metric("Total Quantity", totals["total_qty"])
    metric_cols[2].metric("Inventory Value", f"{totals['total_value']:.2f}")

    st.divider()

    if items:
        display_items = []
        for item in items:
            display_items.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "category": item["category"] or "Uncategorized",
                    "quantity": item["quantity"],
                    "price": item["price"],
                    "supplier": item["supplier_name"] or "Unassigned",
                }
            )
        st.dataframe(display_items, width="stretch")
    else:
        st.info("No items match your filters.")


def render_add():
    st.subheader("Add Item")

    supplier_labels, supplier_ids = build_supplier_options()

    with st.form("add_item"):
        name = st.text_input("Item name")
        category = st.text_input("Category")
        supplier_label = st.selectbox("Supplier", supplier_labels)
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price", min_value=0.0,
                                step=0.01, format="%.2f")
        submitted = st.form_submit_button("Add")

    if submitted:
        if not name.strip():
            st.error("Item name is required.")
            return
        supplier_id = supplier_ids[supplier_labels.index(supplier_label)]
        insert_item(name.strip(), category.strip(),
                    int(quantity), float(price), supplier_id)
        st.success("Item added.")


def render_update():
    st.subheader("Update Item")

    items = fetch_items("", "All")
    if not items:
        st.info("Add an item before updating.")
        return

    item_lookup = {format_item_label(item): item for item in items}
    selected_label = st.selectbox("Select item", list(item_lookup.keys()))
    selected_item = item_lookup[selected_label]

    supplier_labels, supplier_ids = build_supplier_options()
    current_supplier_id = selected_item.get("supplier_id")
    supplier_index = 0
    if current_supplier_id in supplier_ids:
        supplier_index = supplier_ids.index(current_supplier_id)

    with st.form("update_item"):
        name = st.text_input("Item name", value=selected_item["name"])
        category = st.text_input(
            "Category", value=selected_item["category"] or "")
        supplier_label = st.selectbox(
            "Supplier", supplier_labels, index=supplier_index)
        quantity = st.number_input(
            "Quantity", min_value=0, step=1, value=int(selected_item["quantity"])
        )
        price = st.number_input(
            "Price",
            min_value=0.0,
            step=0.01,
            value=float(selected_item["price"]),
            format="%.2f",
        )
        submitted = st.form_submit_button("Update")

    if submitted:
        if not name.strip():
            st.error("Item name is required.")
            return
        supplier_id = supplier_ids[supplier_labels.index(supplier_label)]
        update_item(
            selected_item["id"],
            name.strip(),
            category.strip(),
            int(quantity),
            float(price),
            supplier_id,
        )
        st.success("Item updated.")


def render_delete():
    st.subheader("Delete Item")

    items = fetch_items("", "All")
    if not items:
        st.info("Add an item before deleting.")
        return

    item_lookup = {format_item_label(item): item for item in items}
    selected_label = st.selectbox("Select item", list(item_lookup.keys()))
    selected_item = item_lookup[selected_label]

    confirm = st.checkbox("I understand this cannot be undone")
    if st.button("Delete"):
        if not confirm:
            st.error("Please confirm the deletion.")
            return
        delete_item(selected_item["id"])
        st.success("Item deleted.")


def build_supplier_options():
    suppliers = fetch_suppliers()
    labels = ["Unassigned"]
    ids = [None]
    for supplier in suppliers:
        labels.append(f"{supplier['name']} (ID: {supplier['id']})")
        ids.append(supplier["id"])
    return labels, ids


def render_suppliers():
    st.subheader("Suppliers")

    with st.form("add_supplier"):
        name = st.text_input("Supplier name")
        city = st.text_input("City")
        submitted = st.form_submit_button("Add supplier")

    if submitted:
        if not name.strip():
            st.error("Supplier name is required.")
            return
        insert_supplier(name.strip(), city.strip())
        st.success("Supplier added.")

    suppliers = fetch_suppliers()
    if suppliers:
        st.dataframe(suppliers, width="stretch")
    else:
        st.info("No suppliers yet. Add one to link items.")

    if not suppliers:
        return

    st.divider()
    st.markdown("Remove Supplier")
    supplier_lookup = {
        f"{supplier['name']} (ID: {supplier['id']})": supplier["id"]
        for supplier in suppliers
    }
    selected_label = st.selectbox(
        "Select supplier", list(supplier_lookup.keys()))
    confirm = st.checkbox(
        "I understand this cannot be undone", key="confirm_supplier_delete"
    )
    if st.button("Delete supplier"):
        if not confirm:
            st.error("Please confirm the deletion.")
            return
        deleted = delete_supplier(supplier_lookup[selected_label])
        if not deleted:
            st.error("Cannot delete: supplier is linked to items.")
            return
        st.success("Supplier deleted.")


def render_reports():
    st.subheader("Aggregations")
    st.caption("Summaries using GROUP BY and HAVING clauses.")

    st.markdown("Category Summary")
    col1, col2 = st.columns(2)
    with col1:
        min_value = st.number_input(
            "Min total value (HAVING)", min_value=0.0, step=1.0, value=0.0
        )
    with col2:
        min_count = st.number_input(
            "Min item count (HAVING)", min_value=0, step=1, value=0
        )

    category_summary = fetch_category_summary(min_value, min_count)
    if category_summary:
        st.dataframe(category_summary, width="stretch")
    else:
        st.info("No categories meet the HAVING conditions.")

    st.divider()
    st.markdown("Supplier Summary (JOIN + GROUP BY)")
    col3, col4 = st.columns(2)
    with col3:
        min_value_suppliers = st.number_input(
            "Min total value (HAVING)",
            min_value=0.0,
            step=1.0,
            value=0.0,
            key="supplier_min_value",
        )
    with col4:
        min_count_suppliers = st.number_input(
            "Min item count (HAVING)",
            min_value=0,
            step=1,
            value=0,
            key="supplier_min_count",
        )

    supplier_summary = fetch_supplier_summary(
        min_value_suppliers, min_count_suppliers
    )
    if supplier_summary:
        st.dataframe(supplier_summary, width="stretch")
    else:
        st.info("No suppliers meet the HAVING conditions.")


def render_joins():
    st.subheader("Join Operations")
    st.caption("Compare INNER JOIN and LEFT JOIN results.")

    join_label = st.selectbox("Join type", ["INNER JOIN", "LEFT JOIN"])
    join_type = "INNER" if join_label.startswith("INNER") else "LEFT"

    cities = ["All"] + fetch_supplier_cities()
    selected_city = st.selectbox("Supplier city (optional)", cities)
    city_filter = None if selected_city == "All" else selected_city

    rows = fetch_join_results(join_type, city_filter)
    if rows:
        st.dataframe(rows, width="stretch")
    else:
        st.info("No rows match the selected join and filter.")


def main():
    st.set_page_config(page_title="Inventory Manager", layout="wide")
    st.title("Inventory Management System")

    init_db()

    page = st.sidebar.radio(
        "Navigation",
        options=["View", "Add", "Update", "Delete",
                 "Suppliers", "Reports", "Joins"],
        index=0,
    )

    st.sidebar.subheader("Project Contributers")
    st.sidebar.markdown(
        "- Namarata Gilbile (A-50)\n"
        "- Divya Giri (A-38)\n"
        "- Yashodeep Hundiwale (A-55)"
    )

    if page == "View":
        render_view()
    elif page == "Add":
        render_add()
    elif page == "Update":
        render_update()
    elif page == "Delete":
        render_delete()
    elif page == "Suppliers":
        render_suppliers()
    elif page == "Reports":
        render_reports()
    else:
        render_joins()


if __name__ == "__main__":
    main()
