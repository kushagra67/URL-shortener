import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="URL Shortener",
    page_icon="🔗",
    layout="wide"
)

BACKEND_URL = "http://localhost:8000"

st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stTextInput > label {
        font-size: 18px;
        font-weight: bold;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("URL Shortener")
st.markdown("---")

with st.sidebar:
    st.header("About")
    st.info("""
    **URL Shortener** helps you convert long URLs into short, shareable links.
    
    Features:
    - Generate short codes
    - Track clicks
    - View all shortened URLs
    - Copy to clipboard
    """)
    st.markdown("---")
    st.subheader("Backend Status")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("Backend is running")
        else:
            st.error("Backend error")
    except Exception as e:
        st.error(f"Cannot connect to backend\n\n{str(e)}")

tab1, tab2, tab3 = st.tabs(["Shorten URL", "View All URLs", "URL Info"])

with tab1:
    st.header("Create a Short URL")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        long_url = st.text_input(
            "Enter your long URL",
            placeholder="https://example.com/very/long/url/path",
            key="url_input"
        )
    
    with col2:
        shorten_button = st.button("Shorten", use_container_width=True)
    
    if shorten_button:
        if not long_url:
            st.error("Please enter a URL")
        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/shorten",
                    json={"url": long_url},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    short_code = data["short_code"]
                    short_url = f"{BACKEND_URL}/{short_code}"
                    
                    st.markdown(f"""
                        <div class='success-box'>
                        <h4>Success!</h4>
                        <p><strong>Original URL:</strong> {long_url}</p>
                        <p><strong>Short URL:</strong> 
                        <code>{short_url}</code></p>
                        <p><strong>Short Code:</strong> <code>{short_code}</code></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Copy button
                    st.code(short_url, language="text")
                    st.success(f"Share this link: {short_url}")
                    
                else:
                    error_msg = response.json().get("detail", "Unknown error")
                    st.markdown(f"""
                        <div class='error-box'>
                        <h4>Error</h4>
                        <p>{error_msg}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure FastAPI is running on http://localhost:8000")
            except requests.exceptions.Timeout:
                st.error("Request timed out. Backend might be slow.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    st.header("All Shortened URLs")
    
    if st.button("Refresh URLs"):
        pass
    
    try:
        response = requests.get(f"{BACKEND_URL}/urls", timeout=5)
        
        if response.status_code == 200:
            urls = response.json()
            
            if not urls:
                st.info("No shortened URLs yet. Create one in the 'Shorten URL' tab!")
            else:
                for short_code, details in urls.items():
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**Code:** `{short_code}`")
                            st.markdown(f"**Created:** {details['created_at']}")
                        
                        with col2:
                            st.markdown(f"**Original URL:** {details['original_url']}")
                        
                        with col3:
                            st.metric("Clicks", details['clicks'])
                        
                        button_col1, button_col2 = st.columns(2)
                        with button_col1:
                            if st.button(f"Copy", key=f"copy_{short_code}"):
                                st.success(f"Copied: {short_code}")
                        
                        with button_col2:
                            if st.button(f"Delete", key=f"delete_{short_code}"):
                                try:
                                    del_response = requests.delete(f"{BACKEND_URL}/{short_code}", timeout=5)
                                    if del_response.status_code == 200:
                                        st.success(f"Deleted {short_code}")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting: {str(e)}")
        else:
            st.error("Failed to fetch URLs")
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Make sure FastAPI is running.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with tab3:
    st.header("Get URL Information")
    
    short_code_input = st.text_input(
        "Enter short code",
        placeholder="abc123",
        key="info_input"
    )
    
    if st.button("Get Info"):
        if not short_code_input:
            st.error("Please enter a short code")
        else:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/info/{short_code_input}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.markdown(f"""
                        <div class='success-box'>
                        <h4>URL Details</h4>
                        <p><strong>Short Code:</strong> <code>{short_code_input}</code></p>
                        <p><strong>Original URL:</strong> {data['original_url']}</p>
                        <p><strong>Created At:</strong> {data['created_at']}</p>
                        <p><strong>Total Clicks:</strong> {data['clicks']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                else:
                    st.error(f"Short code '{short_code_input}' not found")
                    
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p>Built with FastAPI + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
