import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
            st.write("X-axis column")
            x_axis = st.selectbox("", columns, key="x_axis")
        
        with col2:
            st.write("Y-axis column")
            y_axis = st.selectbox("", columns, key="y_axis")
        
        with col3:
            st.write("Plot type")
            plot_type = st.selectbox("", ["Scatter Plot", "Line Plot", "Bar Plot", "Histogram"], key="plot_type")

        if st.button("Generate Plot"):
            plt.figure(figsize=(10, 6))
            if plot_type == "Scatter Plot":
                sns.scatterplot(data=df, x=x_axis, y=y_axis)
            elif plot_type == "Line Plot":
                sns.lineplot(data=df, x=x_axis, y=y_axis)
            elif plot_type == "Bar Plot":
                sns.barplot(data=df, x=x_axis, y=y_axis)
            elif plot_type == "Histogram":
                sns.histplot(data=df, x=x_axis, y=y_axis, bins=30)
            
            st.pyplot(plt)
