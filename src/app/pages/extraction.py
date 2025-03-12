import sys
import os
from src.utils.helpers import hash_file
import streamlit as st
import pandas as pd
from src.services.api_requests import extract_files

def extract_page():
    # Initialize session state variables
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}  
    if "df_invoices" not in st.session_state:
        st.session_state.df_invoices = pd.DataFrame()  
    if "df_pos" not in st.session_state:
        st.session_state.df_pos = pd.DataFrame()

    company_list = ["Company A", "Company B", "Company C"]
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(label="List of Company", options=company_list, key="company")
    with col2:
        st.selectbox(label="Extract Invoice or PO", options=["invoices", "pos"], key="invoices")

    upload_files = st.file_uploader("Upload invoices (PDF, XML)", type=["pdf", "xml"], accept_multiple_files=True)

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
        st.warning("Please upload a file")

    submit = st.button("Extract")

    if submit and invoice_files:
        st.write("Processing extraction...")
        with st.spinner("Extracting data..."):
            try:
                response = extract_files([file for _, file in invoice_files])  # Pass only files

                if response is None:
                    st.error("Extraction failed: No response from API.")
                    return
                
                extracted_data = response.to_dict(orient="records")  # Convert DataFrame to dict

                if not extracted_data:
                    st.warning("Extraction failed: No data extracted.")
                else:
                    # Store extracted results
                    for (file_hash, file), data in zip(invoice_files, extracted_data):
                        st.session_state.processed_files[file_hash] = data

                    # Append new data to the existing DataFrame
                    st.session_state.df_invoices = pd.concat(
                        [st.session_state.df_invoices, response], ignore_index=True
                    )

                    st.success(f"Extraction completed! {len(response)} new invoices processed.")
                    st.dataframe(st.session_state.df_invoices)  # Display extracted data

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                print("Error:", str(e))  # Debugging in console
