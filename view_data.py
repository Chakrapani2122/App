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

    github_token = st.text_input("Enter your GitHub token", type="password")
    if not github_token:
        st.warning("GitHub token is required to access the repository.")
        return

    folder_path = ""
    files = get_github_files(folder_path, github_token)
    if files:
        subdirectories = [file['name'] for file in files if file['type'] == 'dir']
        root_files = [file['name'] for file in files if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv', '.txt', '.dat', '.png', '.jpg', '.jpeg', '.heic', '.md'))]
        
        selected_subdirectory = st.selectbox("Select a subdirectory", ["Root Directory"] + subdirectories)
        if selected_subdirectory == "Root Directory":
            file_names = root_files
        else:
            subdirectory_files = get_github_files(f"{folder_path}/{selected_subdirectory}", github_token)
            file_names = [file['name'] for file in subdirectory_files if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv', '.txt', '.dat', '.png', '.jpg', '.jpeg', '.heic', '.md'))]
        
        if file_names:
            selected_file = st.selectbox("Select a file", file_names)
            if selected_file:
                if selected_subdirectory == "Root Directory":
                    file_url = next(file['download_url'] for file in files if file['name'] == selected_file)
                else:
                    file_url = next(file['download_url'] for file in subdirectory_files if file['name'] == selected_file)
                
                response = requests.get(file_url)
                if response.status_code == 200:
                    try:
                        if selected_file.endswith(".xlsx"):
                            try:
                                xls = pd.ExcelFile(BytesIO(response.content))
                                sheet_name = st.selectbox("Select a sheet", xls.sheet_names)
                                df = pd.read_excel(BytesIO(response.content), sheet_name=sheet_name)
                                st.dataframe(df)
                            except Exception as e:
                                st.error(f"Error reading the .xlsx file: {e}")
                                try:
                                    st.text_area("File Content", response.content.decode("utf-8"), height=300, max_chars=None, key=None, disabled=True)
                                except UnicodeDecodeError:
                                    st.text_area("File Content", response.content.decode("latin1"), height=300, max_chars=None, key=None, disabled=True)
                        elif selected_file.endswith(".csv"):
                            df = pd.read_csv(BytesIO(response.content))
                            st.dataframe(df)
                        elif selected_file.endswith((".txt", ".dat", ".md")):
                            try:
                                file_content = response.content.decode("utf-8")
                            except UnicodeDecodeError:
                                file_content = response.content.decode("latin1")
                            st.text_area("File Content", file_content, height=300, max_chars=None, key=None, disabled=True)
                        elif selected_file.endswith((".jpg", ".jpeg", ".png", ".heic")):
                            image = Image.open(BytesIO(response.content))
                            st.image(image, caption=selected_file)
                        else:
                            st.text_area("File Content", response.content.decode("utf-8"), height=300, max_chars=None, key=None, disabled=True)
                    except Exception as e:
                        st.error(f"Error reading the file: {e}")
                        try:
                            st.text_area("File Content", response.content.decode("utf-8"), height=300, max_chars=None, key=None, disabled=True)
                        except UnicodeDecodeError:
                            st.text_area("File Content", response.content.decode("latin1"), height=300, max_chars=None, key=None, disabled=True)
                else:
                    st.error("Failed to fetch file content.")
        else:
            st.warning("No files found in the selected directory.")

if __name__ == "__main__":
    show_view_data_page()
