import streamlit as st
import hashlib
import requests
import pandas as pd

def hash_file(file):
    #Generate a hash for the uploaded file to track duplicates
    hasher = hashlib.md5()
    hasher.update(file.getvalue())
    return hasher.hexdigest()

def main():
    st.set_page_config(page_title="Invoice Extraction using LangChain")
    st.title("Invoice Extraction Bot")

    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}  # Stores hash -> extracted data
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()  # Stores all extracted results

    # Upload the Invoices (PDF, XML, CSV files)
    uploaded_files = st.file_uploader(
        "Upload invoices here (PDF, XML only)",
        type=["pdf", "xml", "png", "jpeg"],
        accept_multiple_files=True
    )

    if uploaded_files:
        new_files = []
        for file in uploaded_files:
            file_hash = hash_file(file)
            if file_hash in st.session_state.processed_files:
                st.warning(f"Skipping already processed file: {file.name}")
            else:
                new_files.append((file_hash, file))

        #Enable button if there are new files to process
        submit = st.button("Extract Invoice", disabled=len(new_files) == 0)

        if submit and new_files:
            with st.spinner("Extracting..."):
                api_url = "http://localhost:8000/upload_file"

                #Prepare files for upload
                files = [("files", (file.name, file.getvalue(), file.type)) for _,file in new_files]

                response = requests.post(api_url, files=files)

                if response.status_code == 200:
                    try:
                        extracted_data = response.json()  # Parse JSON response
                        new_df = pd.DataFrame(extracted_data)  # Convert to DataFrame
                        if new_df.empty:
                            st.warning("Extraction failed")
                        #Store extracted results
                        else:
                            for (file_hash, file), data in zip(new_files, extracted_data):
                                st.session_state.processed_files[file_hash] = data

                            # Append new data to the existing DataFrame
                            st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                        
                            st.success(f"Extraction completed! {len(new_df)} new invoices processed.")

                    except Exception as e:
                        st.error(f"Failed to process response: {str(e)}")
                else:
                    st.error(f"Failed to upload files. Status Code: {response.status_code}")

    if not st.session_state.df.empty:
        with st.expander("View Extracted Data"):
            st.dataframe(st.session_state.df, use_container_width=True)

        # CSV Download Button
        data_as_csv = st.session_state.df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download data as CSV", 
            data_as_csv, 
            "extracted_invoices.csv",
            "text/csv",
            key="download-invoice-csv",
        )

if __name__ == "__main__":
    main()
