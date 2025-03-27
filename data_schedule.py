import streamlit as st
import pandas as pd

def show_data_schedule_page():
    st.title("Data Schedule")
    
    # Define the data
    data = [
        ["Project Director", "Dr. Chuck Rice", "Kansas State University", "Soil Fertility", "", "", ""],
        ["GRA", "Cesar Guareschi", "Kansas State University", "Soil Fertility", "", "", ""],
        ["GRA", "Jessica Bezerradeoliveira", "Kansas State University", "Soil Fertility", "", "", ""],
        ["Objective Lead", "Dr. Romulo Lollato", "Kansas State University", "Cropping systems (wheat)", "", "", ""],
        ["", "Jazmin Gastaldi", "Kansas State University", "Filed Coordinator", "", "", ""],
        ["Objective Lead", "Dr. Brian Northup", "USDA-ARS Grazinglands Research Laboratory, El Reno, OK", "Cropping System", "", "", ""],
        ["Objective Lead", "Dr. Tyson Ochsner", "Oklahoma State University", "El Reno/Cronos Data", "", "", ""],
        ["GRA", "Cole Diggins", "Oklahoma State University", "El Reno/Cronos Data", "", "", ""],
        ["Objective Lead", "Dr. Ignacio Ciampitti", "Kansas State University", "Ashland/Summer Crops Data", "", "", ""],
        ["GRA", "Lucas Lingua", "Kansas State University", "Ashland/Summer Crops Data", "", "", ""],
        ["Objective Lead", "Dr. Jason Warren", "Oklahoma State University", "El Reno", "", "", ""],
        ["Objective Lead", "Dr. Beatrix Haggard", "Oklahoma State University", "El Reno", "", "", ""],
        ["GRA", "Sarah Mustain", "Oklahoma State University", "El Reno", "", "", ""],
        ["GRA", "Kayla Morrison", "Oklahoma State University", "El Reno", "", "", ""],
        ["Objective Lead", "Dr. Anita Dille", "Kansas State University", "Weed Science", "", "", ""],
        ["GRA", "Ethan Denson", "Kansas State University", "Weed Science", "", "", ""],
        ["Faculty", "Dr. Brian Arnall", "Oklahoma State University", "Precision Technologies & Nutrient Management", "", "", ""],
        ["Faculty", "Dr. Varaprasad Bandaru", "USDA Maricopa", "Nitrogen Forecasting, Recommendation Tool", "", "", ""],
        ["GRA", "Rohit Nandan", "USDA", "Nitrogen Forecasting, Recommendation Tool", "", "", ""],
        ["GRA", "Xiangjie Chen", "University of Maryland", "Nitrogen Forecasting, Recommendation Tool", "", "", ""],
        ["Faculty", "Dr. Robert Chambers", "University of Maryland", "Perkins", "", "", ""],
        ["GRA", "Xiangjie Chen", "University of Maryland", "Perkins", "", "", ""],
        ["Faculty", "Dr. Curtis Jones", "University of Maryland", "Perkins", "", "", ""],
        ["GRA", "Xiangjie Chen", "University of Maryland", "Perkins", "", "", ""],
        ["Faculty", "Dr. Dayton Lambert", "Oklahoma State University", "El Reno", "", "", ""],
        ["GRA", "Enoch Adom", "Oklahoma State University", "El Reno", "", "", ""],
        ["Faculty", "Dr. Lixia Lambert", "Oklahoma State University", "El Reno", "", "", ""],
        ["Faculty", "Dr. Josh Lofton", "Oklahoma State University", "El Reno", "", "", ""],
        ["Faculty", "Dr. Doohong Min", "Kansas State University", "Ashland/Forage Data", "", "", ""],
        ["GRA", "Jiyung Kim", "Kansas State University", "Ashland/Forage Data", "", "", ""],
        ["Faculty", "Dr. Andres Patrignani", "Kansas State University", "Ashland/Soil Moisture", "", "", ""],
        ["GRA", "Sofia Cominelli", "Kansas State University", "Ashland/Soil Moisture", "", "", ""],
        ["Faculty", "Dr. Vara Prasad", "Kansas State University", "Ashland/Cropping Systems", "", "", ""],
        ["GRA", "Muazzamma Mushtaq", "Kansas State University", "Ashland/Cropping Systems", "", "", ""],
        ["Faculty", "Dr. Alexandre Caldeira Rocateli", "Oklahoma State University", "Biomass, soilwater, plant height", "", "", ""],
        ["Faculty", "Dorivar Diaz", "Kansas State University", "Ashland/Soil Fertility", "", "", ""],
        ["GRA", "Paula Garcia Helguera", "Kansas State University", "Ashland/Soil Fertility", "", "", ""],
        ["Faculty", "Dr. Eduardo Santos", "Kansas State University", "Micrometeorology", "", "", ""],
        ["GRA", "Sudipti Parajuli", "Kansas State University", "Micrometeorology", "", "", ""],
        ["Faculty", "Dr. Pradeep Wagle", "El Reno", "ElReno/Field Data", "", "", ""],
        ["Faculty", "Dr. Travis Witt", "El Reno", "ElReno/Field Data", "", "", ""],
        ["GRA", "Jeff Weik", "USDA", "ElReno/Field Data", "", "", ""],
        ["Technician", "Ana Grimaldo Valezquez", "Oklahoma State University", "ElReno/Field Data", "", "", ""]
    ]
    
    # Define the columns
    columns = ["Position", "Name", "Institution", "Research Area", "Start Date", "End Date", "Data Received Date"]
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    # Display the table
    st.table(df)
