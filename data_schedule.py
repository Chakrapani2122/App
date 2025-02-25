import streamlit as st
import pandas as pd

def show_data_schedule_page():
    st.title("Data Schedule (Draft)")
    
    # Create a dataframe with the specified columns
    data = {
        "Research Area": ["Microbial Ecology", "Soil Health Indicators", "Rhizosphere Microbes"],
        "Professor": ["Dr. Charles Rice", "Dr. Charles Rice", "Dr. Charles Rice"],
        "Research Assistant": ["John Doe", "Jane Smith", "Alice Johnson"],
        "Start Date": ["2023-01-01", "2023-02-01", "2023-03-01"],
        "End Date": ["2023-06-01", "2023-07-01", "2023-08-01"],
        "Received Date": ["2023-01-15", "2023-02-15", "2023-03-15"],
        "Status": ["Ongoing", "Ongoing", "Upcoming"]
    }
    
    df = pd.DataFrame(data)
    
    # Display the dataframe
    st.write(df)
