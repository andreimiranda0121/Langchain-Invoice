import streamlit as st
import hashlib
import requests
import pandas as pd

def hash_file(file):
    """Generate a hash for the uploaded file to track duplicates"""
    hasher = hashlib.md5()
    hasher.update(file.getvalue())
    return hasher.hexdigest()

def main():
    st.set_page_config(page_title="Invoice and PO Extraction using LangChain")
    st.title("Invoice and PO Extraction Bot")

    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}  # Stores hash -> extracted data
    if "po_processed_files" not in st.session_state:
        st.session_state.po_processed_files = {}
    if "df_invoices" not in st.session_state:
        st.session_state.df_invoices = pd.DataFrame()  # Stores extracted invoices
    if "df_pos" not in st.session_state:
        st.session_state.df_pos = pd.DataFrame()  # Stores extracted PO data

    col1, col2 = st.columns(2)
    
    # Upload the Invoices (PDF, XML, PNG, JPEG files)
    with col1:
        uploaded_files = st.file_uploader(
            "Upload invoices here (PDF, XML, PNG, JPEG only)",
            type=["pdf", "xml", "png", "jpeg"],
            accept_multiple_files=True
        )
    
    with col2:
        po_uploaded_files = st.file_uploader(
            "Upload PO here (PDF, XML only)",
            type=["pdf", "xml"],
            accept_multiple_files=True
        )

    new_files = []
    po_new_files = []
    
    if uploaded_files and po_uploaded_files:
        invoice_filenames = []
        po_filenames = []

        for file in uploaded_files:
            file_hash = hash_file(file)
            if file_hash in st.session_state.processed_files:
                st.warning(f"Skipping already processed file: {file.name}")
            else:
                new_files.append((file_hash, file))
                invoice_filenames.append(file.name)

        for file in po_uploaded_files:
            po_file_hash = hash_file(file)
            if po_file_hash in st.session_state.po_processed_files:
                st.warning(f"Skipping already processed PO file: {file.name}")
            else:
                po_new_files.append((po_file_hash, file))
                po_filenames.append(file.name)

        file_data = {
            "invoice_files": invoice_filenames,
            "po_files": po_filenames
        }
    
    else:
        st.warning("Please upload both Invoice and PO files.")
    
    # Enable button if there are new files to process
    submit = st.button("Extract Data", disabled=len(new_files) == 0 or len(po_new_files) == 0)
    
    if submit and new_files and po_new_files:
        with st.spinner("Extracting..."):
            api_url = "http://localhost:8000/upload_files"

            # Prepare files for upload (both invoices and POs)
            files = [("invoices", (file.name, file.getvalue(), file.type)) for _, file in new_files]
            po_files = [("pos", (file.name, file.getvalue(), file.type)) for _, file in po_new_files]

            response = requests.post(api_url, files=files + po_files, data=file_data)

            if response.status_code == 200:
                try:
                    extracted_data = response.json()  # Parse JSON response
                    invoices_data = extracted_data.get("invoices", [])
                    pos_data = extracted_data.get("pos", [])

                    df_invoices = pd.DataFrame(invoices_data)
                    df_pos = pd.DataFrame(pos_data)
                    
                    if df_invoices.empty or df_pos.empty:
                        st.warning("Extraction failed or no valid data extracted.")
                    else:
                        # Store extracted results
                        for (file_hash, file), data in zip(new_files, invoices_data):
                            st.session_state.processed_files[file_hash] = data
                        for (po_file_hash, file), data in zip(po_new_files, pos_data):
                            st.session_state.po_processed_files[po_file_hash] = data
                        
                        # Append new data to the existing DataFrames
                        st.session_state.df_invoices = pd.concat([st.session_state.df_invoices, df_invoices], ignore_index=True)
                        st.session_state.df_pos = pd.concat([st.session_state.df_pos, df_pos], ignore_index=True)
                        
                        st.success(f"Extraction completed! {len(df_invoices)} invoices and {len(df_pos)} POs processed.")
                        
                        # Validate matching Invoice numbers in PO and Invoices
                        invoice_numbers = set(st.session_state.df_invoices["invoice_no"].astype(str).str.replace(r"\D", "", regex=True))
                        po_numbers = set(st.session_state.df_pos["invoice_no"].astype(str).str.replace(r"\D", "", regex=True))

                        if not invoice_numbers.intersection(po_numbers):
                            st.warning("No matching Invoice numbers found between Invoices and POs!")
                        else:
                            st.success("Matching Invoice numbers found in both Invoices and POs!")

                except Exception as e:
                    st.error(f"Failed to process response: {str(e)}")
            else:
                st.error(f"Failed to upload files. Status Code: {response.status_code}")
    
    if not st.session_state.df_invoices.empty:
        with st.expander("View Extracted Invoice Data"):
            st.dataframe(st.session_state.df_invoices, use_container_width=True)

    if not st.session_state.df_pos.empty:
        with st.expander("View Extracted PO Data"):
            st.dataframe(st.session_state.df_pos, use_container_width=True)

    # CSV Download Buttons
    if not st.session_state.df_invoices.empty:
        data_as_csv = st.session_state.df_invoices.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Invoices as CSV", 
            data_as_csv, 
            "extracted_invoices.csv",
            "text/csv",
            key="download-invoice-csv",
        )
    
    if not st.session_state.df_pos.empty:
        po_data_as_csv = st.session_state.df_pos.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download POs as CSV", 
            po_data_as_csv, 
            "extracted_pos.csv",
            "text/csv",
            key="download-po-csv",
        )

if __name__ == "__main__":
    main()
