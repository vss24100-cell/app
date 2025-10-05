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

# Custom CSS for green zoo theme
st.markdown("""
<style>
    /* Main background and container styling */
    .stApp {
        background: linear-gradient(135deg, #0d3d1f 0%, #1a5c2e 50%, #0d3d1f 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: #7FD65B;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: 700;
    }
    
    /* Card/Panel styling with zoo theme */
    .role-selector {
        background: linear-gradient(145deg, #1e4d2b, #2a6b3a);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        border: 2px solid #4CAF50;
    }
    
    /* Form container styling */
    div[data-testid="stForm"] {
        background: linear-gradient(145deg, #1e4d2b, #2a6b3a);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #66BB6A;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(30, 77, 43, 0.7);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(42, 107, 58, 0.8);
        border-radius: 8px;
        color: #A5D6A7;
        font-weight: 600;
        border: 1px solid #4CAF50;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #4CAF50, #66BB6A) !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
    }
    
    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #66BB6A !important;
        border-radius: 8px !important;
        color: #1e4d2b !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #81C784 !important;
        box-shadow: 0 0 0 2px rgba(129, 199, 132, 0.3) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(145deg, #4CAF50, #66BB6A);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #66BB6A, #81C784);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.5);
        transform: translateY(-2px);
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(145deg, #2E7D32, #43A047);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #7FD65B;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Error message styling */
    .error-message {
        background: linear-gradient(145deg, #C62828, #D32F2F);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #FF6B6B;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Info/warning styling */
    div[data-testid="stNotification"] {
        background: linear-gradient(145deg, #1e4d2b, #2a6b3a);
        border: 2px solid #4CAF50;
        border-radius: 10px;
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        background: linear-gradient(145deg, #1e4d2b, #2a6b3a);
        border: 2px solid #4CAF50;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d3d1f 0%, #1a5c2e 100%);
        border-right: 3px solid #4CAF50;
    }
    
    /* Label styling */
    label {
        color: #1e4d2b !important;
        font-weight: 600 !important;
    }
    
    /* Paragraph and general text styling */
    p, div, span {
        color: #000000 !important;
    }
    
    /* Animal/Zoo themed decorative elements */
    h1, h2, h3 {
        color: #7FD65B !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
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
