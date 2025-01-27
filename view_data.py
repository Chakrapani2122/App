import streamlit as st
import requests
import pandas as pd
from PIL import Image
from openpyxl import load_workbook

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

    selected_research_area = st.selectbox("**Select Research Area**", research_areas)
    if selected_research_area == "Root Directory":
        folder_path = ""
    else:
        selected_data_folder = st.selectbox("**Select Research Data Folder**", research_data_folders[selected_research_area])
        folder_path = f"{selected_research_area}/{selected_data_folder}"

    files = get_github_files(folder_path, github_token)
    if files:
        file_names = [file['name'] for file in files if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv', '.txt', '.png', '.jpg', '.jpeg', '.md'))]
        selected_file = st.selectbox("**Select a file**", file_names)
        
        if selected_file:
            file_url = next(file['download_url'] for file in files if file['name'] == selected_file)
            response = requests.get(file_url)
            if response.status_code == 200:
                try:
                    if selected_file.endswith(".xlsx"):
                        df = pd.read_excel(file_url, engine='openpyxl')
                        st.dataframe(df)
                    elif selected_file.endswith(".csv"):
                        df = pd.read_csv(file_url)
                        st.dataframe(df)
                    elif selected_file.endswith((".txt", ".md")):
                        file_content = requests.get(file_url).text
                        st.text_area("**File Content**", file_content, height=300, max_chars=None, key="text_file")
                    elif selected_file.endswith((".jpg", ".jpeg", ".png")):
                        image = Image.open(requests.get(file_url, stream=True).raw)
                        st.image(image, caption=selected_file)
                    else:
                        st.text_area("**File Content**", requests.get(file_url).text, height=300, max_chars=None, key="other_file")
                    
                    # Display data types of each column
                    if selected_file.endswith((".xlsx", ".csv")):
                        st.subheader("Column Data Types")
                        column_data = []
                        for col in df.columns:
                            column_data.append({
                                "Column Name": col,
                                "Data Type": str(df[col].dtype),
                                "Example Value": df[col].iloc[0] if not df[col].empty else "N/A",
                                "Description": ""
                            })
                        st.table(pd.DataFrame(column_data))
                except Exception as e:
                    st.error(f"Error reading the file: {e}")
                    st.text_area("**File Content**", requests.get(file_url).text, height=300, max_chars=None, key="read_error")
            else:
                st.error("Failed to fetch file content.")
        else:
            st.warning("No files found in the selected directory.")

if __name__ == "__main__":
    show_view_data_page()
