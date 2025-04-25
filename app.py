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
st.set_page_config(page_title="Kansas State University - SMAL Lab", page_icon="assets/logo.png", layout="wide")

# Load the logo image with error handling
logo_path = os.path.join("assets", "logo.png")
try:
    with open(logo_path, "rb") as f:
        Image.open(f).verify()  # Verify the image is valid
    logo_url = logo_path
except (FileNotFoundError, UnidentifiedImageError):
    st.error("Error: Logo image could not be loaded. Please check the file.")
    logo_url = None

# Update the sidebar image to use the new logo if valid
if logo_url:
    st.sidebar.image(logo_url, width=50)

st.sidebar.title("SMAL Lab")
page = st.sidebar.radio("Navigation", ["Home", "Upload", "View Data", "Data Schedule", "Visualizations", "Custom Visualizations", "Contact"], label_visibility="collapsed")

# Define the home page content
if page == "Home":
    col1, col2 = st.columns([1, 10])
    with col1:
        if logo_url:
            st.image(logo_url, width=100)
    with col2:
        st.title("Welcome!")
    st.write("## 🌱 Soil Microbial Agroecology Lab (SMAL - KSU)  ")
    st.image("assets/home.png", use_column_width=True)
    st.write("")
    st.write("""
### Kansas State University

The **Soil Microbial Agroecology Lab (SMAL)** at Kansas State University is dedicated to advancing **soil health** through comprehensive research on 💧 water efficiency, ⚖️ nutrient and energy balance, and 🌍 climate change.

---

## 🌟 Vision and Mission

SMAL envisions **sustainable agricultural systems** that are:
- 🌾 Productive  
- 💦 Efficient in water, nutrients, and energy  
- 🌡️ Resilient to climate change  
- 🌿 Promoting soil health  

The lab aims to provide leadership in understanding **soil microbial ecology** in **grassland** and **agricultural systems**, applying this knowledge to optimize:
- 💧 Water management  
- 🌾 Nutrient management  
- 🍂 Residue management  

All for **sustainable production systems** that:
- 🛡️ Conserve resources  
- ♻️ Offer ecosystem services  

---

## 🔬 Research Focus

The lab's research is centered on three key areas:

1. 🧫 **Microbial Ecology and Processes**  
   Investigating microbial ecology, carbon (C), and nitrogen (N) processes in grassland and agricultural ecosystems.

2. 🌱 **Soil Health Indicators**  
   Identifying biological indicators of soil health and practices that sustain and enhance it.

3. 🌿 **Rhizosphere Microbes**  
   Exploring the role and potential of microbes in the rhizosphere to boost 🌾 plant growth and improve 💧 water and nutrient efficiency.

---

## 🧪 Research Areas

SMAL conducts research on:

- 🧮 Carbon and nitrogen analysis in different land uses  
- 🔁 Carbon and nitrogen mineralization  
- 🦠 Factors affecting soil fungi and bacteria populations  
- 🍄 Mycorrhizae population dynamics  
- 🚜 Effects of tillage, nutrients, and cropping systems on soil microbial populations  
- 🧱 Soil aggregate formation and stability  
- 💧 Soil water infiltration capability  
- 🧬 Phospholipid fatty acids and neutral lipid fatty acids in soil organic matter  
- ⚙️ Soil enzyme activity  
- 🔬 Stable isotope 13C and 15N analysis  

---

## 👨‍🔬 Leadership

The lab is led by **Dr. Charles (Chuck) Rice**:
- 🏅 University Distinguished Professor  
- 🎓 Holder of the Vanier University Professorship at Kansas State University  

Dr. Rice is a Professor of **Soil Microbiology** in the Department of Agronomy and has received significant recognition for his work, including:

🕊️ **Co-winner of the 2007 Nobel Peace Prize** for contributions to the **United Nations’ Intergovernmental Panel on Climate Change**.

📚 **Published over 100 scholarly publications**.

🌱 **Past President** of the **Soil Science Society of America** (2011).

🧪 **Current Service Roles**:
  - Member, **National Academies Board on Agriculture**
  - Member, **USDA Agricultural Air Quality Task Force**
  - Chair, **Commission on Soils, Food Security and Public Health**, International Union of Soil Sciences

🌍 Recognized as a **Fellow** of:
  - Soil Science Society of America
  - American Society of Agronomy
  - American Association for the Advancement of Science (AAAS)
---

Through its research and leadership, **SMAL** contributes to the advancement of:
- 🌾 Sustainable agricultural practices  
- 🌱 Promotion of soil health

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

