import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).with_name("inventory.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)")
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


def insert_item(name, category, quantity, price):
    now = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO items (name, category, quantity, price, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, category, quantity, price, now, now),
    )


def update_item(item_id, name, category, quantity, price):
    now = datetime.now(timezone.utc).isoformat()
    execute(
        """
        UPDATE items
        SET name = ?, category = ?, quantity = ?, price = ?, updated_at = ?
        WHERE id = ?
        """,
        (name, category, quantity, price, now, item_id),
    )


def delete_item(item_id):
    execute("DELETE FROM items WHERE id = ?", (item_id,))


def fetch_items(search_text, category):
    sql = "SELECT * FROM items"
    params = []
    filters = []

    if search_text:
        filters.append("name LIKE ?")
        params.append(f"%{search_text}%")

    if category and category != "All":
        filters.append("category = ?")
        params.append(category)

    if filters:
        sql += " WHERE " + " AND ".join(filters)

    sql += " ORDER BY name ASC"
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
        st.dataframe(items, width="stretch")
    else:
        st.info("No items match your filters.")


def render_add():
    st.subheader("Add Item")

    with st.form("add_item"):
        name = st.text_input("Item name")
        category = st.text_input("Category")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        price = st.number_input("Price", min_value=0.0,
                                step=0.01, format="%.2f")
        submitted = st.form_submit_button("Add")

    if submitted:
        if not name.strip():
            st.error("Item name is required.")
            return
        insert_item(name.strip(), category.strip(),
                    int(quantity), float(price))
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

    with st.form("update_item"):
        name = st.text_input("Item name", value=selected_item["name"])
        category = st.text_input(
            "Category", value=selected_item["category"] or "")
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
        update_item(
            selected_item["id"],
            name.strip(),
            category.strip(),
            int(quantity),
            float(price),
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


def main():
    st.set_page_config(page_title="Inventory Manager", layout="wide")
    st.title("Inventory Management System")

    init_db()

    page = st.sidebar.radio(
        "Navigation",
        options=["View", "Add", "Update", "Delete"],
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
    else:
        render_delete()


if __name__ == "__main__":
    main()
