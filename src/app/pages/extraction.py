from src.utils.helpers import hash_file
import streamlit as st
import pandas as pd

def extract_page():

    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}  
    if "df_invoices" not in st.session_state:
        st.session_state.df_invoices = pd.DataFrame()  
    
    company_list = ["Company A", "Company B", "Company C"]
    st.selectbox(label="List of Company",options=company_list, key="company")