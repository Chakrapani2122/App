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
GITHUB_COMMITS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits"

def upload_to_github(file, path, token):
    url = GITHUB_API_URL + path
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    content = file.read()
    if isinstance(content, bytes):
        content = base64.b64encode(content).decode("utf-8")
    else:
        content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    # Check if the file already exists
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return 409, {"message": "File already exists"}
    
    data = {
        "message": f"Upload {path}",
        "content": content
    }
    response = requests.put(url, json=data, headers=headers)
    st.write(f"Upload response status code: {response.status_code}")  # Log the status code
    return response.status_code, response.json()

def get_commit_history(token):
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(GITHUB_COMMITS_URL, headers=headers)
    if response.status_code == 200:
        return response.json()[:5]  # Get the last 5 commits
    else:
        return []

def show_upload_page():
    st.title("Upload Files to GitHub")
    
    github_token = st.text_input("**Enter your GitHub token**", type="password")
    if github_token:
        commits = get_commit_history(github_token)
        if commits:
            st.subheader("Last 5 Commits")
            for commit in commits:
                st.write(f"- {commit['commit']['author']['date']}: {commit['commit']['author']['name']}: {commit['commit']['message']}")
        else:
            st.warning("Failed to retrieve commit history. Please check your GitHub token.")
    
    uploaded_files = st.file_uploader("**Choose files**", type=["xlsx", "csv", "txt", "dat", "jpg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        uploaded_file_names = [uploaded_file.name for uploaded_file in uploaded_files]
        if len(uploaded_file_names) != len(set(uploaded_file_names)):
            st.warning("Duplicate files detected. Please remove duplicate files before uploading.")
        else:
            selected_file = st.selectbox("**Select a file to view**", uploaded_file_names)
            for uploaded_file in uploaded_files:
                if uploaded_file.name == selected_file:
                    file_name = uploaded_file.name
                    try:
                        if file_name.endswith(".xlsx"):
                            xls = pd.ExcelFile(uploaded_file)
                            sheet_name = st.selectbox("**Select a sheet**", xls.sheet_names)
                            df = pd.read_excel(xls, sheet_name=sheet_name)
                            st.dataframe(df)
                        elif file_name.endswith(".csv"):
                            df = pd.read_csv(uploaded_file)
                            st.dataframe(df)
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
            
            upload_status = st.empty()  # Placeholder for upload status message
            file_statuses = []  # List to hold the status of each file
            
            if st.button("Upload"):
                if github_token:
                    for uploaded_file in uploaded_files:
                        file_name = uploaded_file.name
                        status_code, response = upload_to_github(uploaded_file, file_name, github_token)
                        if status_code == 201:
                            file_statuses.append(f"File '{file_name}' uploaded successfully!")
                        elif status_code == 409:
                            file_statuses.append(f"File '{file_name}' already exists at path: {file_name}")
                        else:
                            file_statuses.append(f"Failed to upload file '{file_name}'. Error: {response}")
                    
                    # Display the status of each file
                    for status in file_statuses:
                        upload_status.write(status)
                else:
                    upload_status.error("GitHub token is required to upload files.")

if __name__ == "__main__":
    show_upload_page()
