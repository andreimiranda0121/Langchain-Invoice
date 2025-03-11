from src.utils.helpers import hash_file
import streamlit as st
import pandas as pd

def extract_page():

    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}  
    if "df_invoices" not in st.session_state:
        st.session_state.df_invoices = pd.DataFrame()  
    if "df_pos" not in st.session_state:
        st.session_state.df_pos = pd.DataFrame()

    company_list = ["Company A", "Company B", "Company C"]
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(label="List of Company",options=company_list, key="company")
    with col2:
        st.selectbox(label="Extract Invoice or PO", options=["invoices", "pos"], key="invoices")

    upload_files = st.file_uploader("Upload invoices (PDF, XML", type=["pdf","xml"],accept_multiple_files=True)
    
    invoice_files = []

    if upload_files:
        filename = []
        for file in upload_files:
            file_hash = hash_file(file)
            if file_hash in st.session_state.processed_files:
                st.warning(f"Skipping already processed file: {file.name}")
            else:
                invoice_files.append((file_hash, file))
                filename.append(file.name)
    else:
        st.warning("Please upload a files")

    submit = st.button("Extract")

    if submit:
        with st.spinner("Processing..."):
            st.write("test")