import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import requests
import xml.etree.ElementTree as ET
from io import BytesIO
from pandas.errors import EmptyDataError

# GitHub repository details
GITHUB_REPO = "Chakrapani2122/Data"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"

def upload_to_github(file_content, path, token, message, sha=None):
    url = GITHUB_API_URL + path
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    content = base64.b64encode(file_content).decode("utf-8")
    
    data = {
        "message": message,
        "content": content
    }
    if sha:
        data["sha"] = sha

    response = requests.put(url, json=data, headers=headers)
    return response.status_code, response.json()

def get_file_sha(path, token):
    url = GITHUB_API_URL + path
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["sha"]
    return None

def validate_xml(xml_content):
    try:
        ET.fromstring(xml_content)
        return True
    except ET.ParseError:
        return False

@st.cache_data(ttl=300)
def get_repo_contents(token, path=""):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def display_file_content(token, path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
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
                except ValueError:
                    st.error("The .xlsx file appears to be invalid or corrupted.")
                except Exception as e:
                    st.error(f"An error occurred while reading the Excel file: {e}")
            elif path.endswith('.csv'):
                try:
                    df = pd.read_csv(BytesIO(file_content))
                except EmptyDataError:
                    st.error("The CSV file is empty or improperly formatted.")
                except Exception as e:
                    st.error(f"An error occurred while reading the CSV file: {e}")
            else:
                st.error("Unsupported file format.")
            return df
        else:
            st.error("Selected path is not a file.")
    else:
        st.error("Failed to retrieve file content.")
    return None

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

def show_custom_visualizations_page(github_token: str | None = None, show_header: bool = True):
    # Optionally render header/subtitle when used as a standalone page
    if show_header:
        st.title("🎨 Custom Visualizations")
        st.markdown("**Visualize your data and save the visualization to allow others to view it.**")

    # If token wasn't provided, try to read from session state
    if not github_token:
        github_token = st.session_state.get('github_token')
    # If still no token and header is shown, prompt for it here and validate/persist
    if not github_token and show_header:
        input_token = st.text_input("**Enter security token**", type="password", key="custom_viz_token_input")
        if input_token:
            headers = {"Authorization": f"token {input_token}"}
            test = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}", headers=headers)
            if test.status_code == 200:
                st.success("Token validated and saved for this session.")
                st.session_state['github_token'] = input_token
                github_token = input_token
            else:
                st.error("Invalid token or insufficient permissions.")
    df = None
    if github_token:
        st.write("**Select a file from the repository or upload a new file**")
        option = st.radio("Choose an option", ["Select from repository", "Upload new file"], key="file_option")

        if option == "Select from repository":
            research_areas = get_repo_contents(github_token)
            research_area_names = [area['name'] for area in research_areas if area['type'] == 'dir' and area['name'] != 'visualizations']

            col1, col2, col3 = st.columns(3)
            with col1:
                selected_research_area = st.selectbox("Select Research Area", research_area_names, key="research_area_select")

            if selected_research_area:
                selected_area_contents = get_repo_contents(github_token, selected_research_area)
                folder_names = [folder['name'] for folder in selected_area_contents if folder['type'] == 'dir']

                with col2:
                    selected_data_folder = st.selectbox("Select Research Data Folder", folder_names, key="data_folder_select")

                if selected_data_folder:
                    selected_folder_contents = get_repo_contents(github_token, f"{selected_research_area}/{selected_data_folder}")
                    file_names = [file['name'] for file in selected_folder_contents if file['type'] == 'file' and file['name'].lower().endswith(('.xlsx', '.csv'))]

                    with col3:
                        selected_file = st.selectbox("Select a file", file_names, key="file_select")

                    if selected_file:
                        file_path = f"{selected_research_area}/{selected_data_folder}/{selected_file}"
                        st.write("**File Contents**")
                        df = display_file_content(github_token, file_path)
                        with st.expander("**Data Preview**", expanded=False):
                            st.dataframe(df)
                    else:
                        st.info("Please select a file to start building visualizations.")
        else:
            uploaded_file = st.file_uploader("**Choose a CSV or Excel file**", type=["csv", "xlsx"])
            if uploaded_file is not None:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(".xlsx"):
                    xls = pd.ExcelFile(uploaded_file)
                    sheet_name = st.selectbox("**Select a sheet**", xls.sheet_names)
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                st.write("**Data Preview: First 100 Observations**")
                st.dataframe(df.head(100))
                st.write("---")

        if df is not None:
            # Display data types of each column
            show_column_data_types(df)
            st.write("---")

            columns = df.columns.tolist()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**X-axis columns**")
                x_axis = st.multiselect("Select X-axis columns", columns, key="x_axis")
            
            with col2:
                st.write("**Y-axis columns**")
                y_axis = st.multiselect("Select Y-axis columns", columns, key="y_axis")
            
            with col3:
                st.write("**Plot type**")
                plot_type = st.selectbox("Select Plot Type", [
                    "Scatter Plot", "Line Plot", "Bar Plot", "Histogram", "Box Plot", "Violin Plot",
                    "Heatmap", "Pair Plot", "Regression Plot", "Density Plot", "Swarm Plot"
                ], key="plot_type")

            if st.button("Generate Plot"):
                plt.figure(figsize=(10, 6))
                try:
                    if plot_type == "Scatter Plot":
                        for y in y_axis:
                            sns.scatterplot(data=df, x=x_axis[0], y=y, label=y)
                        plt.legend()
                    elif plot_type == "Line Plot":
                        for y in y_axis:
                            sns.lineplot(data=df, x=x_axis[0], y=y, label=y)
                        plt.legend()
                    elif plot_type == "Bar Plot":
                        for y in y_axis:
                            sns.barplot(data=df, x=x_axis[0], y=y, label=y)
                        plt.legend()
                    elif plot_type == "Histogram":
                        for y in y_axis:
                            sns.histplot(data=df, x=x_axis[0], y=y, bins=30, label=y)
                        plt.legend()
                    elif plot_type == "Box Plot":
                        sns.boxplot(data=df, x=x_axis[0], y=y_axis)
                        plt.legend()
                    elif plot_type == "Violin Plot":
                        sns.violinplot(data=df, x=x_axis[0], y=y_axis)
                        plt.legend()
                    elif plot_type == "Heatmap":
                        sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
                        plt.legend()
                    elif plot_type == "Pair Plot":
                        sns.pairplot(df)
                        plt.legend()
                    elif plot_type == "Regression Plot":
                        for y in y_axis:
                            sns.regplot(data=df, x=x_axis[0], y=y)
                        plt.legend()
                    elif plot_type == "Density Plot":
                        sns.kdeplot(data=df, x=x_axis[0], hue=y_axis[0], fill=True)
                        plt.legend()
                    elif plot_type == "Swarm Plot":
                        sns.swarmplot(data=df, x=x_axis[0], y=y_axis)
                        plt.legend()

                    plt.xlabel(", ".join(x_axis))
                    plt.ylabel(", ".join(y_axis))
                    plt.legend()
                    plt.title(f"{plot_type} of {', '.join(y_axis)} vs {', '.join(x_axis)}")
                    st.pyplot(plt)

                    # Save the plot to session state
                    img_buffer = BytesIO()
                    plt.savefig(img_buffer, format='png')
                    img_buffer.seek(0)
                    st.session_state['plot_image'] = img_buffer

                except Exception as e:
                    st.error(f"Error generating plot: {e}")

            if 'plot_image' in st.session_state:
                st.image(st.session_state['plot_image'].getvalue(), caption="Generated Plot")

                plot_name = st.text_input("**Enter the name for the visualization**")
                plot_description = st.text_area("**Enter the description for the visualization**")
                
                if plot_name and plot_description:
                    # Save description in XML
                    visualization = ET.Element("Visualization")
                    ET.SubElement(visualization, "Name").text = plot_name
                    ET.SubElement(visualization, "Description").text = plot_description
                    
                    if st.button("Save"):
                        # Upload image
                        img_status, img_response = upload_to_github(st.session_state['plot_image'].getvalue(), f"visualizations/{plot_name}.png", github_token, f"Upload visualization image: {plot_name}")
                        
                        # Check if descriptions.xml exists
                        xml_sha = get_file_sha("visualizations/descriptions.xml", github_token)
                        if xml_sha:
                            # Download existing XML
                            xml_url = GITHUB_API_URL + "visualizations/descriptions.xml"
                            xml_headers = {"Authorization": f"token {github_token}"}
                            xml_response = requests.get(xml_url, headers=xml_headers)
                            if xml_response.status_code == 200:
                                try:
                                    xml_content_base64 = xml_response.json()['content']
                                    xml_content = base64.b64decode(xml_content_base64).decode('utf-8')
                                    existing_tree = ET.ElementTree(ET.fromstring(xml_content))
                                    existing_root = existing_tree.getroot()
                                    existing_root.append(visualization)
                                    xml_buffer = BytesIO()
                                    existing_tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
                                    xml_buffer.seek(0)
                                except (ET.ParseError, KeyError, base64.binascii.Error) as e:
                                    st.error(f"Error parsing XML: {e}")
                                    st.text(xml_content)  # Display the problematic XML content for debugging
                                    return
                        else:
                            # Create new XML
                            root = ET.Element("Visualizations")
                            root.append(visualization)
                            tree = ET.ElementTree(root)
                            xml_buffer = BytesIO()
                            tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
                            xml_buffer.seek(0)
                        
                        # Validate XML
                        xml_content = xml_buffer.getvalue().decode('utf-8')
                        if validate_xml(xml_content):
                            # Upload XML
                            xml_status, xml_response = upload_to_github(xml_buffer.read(), "visualizations/descriptions.xml", github_token, f"Upload visualization description: {plot_name}", sha=xml_sha)
                            
                            if img_status == 201 and xml_status in [200, 201]:
                                st.success("Visualization uploaded successfully!")
                            else:
                                st.error("Failed to upload visualization.")
                        else:
                            st.error("Invalid XML format.")
        else:
            st.info("Please select a file to start building visualizations.")

if __name__ == "__main__":
    show_custom_visualizations_page()
