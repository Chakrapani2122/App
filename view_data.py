import streamlit as st
import requests
from io import BytesIO
import pandas as pd
from PIL import Image
from openpyxl.utils.exceptions import InvalidFileException
from pandas.errors import EmptyDataError

GITHUB_REPO = "Chakrapani2122/Data"
SUPPORTED_EXTENSIONS = ('.xlsx', '.xls', '.csv', '.txt', '.md', '.png', '.jpg', '.jpeg', '.dat')


# Function to validate GitHub PAT
def validate_token(token):
    url = f"https://api.github.com/repos/{GITHUB_REPO}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200


# Function to get repository contents at a given path
@st.cache_data(ttl=300)
def get_repo_contents(token, path=""):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        # GitHub returns a list for directories, dict for single files
        if isinstance(result, list):
            return result
        return None
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
        col1, col2 = st.columns(2)
        with col1:
            st.table(pd.DataFrame(column_data[:len(column_data) // 2]).set_index("Column Name"))
        with col2:
            st.table(pd.DataFrame(column_data[len(column_data) // 2:]).set_index("Column Name"))


# Function to display file content
def display_file_content(token, path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        if isinstance(content, dict) and content.get('type') == 'file':
            file_content = requests.get(content['download_url']).content
            if path.lower().endswith(('.xlsx', '.xls')):
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
            elif path.lower().endswith('.csv'):
                try:
                    df = pd.read_csv(BytesIO(file_content))
                    st.dataframe(df)
                    show_column_data_types(df)
                    return df
                except EmptyDataError:
                    st.error("The CSV file is empty or improperly formatted.")
                except Exception as e:
                    st.error(f"An error occurred while reading the CSV file: {e}")
            elif path.lower().endswith(('.txt', '.md', '.dat')):
                try:
                    st.text(file_content.decode('utf-8'))
                except UnicodeDecodeError:
                    st.text(file_content.decode('latin-1'))
            elif path.lower().endswith(('.jpg', '.jpeg', '.png')):
                image = Image.open(BytesIO(file_content))
                st.image(image, caption=path.split('/')[-1])
            else:
                try:
                    st.text(file_content.decode('utf-8'))
                except UnicodeDecodeError:
                    st.warning("This file cannot be displayed as text.")
        else:
            st.error("Selected path is not a file.")
    else:
        st.error(f"Failed to retrieve file content (HTTP {response.status_code}).")
    return None


def _show_data_insights(df):
    """Show an expander with shape, missing values, and descriptive stats."""
    with st.expander("**Expand to view data insights**", expanded=False):
        if df is not None:
            st.write(f"**Shape:** {df.shape[0]} rows and {df.shape[1]} columns")
            missing_values = pd.DataFrame({
                "Column Name": df.columns,
                "Missing Values": df.isnull().sum().values
            })
            missing_values = missing_values[missing_values["Missing Values"] > 0]
            if not missing_values.empty:
                st.write("**Missing Values:**")
                num_columns = 4
                cols = st.columns(num_columns)
                for i, row in missing_values.iterrows():
                    with cols[i % num_columns]:
                        st.write(f"{row['Column Name']}: {row['Missing Values']}")
            else:
                st.write("**Missing Values:** There are no missing values in this sheet.")
            st.write("**Descriptive Analysis:**")
            st.dataframe(df.describe())
        else:
            st.warning("No data available to display insights.")


# Function to show the view data page
def show_view_data_page():
    st.title("📊 View Data")

    # Token handling: use session token if already set, otherwise prompt
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

    if not token:
        return

    st.write("**Select File**")

    # ── Phase 1: Trace selections stored in session state to build the list of
    #             dropdowns that need to be rendered, without rendering yet.
    dropdown_specs = []
    selected_file_path = None
    path_so_far = ""

    while True:
        contents = get_repo_contents(token, path_so_far)
        if contents is None:
            st.error("Failed to load folder contents. Please verify your token or try again.")
            break

        dirs = sorted(
            [item for item in contents
             if item['type'] == 'dir' and not (path_so_far == "" and item['name'].lower() == 'visualizations')],
            key=lambda x: x['name'].lower()
        )
        files = sorted(
            [item for item in contents if item['type'] == 'file'
             and item['name'].lower().endswith(SUPPORTED_EXTENSIONS)],
            key=lambda x: x['name'].lower()
        )

        dir_names = [d['name'] for d in dirs]
        file_names = [f['name'] for f in files]

        if not dir_names and not file_names:
            break

        options = ["-- Select --"] + dir_names + file_names
        nav_key = f"nav_{path_so_far or 'root'}"
        folder_label = path_so_far.split('/')[-1] if path_so_far else "Root"

        dropdown_specs.append({
            'key': nav_key,
            'label': f"📂 {folder_label}",
            'options': options,
            'dir_names': dir_names,
            'file_names': file_names,
        })

        # Read already-stored selection (won't block render — just reading state)
        current_val = st.session_state.get(nav_key, "-- Select --")
        if current_val not in (dir_names + file_names):
            break  # Nothing chosen yet at this level

        if current_val in file_names:
            selected_file_path = f"{path_so_far}/{current_val}" if path_so_far else current_val
            break  # File chosen — stop building dropdowns

        # Folder chosen — go one level deeper
        path_so_far = f"{path_so_far}/{current_val}" if path_so_far else current_val

    # ── Phase 2: Render all collected dropdowns in a 3-column grid,
    #             adding a new row every 3 levels of depth.
    for row_start in range(0, len(dropdown_specs), 3):
        row_specs = dropdown_specs[row_start:row_start + 3]
        cols = st.columns(3)
        for i, spec in enumerate(row_specs):
            with cols[i]:
                dn = spec['dir_names']

                def fmt(name, _dn=dn):
                    if name == "-- Select --":
                        return "-- Select --"
                    return f"📁 {name}" if name in _dn else f"📄 {name}"

                st.selectbox(
                    spec['label'],
                    spec['options'],
                    format_func=fmt,
                    key=spec['key']
                )

    # ── Phase 3: Display the selected file (if any).
    if selected_file_path:
        st.write("---")
        st.markdown(f"**📄 File:** `{selected_file_path.split('/')[-1]}`")
        st.write("**File Contents**")
        df = display_file_content(token, selected_file_path)
        _show_data_insights(df)
