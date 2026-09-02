import streamlit as st
import json
import os

st.set_page_config(page_title="Utility Tools Portal", layout="wide")

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

st.title("🛠️ Utility Tools Dashboard")
st.write("Access all internal utility tools in one place.")

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
        st.rerun()

    st.sidebar.subheader("➕ Add New Tool Link")

    with st.sidebar.form("add_tool_form", clear_on_submit=True):
        tool_name = st.text_input("Tool Name:")
        tool_url = st.text_input("Tool URL:")
        tool_desc = st.text_area("Description (What this tool does):")
        
        submit_button = st.form_submit_button("Add to Dashboard")

        if submit_button:
            if tool_name and tool_url:
                new_tool = {
                    "name": tool_name,
                    "url": tool_url,
                    "desc": tool_desc if tool_desc else "No description provided."
                }
                st.session_state.tools_list.append(new_tool)
                save_tools(st.session_state.tools_list)
                st.sidebar.success(f"'{tool_name}' added to dashboard!")
                st.rerun()
            else:
                st.sidebar.error("Please fill in both Name and URL fields!")

# --- MAIN DASHBOARD DISPLAY ---
st.divider()

if not st.session_state.tools_list:
    st.info("No tools added yet. Log in via the sidebar to add new links.")
else:
    cols = st.columns(2)
    for index, tool in enumerate(st.session_state.tools_list):
        col = cols[index % 2]
        with col:
            with st.container(border=True):
                st.subheader(f"📌 {tool['name']}")
                st.write(f"**Description:** {tool['desc']}")
                st.link_button(f"Open {tool['name']} 🚀", tool['url'])
