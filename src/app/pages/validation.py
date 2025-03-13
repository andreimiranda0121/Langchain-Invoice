import streamlit as st
import pandas as pd
from src.utils.helpers import hash_file
from src.services.api_requests import upload_files
from src.services.api_requests import save_to_db

# Function to reset session state when the company selection changes
def reset_data():
    st.session_state.processed_files = {}  
    st.session_state.po_processed_files = {}
    st.session_state.df_invoices = pd.DataFrame()  
    st.session_state.df_pos = pd.DataFrame()

def validation_page():
    
    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}  
    if "po_processed_files" not in st.session_state:
        st.session_state.po_processed_files = {}
    if "df_invoices" not in st.session_state:
        st.session_state.df_invoices = pd.DataFrame()  
    if "df_pos" not in st.session_state:
        st.session_state.df_pos = pd.DataFrame()  

    company_list = ["Company A", "Company B", "Company C"]
    st.selectbox(
        label="List of Company",
        options=company_list,
        key="company",
        on_change=reset_data  # 🔹 Reset data when a new company is selected
    )
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_files = st.file_uploader(
            "Upload invoices (PDF, XML, PNG, JPEG)", 
            type=["pdf", "xml", "png", "jpeg"], 
            accept_multiple_files=True
        )

    with col2:
        po_uploaded_files = st.file_uploader(
            "Upload PO (PDF, XML only)", 
            type=["pdf", "xml"], 
            accept_multiple_files=True
        )

    new_files, po_new_files = [], []

    if uploaded_files and po_uploaded_files:
        invoice_filenames, po_filenames = [], []

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

        file_data = {"invoice_files": invoice_filenames, "po_files": po_filenames}
    else:
        st.warning("Please upload both Invoice and PO files.")

    submit = st.button("Extract Data", disabled=not (new_files and po_new_files))
    
    if submit and new_files and po_new_files:
        with st.spinner("Extracting..."):
            response = upload_files(new_files, po_new_files, file_data, st.session_state.company)  # API call

            if response and "invoices" in response and "pos" in response:
                print(type(response["invoices"]))
                print(type(response["pos"]))
                df_invoices = pd.DataFrame(response["invoices"])
                df_pos = pd.DataFrame(response["pos"])

                if df_invoices.empty or df_pos.empty:
                    st.warning("Extraction failed or no valid data extracted.")
                else:
                    for (file_hash, _), data in zip(new_files, response["invoices"]):
                        st.session_state.processed_files[file_hash] = data
                    for (po_file_hash, _), data in zip(po_new_files, response["pos"]):
                        st.session_state.po_processed_files[po_file_hash] = data

                    st.session_state.df_invoices = pd.concat(
                        [st.session_state.df_invoices, df_invoices], ignore_index=True
                    )
                    st.session_state.df_pos = pd.concat(
                        [st.session_state.df_pos, df_pos], ignore_index=True
                    )

                    st.success(f"Extraction completed! {len(df_invoices)} invoices and {len(df_pos)} POs processed.")

                    invoice_numbers = set(st.session_state.df_invoices["invoice_no"].astype(str).str.replace(r"\D", "", regex=True))
                    po_numbers = set(st.session_state.df_pos["invoice_no"].astype(str).str.replace(r"\D", "", regex=True))

                    if not invoice_numbers.intersection(po_numbers):
                        st.warning("No matching Invoice numbers found between Invoices and POs!")
                    else:
                        st.success("Matching Invoice numbers found in both Invoices and POs!")

            else:
                st.error("Failed to process files.")

    if not st.session_state.df_invoices.empty:
        with st.expander("View Extracted Invoice Data"):
            st.dataframe(st.session_state.df_invoices, use_container_width=True)

    if not st.session_state.df_invoices.empty:
        data_as_csv = st.session_state.df_invoices.to_csv(index=False).encode("utf-8")
        st.download_button("Download Invoices as CSV", data_as_csv, "extracted_invoices.csv", "text/csv")

    if not st.session_state.df_pos.empty:
        with st.expander("View Extracted PO Data"):
            st.dataframe(st.session_state.df_pos, use_container_width=True)


    if not st.session_state.df_pos.empty:
        po_data_as_csv = st.session_state.df_pos.to_csv(index=False).encode("utf-8")
        st.download_button("Download POs as CSV", po_data_as_csv, "extracted_pos.csv", "text/csv")

    save = st.button(label="Save")

    if save:
        with st.spinner("Saving..."):
            if st.session_state.df_invoices.empty and st.session_state.df_pos.empty:
                st.warning("No data to save!")
            else:
                response = save_to_db(st.session_state.df_invoices, st.session_state.df_pos)
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


