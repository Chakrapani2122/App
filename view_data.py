import streamlit as st
import requests
from io import BytesIO
import pandas as pd
from PIL import Image
from openpyxl import load_workbook
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
@st.cache_data(ttl=300)
def get_repo_contents(token, path=""):
    repo = "Chakrapani2122/Data"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to display column data types
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
                    show_column_data_types(df)
                    return df
                except InvalidFileException:
                    st.error("The .xlsx file appears to be invalid or corrupted.")
                except Exception as e:
                    st.error(f"An error occurred while reading the Excel file: {e}")
            elif path.endswith('.csv'):
                try:
                    df = pd.read_csv(BytesIO(file_content))
                    st.dataframe(df)
                    show_column_data_types(df)
                    return df
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
    return None

# Function to show the view data page
def show_view_data_page():
    st.title("📊 View Data")

    # Use token from session_state if available, otherwise prompt
    # Get token from session or prompt. If prompted here and validated, persist to session.
    token = st.session_state.get('github_token')
    if not token:
        input_token = st.text_input("Enter security token", type="password", key="github_token_view")
        if input_token:
            if validate_token(input_token):
                st.success("Token validated successfully and saved for this session.")
                st.session_state['github_token'] = input_token
                token = input_token
            else:
                st.error("Invalid token.")

    if token:
        if validate_token(token):
            st.success("Token validated successfully!")

            research_areas = get_repo_contents(token)
            research_area_names = [area['name'] for area in research_areas if area['type'] == 'dir']

            col1, col2, col3 = st.columns(3)
            with col1:
                selected_research_area = st.selectbox("Select Research Area", research_area_names, key="research_area_select")

            if selected_research_area:
                selected_area_contents = get_repo_contents(token, selected_research_area)
                folder_names = [folder['name'] for folder in selected_area_contents if folder['type'] == 'dir']

                with col2:
                    selected_data_folder = st.selectbox("Select Research Data Folder", folder_names, key="data_folder_select")

                if selected_data_folder:
                    selected_folder_contents = get_repo_contents(token, f"{selected_research_area}/{selected_data_folder}")
                    file_names = [file['name'] for file in selected_folder_contents if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv', '.txt', '.png', '.jpg', '.jpeg', '.md'))]

                    with col3:
                        selected_file = st.selectbox("Select a file", file_names, key="file_select")

                    if selected_file:
                        file_path = f"{selected_research_area}/{selected_data_folder}/{selected_file}"
                        st.write("**File Contents**")
                        df = display_file_content(token, file_path)

                        # Add an expander below the data types button to display additional data insights
                        with st.expander("**Expand to view data insights**", expanded=False):
                            if df is not None:
                                st.write(f"**Shape:** {df.shape[0]} rows and {df.shape[1]} columns")
                                missing_values = pd.DataFrame({
                                    "Column Name": df.columns,
                                    "Missing Values": df.isnull().sum().values
                                })
                                missing_values = missing_values[missing_values["Missing Values"] > 0]  # Filter columns with missing values > 0
                                if not missing_values.empty:
                                    st.write("**Missing Values:**")
                                    num_columns = 4
                                    columns = st.columns(num_columns)
                                    for i, row in missing_values.iterrows():
                                        col_index = i % num_columns
                                        with columns[col_index]:
                                            st.write(f"{row['Column Name']}: {row['Missing Values']}")
                                else:
                                    st.write("**Missing Values:** There are no missing values in this sheet.")
                                st.write("**Descriptive Analysis:**")
                                st.dataframe(df.describe())
                            else:
                                st.warning("No data available to display insights.")
        else:
            st.error("Invalid token.")



