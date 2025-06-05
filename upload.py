import streamlit as st
import requests
import base64
import pandas as pd
from PIL import Image

# Ensure openpyxl is installed for reading .xlsx files
try:
    import openpyxl
except ImportError:
    st.error("Missing optional dependency 'openpyxl'. Use pip or conda to install openpyxl.")

# GitHub repository details
GITHUB_REPO = "Chakrapani2122/Data"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"

def upload_to_github(file, path, token):
    url = GITHUB_API_URL + path
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    content = file.read()
    content_base64 = base64.b64encode(content).decode("utf-8")
    
    # Check if the file already exists
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return 409, {"message": "File already exists"}
    
    data = {
        "message": f"Upload {path}",
        "content": content_base64
    }
    response = requests.put(url, json=data, headers=headers)
    st.write(f"Upload response status code: {response.status_code}")  # Log the status code
    return response.status_code, response.json()

def show_column_data_types(df):
    with st.expander("**Show Column Data Types**", expanded=False):
        column_data = []
        for col in df.columns:
            column_data.append({
                "Column Name": col,
                "Data Type": str(df[col].dtype)
            })
        # Organize data types into two columns
        col1, col2 = st.columns(2)
        with col1:
            st.table(pd.DataFrame(column_data[:len(column_data)//2]).set_index("Column Name"))
        with col2:
            st.table(pd.DataFrame(column_data[len(column_data)//2:]).set_index("Column Name"))

def get_repo_contents(token, path=""):
    url = GITHUB_API_URL + path
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch repository contents: {response.status_code} - {response.text}")
        return []

def display_file_content(token, path):
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        if 'application/vnd.ms-excel' in content_type or 'application/octet-stream' in content_type:
            return pd.read_excel(response.content)
        elif 'text/csv' in content_type:
            return pd.read_csv(response.content.decode('utf-8'))
        else:
            st.warning(f"Unsupported file type for preview: {content_type}")
            return pd.DataFrame()  # Return empty DataFrame for unsupported types
    else:
        st.error(f"Failed to fetch file content: {response.status_code} - {response.text}")
        return pd.DataFrame()  # Return empty DataFrame on error

def show_upload_page():
    st.title("📎 Upload Files")
    
    github_token = st.text_input("**Enter your security token**", type="password")
    
    uploaded_files = st.file_uploader("**Choose files**", type=["xlsx", "csv", "txt", "dat", "jpg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        uploaded_file_names = [uploaded_file.name for uploaded_file in uploaded_files]
        if len(uploaded_file_names) != len(set(uploaded_file_names)):
            st.warning("Duplicate files detected. Please remove duplicate files before uploading.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Select a file to view**")
            with col2:
                st.write("**Select a sheet (if applicable)**")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_file = st.selectbox("Select a file", uploaded_file_names, label_visibility="collapsed")
            with col2:
                sheet_name = None
                for uploaded_file in uploaded_files:
                    if uploaded_file.name == selected_file and uploaded_file.name.endswith(".xlsx"):
                        xls = pd.ExcelFile(uploaded_file)
                        sheet_name = st.selectbox("Select a sheet", xls.sheet_names, label_visibility="collapsed")
            st.write("**Showing First 100 Rows:**")
            with st.expander("Expand to view the first 100 rows", expanded=True):
                for uploaded_file in uploaded_files:
                    if uploaded_file.name == selected_file:
                        file_name = uploaded_file.name
                        try:
                            if file_name.endswith(".xlsx"):
                                df = pd.read_excel(xls, sheet_name=sheet_name)
                                st.dataframe(df.head(100))
                            elif file_name.endswith(".csv"):
                                df = pd.read_csv(uploaded_file)
                                st.dataframe(df.head(100))
                            elif file_name.endswith(".txt") or file_name.endswith(".dat"):
                                file_content = uploaded_file.getvalue().decode("utf-8")
                                st.text_area(file_name, file_content, height=300, max_chars=None, key=None)
                            elif file_name.endswith(".jpg") or file_name.endswith(".png"):
                                image = Image.open(uploaded_file)
                                st.image(image, caption=file_name)
                            else:
                                st.warning(f"Cannot display content of {file_name} (unsupported file type).")
                        except Exception as e:
                            st.warning(f"Cannot display content of {file_name} (error: {e}).")

            # Display data types of each column
            if file_name.endswith((".xlsx", ".csv")):
                show_column_data_types(df)

            # Research Area and Data Folder Selection
            research_areas = get_repo_contents(github_token)
            research_area_names = [area['name'] for area in research_areas if area['type'] == 'dir']

            col1, col2 = st.columns(2)
            with col1:
                selected_research_area = st.selectbox("Select Research Area", research_area_names, key="research_area_select")

            if selected_research_area:
                selected_area_contents = get_repo_contents(github_token, selected_research_area)
                folder_names = [folder['name'] for folder in selected_area_contents if folder['type'] == 'dir']

                with col2:
                    selected_data_folder = st.selectbox("Select Research Data Folder", folder_names, key="data_folder_select")

                if selected_data_folder:
                    upload_status = st.empty()  # Placeholder for upload status message
                    file_statuses = []  # List to hold the status of each file

                    if st.button("Upload"):
                        if github_token:
                            for uploaded_file in uploaded_files:
                                file_name = uploaded_file.name
                                path = f"{selected_research_area}/{selected_data_folder}/{file_name}"
                                # Re-read the file content to ensure it is not corrupted
                                uploaded_file.seek(0)
                                status_code, response = upload_to_github(uploaded_file, path, github_token)
                                if status_code == 201:
                                    file_statuses.append(f"File '{file_name}' uploaded successfully!")
                                elif status_code == 409:
                                    file_statuses.append(f"File '{file_name}' already exists at path: {path}")
                                else:
                                    file_statuses.append(f"Failed to upload file '{file_name}'. Error: {response}")

                            # Display the status of each file
                            for status in file_statuses:
                                upload_status.write(status)
                        else:
                            upload_status.error("Security token is required to upload files.")

if __name__ == "__main__":
    show_upload_page()
