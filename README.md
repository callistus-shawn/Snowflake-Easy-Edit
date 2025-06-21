# Snowflake Table Editor (with Streamlit)
This is a web-based interactive tool built using Streamlit and AgGrid, allowing users to connect to a Snowflake database, view tables, edit data inline, and apply updates directly to the database.


<img src="Screenshot 2025-06-21 085904.png" heigth='800' width="800" />


### 🗂️ Project Files Description

#### 📁 `snowflake_editor_app/` – Streamlit-Based Snowflake Table Editor

| File                  | Description |
|-----------------------|-------------|
| `main.py`             | Entry point for starting the Streamlit app. Calls the UI render function from `frontend.py`. |
| `frontend.py`               | Handles all Streamlit UI layout: connection form, table selection, primary key configuration, editable grid display, and applying updates. |
| `backend.py` | Core Snowflake logic: handles database connection, table/column fetching, data loading, and executing update queries. |
