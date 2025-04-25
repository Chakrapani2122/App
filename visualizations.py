import streamlit as st
import requests
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
import base64

# GitHub repository details
GITHUB_REPO = "Chakrapani2122/Data"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/visualizations/"

def fetch_visualizations(token):
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch visualizations.")
        return []

def fetch_description(token):
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(GITHUB_API_URL + "descriptions.xml", headers=headers)
    if response.status_code == 200:
        return base64.b64decode(response.json()['content']).decode('utf-8')
    else:
        st.error("Failed to fetch descriptions.")
        return None

def show_visualizations_page():
    st.title("📈 Visualizations")
    st.write("For better experience, please enable the wide mode.")

    github_token = st.text_input("Enter security token", type="password")
    if github_token:
        visualizations = fetch_visualizations(github_token)
        description_xml = fetch_description(github_token)

        descriptions = {}
        if description_xml:
            try:
                root = ET.fromstring(description_xml)
                for viz in root.findall("Visualization"):
                    name = viz.find("Name").text
                    description = viz.find("Description").text
                    descriptions[name] = description
            except ET.ParseError as e:
                st.error(f"Failed to parse descriptions XML: {e}")

        for viz in visualizations:
            if viz['name'].endswith('.png'):
                image_url = viz['download_url']
                image_name = viz['name'].replace('.png', '')
                image_description = descriptions.get(image_name, "No description available")

                response = requests.get(image_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(image, caption=image_name)
                    with col2:
                        st.write(f"**Name:** {image_name}")
                        st.write(f"**Description:** {image_description}")

if __name__ == "__main__":
    show_visualizations_page()
