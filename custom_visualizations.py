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

def upload_to_github(file_content, path, token, message):
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
    response = requests.put(url, json=data, headers=headers)
    return response.status_code, response.json()

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
                
                if st.button("Upload Visualization"):
                    plot_name = st.text_input("Enter the name for the visualization")
                    plot_description = st.text_area("Enter the description for the visualization")
                    
                    if plot_name and plot_description:
                        # Save plot as image
                        img_buffer = BytesIO()
                        plt.savefig(img_buffer, format='png')
                        img_buffer.seek(0)
                        
                        # Save description in XML
                        root = ET.Element("Visualizations")
                        visualization = ET.SubElement(root, "Visualization")
                        ET.SubElement(visualization, "Name").text = plot_name
                        ET.SubElement(visualization, "Description").text = plot_description
                        tree = ET.ElementTree(root)
                        xml_buffer = BytesIO()
                        tree.write(xml_buffer, encoding='utf-8', xml_declaration=True)
                        xml_buffer.seek(0)
                        
                        github_token = st.text_input("Enter your GitHub token", type="password")
                        if github_token:
                            if st.button("Save"):
                                # Upload image
                                img_status, img_response = upload_to_github(img_buffer.read(), f"visualizations/{plot_name}.png", github_token, f"Upload visualization image: {plot_name}")
                                # Upload XML
                                xml_status, xml_response = upload_to_github(xml_buffer.read(), "visualizations/descriptions.xml", github_token, f"Upload visualization description: {plot_name}")
                                
                                if img_status == 201 and xml_status == 201:
                                    st.success("Visualization uploaded successfully!")
                                else:
                                    st.error("Failed to upload visualization.")
            except Exception as e:
                st.error(f"Error generating plot: {e}")

if __name__ == "__main__":
    show_custom_visualizations_page()
