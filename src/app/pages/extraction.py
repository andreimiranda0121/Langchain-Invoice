import streamlit as st
import pandas as pd
from src.utils.helpers import hash_file
from src.services.api_requests import extract_files, save_to_db

# Function to reset session state when the company selection changes
def reset_data():
    st.session_state.processed_files = {}  
    st.session_state.df_extracted = pd.DataFrame()

def extract_page():
    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    if "df_extracted" not in st.session_state:
        st.session_state.df_extracted = pd.DataFrame()
    
    company_list = ["Company A", "Company B", "Company C"]
    col1, col2 = st.columns(2)

    with col1:
        st.selectbox(
        label="List of Company",
        options=company_list,
        key="company",
        on_change=reset_data
        )

    with col2:
        extract_type = st.selectbox(label="Extract Invoice or PO", options=["invoice", "pos"], key="extract_type")

    uploaded_files = st.file_uploader(
        f"Upload {extract_type}s (PDF, XML)", 
        type=["pdf", "xml"], 
        accept_multiple_files=True
    )

    
    new_files = []
    if uploaded_files:
        filenames = []
        for file in uploaded_files:
            file_hash = hash_file(file)
            if file_hash in st.session_state.processed_files:
                st.warning(f"Skipping already processed file: {file.name}")
            else:
                new_files.append((file_hash, file))
                filenames.append(file.name)
    else:
        st.warning("Please upload a file")
    
    submit = st.button("Extract Data", disabled=not new_files)
    
    if submit and new_files:
        with st.spinner("Extracting data..."):  
            response = extract_files(new_files, st.session_state.company)
            if response:
                df_extracted = pd.DataFrame(response["response"])
                if df_extracted.empty:
                    st.warning("Extraction failed or no valid data extracted.")
                else:
                    for (file_hash, _), data in zip(new_files, response):
                        st.session_state.processed_files[file_hash] = data
                    
                    st.session_state.df_extracted = pd.concat(
                        [st.session_state.df_extracted, df_extracted], ignore_index=True
                    )
                    st.success(f"Extraction completed! {len(df_extracted)} {extract_type}(s) processed.")
            else:
                st.error("Failed to process files.")
    
    if not st.session_state.df_extracted.empty:
        with st.expander("View Extracted Data"):
            st.dataframe(st.session_state.df_extracted, use_container_width=True)
        
        data_as_csv = st.session_state.df_extracted.to_csv(index=False).encode("utf-8")
        st.download_button(f"Download Extracted {extract_type.capitalize()}s as CSV", data_as_csv, f"extracted_{extract_type}s.csv", "text/csv")
    
    save = st.button("Save")
    if save:
        with st.spinner("Saving..."):
            if st.session_state.df_extracted.empty:
                st.warning("No data to save!")
            else:
                # Separate invoices and POs based on extract_type
                invoices = st.session_state.df_extracted if extract_type == "invoice" else None
                pos = st.session_state.df_extracted if extract_type == "pos" else None

                response = save_to_db(invoices, pos)  # Pass both to FastAPI

                if "error" in response:
                    st.error(response["error"])
                else:
                    st.success(f"✅ {response['new_vectorized_invoices']} invoices saved, {response['new_vectorized_pos']} POs saved")

                    # Show warnings if duplicates exist
                    if response["duplicate_invoices"] > 0 or response["duplicate_pos"] > 0:
                        st.warning(
                            f"⚠️ {response['duplicate_invoices']} invoices and {response['duplicate_pos']} POs were duplicates and not saved."
                        )

                        # Display filenames of duplicate invoices
                        if response["duplicate_invoice_files"]:
                            st.write("📝 **Duplicate Invoice Files:**")
                            for filename in response["duplicate_invoice_files"]:
                                st.write(f"- {filename}")

                        # Display filenames of duplicate POs
                        if response["duplicate_pos_files"]:
                            st.write("📌 **Duplicate PO Files:**")
                            for filename in response["duplicate_pos_files"]:
                                st.write(f"- {filename}")
