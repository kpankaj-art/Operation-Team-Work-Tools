import streamlit as st

st.set_page_config(page_title="My Dynamic Tools Portal", layout="wide")

st.title("🛠️ My Utility Tools Dashboard")
st.write("Yahan aap apne naye tools add kar sakte hain aur unhe direct access kar sakte hain.")

# Session state initialize kar rahe hain taaki naye added links save rahein
if "tools_list" not in st.session_state:
    # Default tools list
    st.session_state.tools_list = [
        {
            "name": "Brand to PPT Generator", 
            "url": "https://share.streamlit.io/", 
            "desc": "Convert brand guidelines into PPT"
        },
        {
            "name": "Duplicate Image Finder", 
            "url": "https://share.streamlit.io/", 
            "desc": "Find and remove duplicate images"
        }
    ]

# --- SIDEBAR: Manual Input Form ---
st.sidebar.header("➕ Add New Tool Link")

with st.sidebar.form("add_tool_form", clear_on_submit=True):
    tool_name = st.text_input("Tool ka Naam (Name):")
    tool_url = st.text_input("Tool ka Link (URL):")
    tool_desc = st.text_area("Ye Link kya kaam karta hai (Description):")
    
    submit_button = st.form_submit_button("Dashboard me Add Karein")

    if submit_button:
        if tool_name and tool_url:
            # New tool ko list me append karna
            new_tool = {
                "name": tool_name,
                "url": tool_url,
                "desc": tool_desc if tool_desc else "No description provided."
            }
            st.session_state.tools_list.append(new_tool)
            st.sidebar.success(f"'{tool_name}' Dashboard me add ho gaya!")
        else:
            st.sidebar.error("Kripya Naam aur Link dono bharein!")

# --- MAIN DASHBOARD DISPLAY ---
st.divider()

if not st.session_state.tools_list:
    st.info("Abhi koi tool add nahi hai. Sidebar se naya tool add karein.")
else:
    # Cards layout using columns
    cols = st.columns(2)
    for index, tool in enumerate(st.session_state.tools_list):
        col = cols[index % 2]
        with col:
            with st.container(border=True):
                st.subheader(f"📌 {tool['name']}")
                st.write(f"**Kaam:** {tool['desc']}")
                st.link_button(f"Open {tool['name']} 🚀", tool['url'])
