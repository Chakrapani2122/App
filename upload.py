import streamlit as st
import requests
import base64

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
    return response.status_code, response.json()

def show_upload_page():
    st.title("Upload Files to GitHub")
    uploaded_files = st.file_uploader("Choose files", type=["xlsx", "csv", "txt", "dat"], accept_multiple_files=True)
    if uploaded_files:
        github_token = st.text_input("Enter your GitHub token", type="password")
        if st.button("Upload"):
            if github_token:
                for uploaded_file in uploaded_files:
                    file_name = uploaded_file.name
                    status_code, response = upload_to_github(uploaded_file, file_name, github_token)
                    if status_code == 201:
                        st.success(f"File '{file_name}' uploaded successfully!")
                        st.experimental_rerun()  # Clear the selected files and token input area
                    elif status_code == 409:
                        st.warning(f"File '{file_name}' already exists.")
                    else:
                        st.error(f"Failed to upload file '{file_name}'. Error: {response}")
            else:
                st.error("GitHub token is required to upload files.")

if __name__ == "__main__":
    show_upload_page()
