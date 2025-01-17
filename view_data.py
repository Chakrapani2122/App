import streamlit as st
import requests

def get_onedrive_files(folder_link):
    # Extract the folder ID from the OneDrive link
    folder_id = folder_link.split('/')[-1]
    api_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children"
    headers = {
        "Authorization": f"Bearer {st.secrets['onedrive_token']}"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        st.error("Failed to fetch files from OneDrive.")
        return []

def show_view_data_page():
    st.title("View Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Ashland")
        ashland_options = ["Forage", "Soil Biology & Biochemistry", "Soil Fertility", "Soil Health", "Soil Moisture", "Summer Crops", "Winter Crops", "Soil Water Lab"]
        ashland_selection = st.selectbox("Select a category", [""] + ashland_options, key="ashland")

    with col2:
        st.subheader("El Reno")
        el_reno_options = ["Archive", "Cronos Data", "Field data"]
        el_reno_selection = st.selectbox("Select a category", [""] + el_reno_options, key="el_reno")

    with col3:
        st.subheader("Perkins")
        perkins_options = ["Plant Height - Soil Moisture"]
        perkins_selection = st.selectbox("Select a category", [""] + perkins_options, key="perkins")

    st.write("---")

    if ashland_selection and not el_reno_selection and not perkins_selection:
        category = ashland_selection
    elif el_reno_selection and not ashland_selection and not perkins_selection:
        category = el_reno_selection
    elif perkins_selection and not ashland_selection and not el_reno_selection:
        category = perkins_selection
    else:
        st.warning("Please select a category from only one dropdown.")
        return

    folder_link = st.text_input("Enter OneDrive folder link")
    if folder_link:
        files = get_onedrive_files(folder_link)
        if files:
            subdirectories = [file['name'] for file in files if file['folder']]
            selected_subdirectory = st.selectbox("Select a subdirectory", subdirectories)
            if selected_subdirectory:
                subdirectory_files = get_onedrive_files(f"{folder_link}/{selected_subdirectory}")
                file_names = [file['name'] for file in subdirectory_files if not file['folder']]
                selected_file = st.selectbox("Select a file", file_names)
                if selected_file:
                    file_content = next(file['@microsoft.graph.downloadUrl'] for file in subdirectory_files if file['name'] == selected_file)
                    response = requests.get(file_content)
                    if response.status_code == 200:
                        st.text_area("File Content", response.text, height=300, max_chars=None, key=None)
                    else:
                        st.error("Failed to fetch file content.")
