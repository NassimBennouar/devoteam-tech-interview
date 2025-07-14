import streamlit as st

st.set_page_config(page_title="Infrastructure Monitoring", page_icon="📊", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username == "jean" and password == "jean":
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
else:
    st.title("🏗️ Infrastructure Monitoring Dashboard")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Welcome! Use the sidebar to navigate between ingestion and analysis pages.")
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun() 