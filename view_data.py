import streamlit as st
import requests
from io import BytesIO
import pandas as pd
from PIL import Image
from openpyxl.utils.exceptions import InvalidFileException
import xml.etree.ElementTree as ET
from pandas.errors import EmptyDataError

# Function to validate GitHub PAT
def validate_token(token):
    repo = "Chakrapani2122/Data"
    url = f"https://api.github.com/repos/{repo}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

# Function to get repository contents
def get_repo_contents(token, path=""):
    repo = "Chakrapani2122/Data"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to display file content
def display_file_content(token, path):
    repo = "Chakrapani2122/Data"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        if content['type'] == 'file':
            file_content = requests.get(content['download_url']).content
            if path.endswith(('.xlsx', '.xls')):
                excel_file = BytesIO(file_content)
                try:
                    xls = pd.ExcelFile(excel_file, engine='openpyxl')
                    sheet = st.selectbox('Select sheet', xls.sheet_names, key="sheet_select")
                    df = pd.read_excel(excel_file, sheet_name=sheet)
                    st.dataframe(df)
                except InvalidFileException:
                    st.error("The .xlsx file appears to be invalid or corrupted.")
                except Exception as e:
                    st.error(f"An error occurred while reading the Excel file: {e}")
            elif path.endswith('.csv'):
                try:
                    df = pd.read_csv(BytesIO(file_content))
                    st.dataframe(df)
                except EmptyDataError:
                    st.error("The CSV file is empty or improperly formatted.")
                except Exception as e:
                    st.error(f"An error occurred while reading the CSV file: {e}")
            elif path.endswith(('.txt', '.md')):
                st.text(file_content.decode())
            elif path.endswith(('.jpg', '.jpeg', '.png')):
                image = Image.open(BytesIO(file_content))
                st.image(image, caption=path)
            else:
                st.text(file_content.decode())
        else:
            st.error("Selected path is not a file.")
    else:
        st.error("Failed to retrieve file content.")

# Function to show the view data page
def show_view_data_page():
    st.title("📊 View Data")

    # Input for GitHub PAT
    token = st.text_input("Enter security token", type="password", key="github_token")

    if token:
        if validate_token(token):
            st.success("Token validated successfully!")

            research_areas = ["Root Directory", "Ashland", "El Reno", "Perkins"]
            research_data_folders = {
                "Ashland": ["Forage", "Micrometereology", "Soil Biology & Biochemistry", "Soil Fertility", "Soil Health", "Soil Moisture", "Soil Water Lab", "Summer Crops", "Winter Crops"],
                "El Reno": ["Archive", "Cronos Data", "Field Data"],
                "Perkins": ["Plant Height & Soil Moisture"]
            }

            col1, col2, col3 = st.columns(3)
            with col1:
                selected_research_area = st.selectbox("Select Research Area", research_areas, key="research_area_select")
            with col2:
                if selected_research_area == "Root Directory":
                    folder_path = ""
                else:
                    selected_data_folder = st.selectbox("Select Research Data Folder", research_data_folders[selected_research_area], key="data_folder_select")
                    folder_path = f"{selected_research_area}/{selected_data_folder}"
            with col3:
                files = get_repo_contents(token, folder_path)
                if files:
                    file_names = [file['name'] for file in files if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv', '.txt', '.png', '.jpg', '.jpeg', '.md'))]
                    selected_file = st.selectbox("Select a file", file_names, key="file_select")
                else:
                    selected_file = None

            if selected_file:
                file_path = f"{folder_path}/{selected_file}" if folder_path else selected_file
                st.write("**File Contents**")
                display_file_content(token, file_path)
        else:
            st.error("Invalid token.")



