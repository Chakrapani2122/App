import pandas as pd
from PIL import Image
import streamlit as st

from github_utils import (
    GITHUB_REPO,
    clear_github_caches,
    get_file_metadata,
    get_repo_contents,
    upload_bytes_to_github,
    validate_token,
)

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

def _folder_nav_grid(token, nav_prefix, exclude_root=None):
    dropdown_specs = []
    path_so_far = ""

    while True:
        contents = get_repo_contents(token, path_so_far)
        if not contents:
            break

        excluded = {name.lower() for name in (exclude_root or [])}
        dirs = sorted(
            [
                item for item in contents
                if item['type'] == 'dir'
                and not (path_so_far == "" and item['name'].lower() in excluded)
            ],
            key=lambda x: x['name'].lower()
        )
        dir_names = [d['name'] for d in dirs]
        if not dir_names:
            break

        options = ["-- Select --"] + dir_names
        nav_key = f"{nav_prefix}_{path_so_far or 'root'}"
        folder_label = path_so_far.split('/')[-1] if path_so_far else "Root"

        dropdown_specs.append({
            'key': nav_key,
            'label': f"📂 {folder_label}",
            'options': options,
        })

        current_val = st.session_state.get(nav_key, "-- Select --")
        if current_val not in dir_names:
            break

        path_so_far = f"{path_so_far}/{current_val}" if path_so_far else current_val

    for row_start in range(0, len(dropdown_specs), 3):
        row_specs = dropdown_specs[row_start:row_start + 3]
        cols = st.columns(3)
        for i, spec in enumerate(row_specs):
            with cols[i]:
                st.selectbox(spec['label'], spec['options'], key=spec['key'])

    return path_so_far


def _preview_uploaded_file(uploaded_file, selected_sheet=None):
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".xlsx"):
        workbook = pd.ExcelFile(uploaded_file)
        df = pd.read_excel(workbook, sheet_name=selected_sheet)
        st.dataframe(df.head(100), use_container_width=True)
        show_column_data_types(df)
        return
    if file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head(100), use_container_width=True)
        show_column_data_types(df)
        return
    if file_name.endswith((".txt", ".dat")):
        st.text_area(
            "Read-only preview",
            uploaded_file.getvalue().decode("utf-8", errors="replace"),
            height=300,
            disabled=True,
            key=f"upload_preview_{uploaded_file.name}",
        )
        return
    if file_name.endswith((".jpg", ".png")):
        st.image(Image.open(uploaded_file), caption=uploaded_file.name)
        return
    st.warning(f"Cannot preview {uploaded_file.name}.")


def show_upload_page():
    st.title("Upload Files")
    
    github_token = st.session_state.get('github_token')
    if not github_token:
        input_token = st.text_input("**Enter your security token**", type="password")
        if input_token:
            if validate_token(input_token):
                st.success("Token validated and saved for this session.")
                st.session_state['github_token'] = input_token
                github_token = input_token
            else:
                st.error(f"Invalid token or insufficient permissions for {GITHUB_REPO}.")
    
    uploaded_files = st.file_uploader("**Choose files**", type=["xlsx", "csv", "txt", "dat", "jpg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        uploaded_file_names = [uploaded_file.name for uploaded_file in uploaded_files]
        if len(uploaded_file_names) != len(set(uploaded_file_names)):
            st.warning("Duplicate files detected. Please remove duplicate files before uploading.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                selected_file = st.selectbox("Select a file", uploaded_file_names, label_visibility="collapsed")
            with col2:
                selected_sheet = None
                selected_upload = next((item for item in uploaded_files if item.name == selected_file), None)
                if selected_upload and selected_upload.name.lower().endswith(".xlsx"):
                    workbook = pd.ExcelFile(selected_upload)
                    selected_sheet = st.selectbox("Select a sheet", workbook.sheet_names, label_visibility="collapsed")

            st.write("**Showing First 100 Rows:**")
            with st.expander("Expand to view the first 100 rows", expanded=True):
                if selected_upload is not None:
                    selected_upload.seek(0)
                    try:
                        _preview_uploaded_file(selected_upload, selected_sheet)
                    except Exception as e:
                        st.warning(f"Cannot display content of {selected_upload.name} (error: {e}).")

            st.write("**📂 Select destination folder**")
            dest_folder = _folder_nav_grid(github_token, "up_nav", exclude_root=["visualizations"])

            if dest_folder:
                upload_status = st.empty()

                if st.button("Upload"):
                    if github_token:
                        file_statuses = []
                        for uploaded_file in uploaded_files:
                            file_name = uploaded_file.name
                            path = f"{dest_folder}/{file_name}"
                            if get_file_metadata(github_token, path):
                                file_statuses.append(f"File '{file_name}' already exists at path: {path}")
                                continue

                            uploaded_file.seek(0)
                            status_code, response = upload_bytes_to_github(
                                uploaded_file.read(),
                                path,
                                github_token,
                                f"Upload {path}",
                            )
                            if status_code == 201:
                                file_statuses.append(f"File '{file_name}' uploaded successfully!")
                            else:
                                file_statuses.append(f"Failed to upload file '{file_name}'. Error: {response}")

                        clear_github_caches()
                        for status in file_statuses:
                            upload_status.write(status)
                    else:
                        upload_status.error("Security token is required to upload files.")

if __name__ == "__main__":
    show_upload_page()
