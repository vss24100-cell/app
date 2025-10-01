import streamlit as st
import os
from datetime import datetime
from auth import authenticate_user, get_user_role
from components.admin_interface import show_admin_interface
from components.doctor_interface import show_doctor_interface
from components.zookeeper_interface import show_zookeeper_interface

# Configure page
st.set_page_config(
    page_title="Zoo Management System",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme enhancements
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #4CAF50;
        margin-bottom: 2rem;
    }
    .role-selector {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #1B5E20;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #B71C1C;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''
    if 'selected_role' not in st.session_state:
        st.session_state.selected_role = 'Zoo Keeper'

def show_login_page():
    """Display login interface"""
    st.markdown('<h1 class="main-header">🦁 Zoo Management System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="role-selector">', unsafe_allow_html=True)
        
        # Role selection
        role_options = ['Zoo Keeper', 'Doctor', 'Admin']
        selected_role = st.selectbox(
            "Select Your Role:",
            role_options,
            key="role_select"
        )
        st.session_state.selected_role = selected_role
        
        st.markdown("### Login Credentials")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username and password:
                    if authenticate_user(username, password, selected_role.lower().replace(' ', '')):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = selected_role.lower().replace(' ', '')
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or role mismatch!")
                else:
                    st.error("Please enter both username and password!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Demo credentials info
        with st.expander("Demo Credentials"):
            st.write("**Zoo Keeper:** keeper1 / password123")
            st.write("**Doctor:** doctor1 / medpass456") 
            st.write("**Admin:** admin1 / adminpass789")

def show_main_interface():
    """Display main interface based on user role"""
    # Sidebar with user info and logout
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}!")
        st.markdown(f"**Role:** {st.session_state.user_role.title()}")
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ''
            st.session_state.user_role = ''
            st.rerun()
        
        st.markdown("---")
        st.markdown("### System Info")
        st.info(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Main content based on role
    if st.session_state.user_role == 'zookeeper':
        show_zookeeper_interface()
    elif st.session_state.user_role == 'doctor':
        show_doctor_interface()
    elif st.session_state.user_role == 'admin':
        show_admin_interface()

def main():
    """Main application function"""
    initialize_session_state()
    
    # Create necessary directories
    os.makedirs("data/observations", exist_ok=True)
    os.makedirs("data/comments", exist_ok=True)
    
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_interface()

if __name__ == "__main__":
    main()