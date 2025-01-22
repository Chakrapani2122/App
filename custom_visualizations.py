import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import requests
import xml.etree.ElementTree as ET
from io import BytesIO

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

def show_custom_visualizations_page():
    st.title("Custom Visualizations")
    st.write("Upload a CSV or Excel file to visualize the data using Matplotlib and Seaborn.")

    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            xls = pd.ExcelFile(uploaded_file)
            sheet_name = st.selectbox("Select a sheet", xls.sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        
        st.write("Data Preview:")
        st.dataframe(df.head())

        columns = df.columns.tolist()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("X-axis columns")
            x_axis = st.multiselect("Select X-axis columns", columns, key="x_axis")
        
        with col2:
            st.write("Y-axis columns")
            y_axis = st.multiselect("Select Y-axis columns", columns, key="y_axis")
        
        with col3:
            st.write("Plot type")
            plot_type = st.selectbox("Select Plot Type", ["Scatter Plot", "Line Plot", "Bar Plot", "Histogram", "Box Plot", "Violin Plot"], key="plot_type")

        if st.button("Generate Plot"):
            plt.figure(figsize=(10, 6))
            try:
                if plot_type == "Scatter Plot":
                    for y in y_axis:
                        sns.scatterplot(data=df, x=x_axis[0], y=y, label=y)
                elif plot_type == "Line Plot":
                    for y in y_axis:
                        sns.lineplot(data=df, x=x_axis[0], y=y, label=y)
                elif plot_type == "Bar Plot":
                    for y in y_axis:
                        sns.barplot(data=df, x=x_axis[0], y=y, label=y)
                elif plot_type == "Histogram":
                    for y in y_axis:
                        sns.histplot(data=df, x=x_axis[0], y=y, bins=30, label=y)
                elif plot_type == "Box Plot":
                    sns.boxplot(data=df, x=x_axis[0], y=y_axis)
                elif plot_type == "Violin Plot":
                    sns.violinplot(data=df, x=x_axis[0], y=y_axis)
                
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

            plot_name = st.text_input("Enter the name for the visualization")
            plot_description = st.text_area("Enter the description for the visualization")
            
            if plot_name and plot_description:
                # Save description in XML
                visualization = ET.Element("Visualization")
                ET.SubElement(visualization, "Name").text = plot_name
                ET.SubElement(visualization, "Description").text = plot_description
                
                github_token = st.text_input("Enter your GitHub token", type="password")
                if github_token:
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

if __name__ == "__main__":
    show_custom_visualizations_page()
