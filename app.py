import streamlit as st
import json
import os

st.set_page_config(page_title="Utility Tools Portal", layout="wide")

# Custom CSS to reduce top padding and space
st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
        .custom-title {
            font-size: 20px !important;
            font-weight: 600;
            margin-bottom: 2px;
        }
        .custom-sub {
            font-size: 13px !important;
            color: #888;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Static Credentials
VALID_USER_ID = "VMPL"
VALID_PASSWORD = "VMPL@123"

DATA_FILE = "tools_data.json"

# Function to load stored tools from JSON file
def load_tools():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# Function to save tools to JSON file
def save_tools(tools):
    with open(DATA_FILE, "w") as f:
        json.dump(tools, f, indent=4)

# Initialize Session State
if "tools_list" not in st.session_state:
    st.session_state.tools_list = load_tools()

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

# Compact & Low-Space Header
st.markdown('<div class="custom-title">🛠️ Utility Tools Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-sub">Access all internal utility tools in one place.</div>', unsafe_allow_html=True)
st.divider()

# --- SIDEBAR: Login & Admin Controls ---
st.sidebar.header("🔒 Admin Panel")

if not st.session_state.is_logged_in:
    user_id_input = st.sidebar.text_input("User ID")
    password_input = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if user_id_input == VALID_USER_ID and password_input == VALID_PASSWORD:
            st.session_state.is_logged_in = True
            st.sidebar.success("Logged in successfully!")
            st.rerun()
        else:
            st.sidebar.error("Invalid User ID or Password!")
else:
    st.sidebar.success(f"Welcome, {VALID_USER_ID}!")
    if st.sidebar.button("Logout"):
        st.session_state.is_logged_in = False
        st.session_state.editing_index = None
        st.rerun()

    # --- ADD OR EDIT FORM ---
    if st.session_state.editing_index is not None:
        st.sidebar.subheader("✏️ Edit Tool")
        edit_idx = st.session_state.editing_index
        current_tool = st.session_state.tools_list[edit_idx]

        with st.sidebar.form("edit_tool_form"):
            tool_name = st.text_input("Tool Name:", value=current_tool["name"])
            tool_url = st.text_input("Tool URL:", value=current_tool["url"])
            
            update_button = st.form_submit_button("Update Tool")

            if update_button:
                if tool_name and tool_url:
                    st.session_state.tools_list[edit_idx] = {
                        "name": tool_name,
                        "url": tool_url
                    }
                    save_tools(st.session_state.tools_list)
                    st.session_state.editing_index = None
                    st.sidebar.success(f"'{tool_name}' updated successfully!")
                    st.rerun()
                else:
                    st.sidebar.error("Please fill in both Name and URL fields!")

        if st.sidebar.button("Cancel Edit"):
            st.session_state.editing_index = None
            st.rerun()

    else:
        st.sidebar.subheader("➕ Add New Tool Link")

        with st.sidebar.form("add_tool_form", clear_on_submit=True):
            tool_name = st.text_input("Tool Name:")
            tool_url = st.text_input("Tool URL:")
            
            submit_button = st.form_submit_button("Add to Dashboard")

            if submit_button:
                if tool_name and tool_url:
                    new_tool = {
                        "name": tool_name,
                        "url": tool_url
                    }
                    st.session_state.tools_list.append(new_tool)
                    save_tools(st.session_state.tools_list)
                    st.sidebar.success(f"'{tool_name}' added to dashboard!")
                    st.rerun()
                else:
                    st.sidebar.error("Please fill in both Name and URL fields!")

# --- MAIN DASHBOARD DISPLAY ---
if not st.session_state.tools_list:
    st.info("No tools added yet. Log in via the sidebar to add new links.")
else:
    cols = st.columns(2)
    for index, tool in enumerate(st.session_state.tools_list):
        col = cols[index % 2]
        with col:
            with st.container(border=True):
                st.subheader(f"📌 {tool['name']}")
                st.link_button(f"Open {tool['name']} 🚀", tool["url"])

                # Admin-only Edit & Delete Options
                if st.session_state.is_logged_in:
                    st.divider()
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        if st.button("✏️ Edit", key=f"edit_{index}"):
                            st.session_state.editing_index = index
                            st.rerun()
                            
                    with btn_col2:
                        if st.button("🗑️ Delete", key=f"del_{index}"):
                            st.session_state.tools_list.pop(index)
                            save_tools(st.session_state.tools_list)
                            if st.session_state.editing_index == index:
                                st.session_state.editing_index = None
                            st.rerun()
