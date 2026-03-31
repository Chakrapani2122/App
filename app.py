import streamlit as st
import os
from PIL import Image, UnidentifiedImageError
from contact import show_contact_page
from upload import show_upload_page
from view_data import show_view_data_page
from visualizations import show_visualizations_page
from custom_visualizations import show_custom_visualizations_page
from data_schedule import show_data_schedule_page  # Import the new page

# Set the page configuration
st.set_page_config(
    page_title="King Arthur Project (KSU-SMAL Collaboration)",
    page_icon="assets/logo.png",
    layout="wide",
)

# Load the logo image with error handling
logo_path = os.path.join("assets", "logo.png")
logo2_path = os.path.join("assets", "logo2.png")
try:
    with open(logo_path, "rb") as f:
        Image.open(f).verify()  # Verify the image is valid
    logo_url = logo_path
except (FileNotFoundError, UnidentifiedImageError):
    st.error("Error: Logo image could not be loaded. Please check the file.")
    logo_url = None
try:
    with open(logo2_path, "rb") as f:
        Image.open(f).verify()  # Verify the image is valid
    logo2_url = logo2_path
except (FileNotFoundError, UnidentifiedImageError):
    st.error("Error: Logo image could not be loaded. Please check the file.")
    logo2_url = None
# Update the sidebar image to use the new logo if valid
if logo_url:
    st.sidebar.image(logo_url, width=50)
    st.sidebar.image(logo2_url, width=50)

st.sidebar.title("King Arthur Project")

# Navigation
page = st.sidebar.radio("Navigation", ["Home", "Upload", "View Data", "Data Schedule", "Visualizations", "Contact"], label_visibility="collapsed")

# Define the home page content
if page == "Home":
    col1, col2 = st.columns([1, 10])
    with col1:
        if logo_url:
            st.image(logo_url, width=100)
    with col2:
        if logo_url:
            st.image(logo2_url, width=100)
    st.write("## King Arthur Project with SMAL Lab at Kansas State University")
    try:
        st.image("assets/home.png", width="stretch")
    except TypeError:
        # Compatibility fallback for older Streamlit versions
        st.image("assets/home.png", use_column_width=True)
    st.write("")
    st.write("""
### Project Overview

The **King Arthur Project**, in collaboration with the **Soil Microbial Agroecology Lab (SMAL)** at **Kansas State University (KSU)**, is represented here with placeholder content while the new project narrative is being finalized.

---

## Placeholder Narrative

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Integer feugiat scelerisque varius morbi enim nunc faucibus a pellentesque sit.

---

## Upcoming Content Sections

- Lorem ipsum placeholder for mission and objectives.
- Lorem ipsum placeholder for research focus areas.
- Lorem ipsum placeholder for team and collaboration details.
- Lorem ipsum placeholder for publications and outcomes.
    """)

# Define the upload page content
elif page == "Upload":
    show_upload_page()

# Define the view data page content
elif page == "View Data":
    show_view_data_page()

# Define the data schedule page content
elif page == "Data Schedule":
    show_data_schedule_page()

# Define the visualizations page content (combined)
elif page == "Visualizations":
    # Use tabs to switch between the gallery and custom visualizations
    tab_gallery, tab_custom = st.tabs(["Gallery", "Custom"])

    with tab_gallery:
        # Let the module render its own header and prompt for a token if needed
        show_visualizations_page(None, show_header=True)

    with tab_custom:
        show_custom_visualizations_page(None, show_header=True)

# Define the contact page content
elif page == "Contact":
    show_contact_page()

