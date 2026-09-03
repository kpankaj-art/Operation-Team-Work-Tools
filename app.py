import streamlit as st
import json
import requests
import base64

st.set_page_config(page_title="Utility Tools Portal", layout="wide")

# Custom CSS for compact spacing
st.markdown("""
    <style>
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 0rem !important;
        }
        .custom-title {
            font-size: 22px !important;
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

# GitHub Secrets
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "") # Format: "username/repo_name"
FILE_PATH = "tools_data.json"

# Helper function to fetch tools directly from GitHub
def load_tools_from_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return []
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        file_content = base64.b64decode(content["content"]).decode("utf-8")
        try:
            return json.loads(file_content)
        except Exception:
            return []
    return []

# Helper function to save tools directly to GitHub Repository
def save_tools_to_github(tools_data, commit_message):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        st.error("GitHub Secrets missing! Please set GITHUB_TOKEN and GITHUB_REPO in Streamlit Cloud Secrets.")
        return False

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Get file SHA for update
    get_response = requests.get(url, headers=headers)
    sha = get_response.json().get("sha", "") if get_response.status_code == 200 else None

    # Prepare JSON payload
    updated_content = json.dumps(tools_data, indent=4)
    encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": commit_message,
        "content": encoded_content
    }
    if sha:
        payload["sha"] = sha

    put_response = requests.put(url, headers=headers, json=payload)
    return put_response.status_code in [200, 201]

# Initialize Session State
if "tools_list" not in st.session_state:
    st.session_state.tools_list = load_tools_from_github()

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
                    if save_tools_to_github(st.session_state.tools_list, f"Updated tool: {tool_name}"):
                        st.session_state.editing_index = None
                        st.sidebar.success(f"'{tool_name}' updated permanently!")
                        st.rerun()
                    else:
                        st.sidebar.error("Failed to save changes to GitHub!")
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
                    temp_list = st.session_state.tools_list.copy()
                    temp_list.append(new_tool)
                    
                    if save_tools_to_github(temp_list, f"Added tool: {tool_name}"):
                        st.session_state.tools_list = temp_list
                        st.sidebar.success(f"'{tool_name}' added permanently to dashboard!")
                        st.rerun()
                    else:
                        st.sidebar.error("Failed to save link to GitHub!")
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
                            deleted_name = st.session_state.tools_list[index]['name']
                            temp_list = st.session_state.tools_list.copy()
                            temp_list.pop(index)
                            
                            if save_tools_to_github(temp_list, f"Deleted tool: {deleted_name}"):
                                st.session_state.tools_list = temp_list
                                if st.session_state.editing_index == index:
                                    st.session_state.editing_index = None
                                st.rerun()
                            else:
                                st.error("Failed to delete tool from GitHub!")
