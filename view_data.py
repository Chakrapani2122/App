import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from PIL import Image

# GitHub repository details
GITHUB_REPO = "Chakrapani2122/Data"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"

def get_github_files(path="", token=""):
    url = GITHUB_API_URL + path
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Unauthorized access. Please check your GitHub token.")
        return []
    elif response.status_code == 404:
        st.error("Repository or path not found. Please check the folder path.")
        return []
    else:
        st.error(f"Failed to fetch files from GitHub. Status code: {response.status_code}")
        return []

def show_view_data_page():
    st.title("View Data")

    github_token = st.text_input("**Enter your GitHub token**", type="password")
    if not github_token:
        st.warning("GitHub token is required to access the repository.")
        return

    research_areas = ["Root Directory", "Ashland", "El Reno", "Perkins"]
    research_data_folders = {
        "Ashland": ["Forage", "Soil Biology & Biochemistry", "Soil Fertility", "Soil Health", "Soil Moisture", "Soil Water Lab", "Summer Crops", "Winter Crops"],
        "El Reno": ["Archive", "Cronos Data", "Field Data"],
        "Perkins": ["Plant Height & Soil Moisture"]
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**Select Research Area**")
    with col2:
        st.write("**Select Research Data Folder**")
    with col3:
        st.write("**Select a file**")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_research_area = st.selectbox("", research_areas)
    with col2:
        if selected_research_area == "Root Directory":
            folder_path = ""
        else:
            selected_data_folder = st.selectbox("", research_data_folders[selected_research_area])
            folder_path = f"{selected_research_area}/{selected_data_folder}"
    with col3:
        files = get_github_files(folder_path, github_token)
        if files:
            file_names = [file['name'] for file in files if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv', '.txt', '.png', '.jpg', '.jpeg', '.md'))]
            selected_file = st.selectbox("", file_names)
        else:
            selected_file = None

    if selected_file:
        file_url = next(file['download_url'] for file in files if file['name'] == selected_file)
        response = requests.get(file_url)
        if response.status_code == 200:
            try:
                file_content = BytesIO(response.content)
                if selected_file.endswith(".xlsx"):
                    xls = pd.ExcelFile(file_content)
                    sheet_name = st.selectbox("**Select a sheet**", xls.sheet_names)
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    st.dataframe(df)
                elif selected_file.endswith(".csv"):
                    df = pd.read_csv(file_content)
                    st.dataframe(df)
                elif selected_file.endswith((".txt", ".md")):
                    file_content = response.content.decode('utf-8', errors='replace')
                    st.text_area("**File Content**", file_content, height=300, max_chars=None, key="text_file")
                elif selected_file.endswith((".jpg", ".jpeg", ".png")):
                    image = Image.open(file_content)
                    st.image(image, caption=selected_file)
                else:
                    file_content = response.content.decode('utf-8', errors='replace')
                    st.text_area("**File Content**", file_content, height=300, max_chars=None, key="other_file")
            except Exception as e:
                st.error(f"Error reading the file: {e}")
                st.text_area("**File Content**", response.content.decode('utf-8', errors='replace'), height=300, max_chars=None, key="read_error")
        else:
            st.error("Failed to fetch file content.")
    else:
        st.warning("No files found in the selected directory.")

if __name__ == "__main__":
    show_view_data_page()
