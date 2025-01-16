import streamlit as st
from about import show_about_page
from contact import show_contact_page
from upload import show_upload_page

# Set the page configuration
st.set_page_config(page_title="Kansas State University - SMAL Project", page_icon="assets/logo.png", layout="wide")

# Load the logo image
logo_url = "assets/logo.png"

# Create a sidebar for navigation
st.sidebar.image(logo_url, width=50)
st.sidebar.title("SMAL Project")
page = st.sidebar.radio("Go to", ["Home", "Upload", "About", "Contact"])

# Define the home page content
if page == "Home":
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image(logo_url, width=100)
    with col2:
        st.title("Welcome to the SMAL Project")
    st.write("")
    st.write("This is the home page of the Kansas State University SMAL Project.")

# Define the upload page content
elif page == "Upload":
    show_upload_page()

# Define the about page content
elif page == "About":
    show_about_page()

# Define the contact page content
elif page == "Contact":
    show_contact_page()
