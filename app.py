import streamlit as st
from contact import show_contact_page
from upload import show_upload_page
from view_data import show_view_data_page
from visualizations import show_visualizations_page
from custom_visualizations import show_custom_visualizations_page
from data_schedule import show_data_schedule_page  # Import the new page

# Set the page configuration
st.set_page_config(page_title="Kansas State University - SMAL Lab", page_icon="assets/logo.png", layout="wide")

# Load the logo image
logo_url = "assets/logo.png"

# Create a sidebar for navigation
st.sidebar.image(logo_url, width=50)
st.sidebar.title("SMAL Lab")
page = st.sidebar.radio("Navigation", ["Home", "Upload", "View Data", "Data Schedule", "Visualizations", "Custom Visualizations", "Contact"], label_visibility="collapsed")

# Define the home page content
if page == "Home":
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image(logo_url, width=100)
    with col2:
        st.title("Welcome to the SMAL Lab")
    st.write("")
    st.write("""
    The Soil Microbial Agroecology Lab (SMAL) at Kansas State University is dedicated to advancing soil health through comprehensive research on water efficiency, nutrient and energy balance, and climate change.

    **Vision and Mission**

    SMAL envisions sustainable agricultural systems that are productive, efficient in water, nutrients, and energy, resilient to climate change, and promote soil health. The lab aims to provide leadership in understanding soil microbial ecology in grassland and agricultural systems, applying this knowledge to optimize nutrient, water, and residue management for sustainable production systems that conserve resources and offer ecosystem services.

    **Research Focus**

    The lab's research is centered on three key areas:

    - Microbial Ecology and Processes: Investigating the microbial ecology, carbon (C), and nitrogen (N) processes in grassland and agricultural ecosystems.
    - Soil Health Indicators: Identifying biological indicators of soil health and practices that sustain and enhance it.
    - Rhizosphere Microbes: Exploring the role and potential of microbes in the rhizosphere to boost plant growth and improve water and nutrient efficiency.

    **Research Areas**

    SMAL conducts research on:

    - Carbon and nitrogen analysis in different land uses.
    - Carbon and nitrogen mineralization.
    - Factors affecting soil fungi and bacteria populations.
    - Mycorrhizae population dynamics.
    - Effects of tillage, nutrients, and cropping systems on soil microbial populations.
    - Soil aggregate formation and stability.
    - Soil water infiltration capability.
    - Phospholipid fatty acids and neutral lipid fatty acids in soil organic matter.
    - Soil enzyme activity.
    - Stable isotope 13C and 15N analysis.

    **Leadership**

    The lab is led by Dr. Charles (Chuck) Rice, a University Distinguished Professor and holder of the Vanier University Professorship at Kansas State University. Dr. Rice is a Professor of Soil Microbiology in the Department of Agronomy and has received significant recognition for his work, including co-winning the 2007 Nobel Peace Prize for his contributions to the United Nations’ Intergovernmental Panel on Climate Change.

    Through its research and leadership, SMAL contributes to the advancement of sustainable agricultural practices and the promotion of soil health.
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

# Define the visualizations page content
elif page == "Visualizations":
    show_visualizations_page()

# Define the custom visualizations page content
elif page == "Custom Visualizations":
    show_custom_visualizations_page()

# Define the contact page content
elif page == "Contact":
    show_contact_page()

