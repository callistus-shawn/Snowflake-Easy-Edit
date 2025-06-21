import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from backend import SnowflakeTableEditor

def render_ui():
    st.set_page_config(page_title="Snowflake Table Editor", layout="wide")
    st.title("Snowflake Table Editor")

    if 'editor' not in st.session_state:
        st.session_state.editor = SnowflakeTableEditor()
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    if 'current_table' not in st.session_state:
        st.session_state.current_table = None
    if 'table_data' not in st.session_state:
        st.session_state.table_data = pd.DataFrame()
    if 'edited_data' not in st.session_state:
        st.session_state.edited_data = pd.DataFrame()
    if 'selected_primary_key' not in st.session_state:
        st.session_state.selected_primary_key = None

    # Sidebar for connection
    with st.sidebar:
        st.header("Snowflake Connection")
        if not st.session_state.connected:
            with st.form("connection_form"):
                database = st.text_input("Database")
                schema = st.text_input("Schema")
                if st.form_submit_button("Connect"):
                    if all([database, schema]):
                        if st.session_state.editor.connect_to_snowflake(database, schema):
                            st.session_state.connected = True
                            st.success("Connected!")
                            st.rerun()
                    else:
                        st.error("Fill all fields to connect.")
        else:
            st.success("Connected to Snowflake")
            if st.button("Disconnect"):
                st.session_state.editor.close_connection()
                st.session_state.connected = False
                st.rerun()

    # Main Content
    if st.session_state.connected:
        col1, col2 = st.columns([1, 3])

        with col1:
            tables = st.session_state.editor.get_tables()
            if tables:
                selected_table = st.selectbox("Select Table", tables, index=tables.index(st.session_state.current_table) if st.session_state.current_table in tables else 0)
                if selected_table != st.session_state.current_table:
                    st.session_state.current_table = selected_table
                    df = st.session_state.editor.load_table_data(selected_table)
                    st.session_state.table_data = df
                    st.session_state.edited_data = df.copy()

                st.info(f"Rows: {len(st.session_state.table_data)}")

                # Select PK
                columns_info = st.session_state.editor.get_table_columns(selected_table)
                auto_pk = [col['name'] for col in columns_info if col.get('primary_key')]
                default_pk = auto_pk[0] if auto_pk else st.session_state.table_data.columns[0]

                selected_pk = st.selectbox("Select Primary Key", st.session_state.table_data.columns, index=st.session_state.table_data.columns.get_loc(default_pk))
                st.session_state.selected_primary_key = selected_pk

                if st.session_state.table_data[selected_pk].nunique() == len(st.session_state.table_data):
                    st.success("Primary key column is valid.")
                else:
                    st.warning("Selected column is not unique!")

        with col2:
            if not st.session_state.table_data.empty:
                gb = GridOptionsBuilder.from_dataframe(st.session_state.edited_data)
                gb.configure_default_column(editable=True)
                gb.configure_selection("single")
                grid_options = gb.build()

                grid_response = AgGrid(
                    st.session_state.edited_data,
                    gridOptions=grid_options,
                    update_mode=GridUpdateMode.VALUE_CHANGED,
                    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                    height=500,
                    fit_columns_on_grid_load=True
                )
                st.session_state.edited_data = grid_response.data.copy()

                if st.button("Apply Updates"):
                    pk_col = st.session_state.selected_primary_key
                    original = st.session_state.table_data
                    edited = st.session_state.edited_data

                    changes_made = False
                    for idx in range(len(edited)):
                        orig_row = original.iloc[idx]
                        edit_row = edited.iloc[idx]
                        pk_value = orig_row[pk_col]

                        for col in edited.columns:
                            if col == pk_col:
                                continue
                            if str(orig_row[col]) != str(edit_row[col]):
                                success = st.session_state.editor.update_record(
                                    st.session_state.current_table,
                                    pk_col,
                                    pk_value,
                                    col,
                                    edit_row[col]
                                )
                                if success:
                                    st.success(f"Updated row {idx+1}: {col} -> {edit_row[col]}")
                                    changes_made = True
                                else:
                                    st.error(f"Failed to update {col} for {pk_col}={pk_value}")
                    if changes_made:
                        st.success("All changes applied successfully.")
                        st.session_state.table_data = st.session_state.edited_data.copy()
            else:
                st.warning("No data to display.")
    else:
        st.info("Connect to Snowflake to begin.")
