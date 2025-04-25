import streamlit as st
import pandas as pd

def show_data_schedule_page():
    st.title("📅 Data Schedule")
    
    # Read the Excel file
    excel_file = "research_team_data.xlsx"
    df_from_excel = pd.read_excel(excel_file)
    
    # Display the table
    st.table(df_from_excel)
