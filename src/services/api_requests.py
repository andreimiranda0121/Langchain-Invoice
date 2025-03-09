import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def upload_files(new_files, po_new_files,file_data):
    try:
        API_URL = os.getenv("API_URL")
        files = [("invoices", (file.name, file.getvalue(), file.type)) for _, file in new_files]
        po_files = [("pos", (file.name, file.getvalue(), file.type)) for _, file in po_new_files]

        response = requests.post(f"{API_URL}/upload_files/", files=files + po_files, data=file_data)

        if response.status_code == 200:
            extracted_data = response.json()
            return {
                "invoices": pd.DataFrame(extracted_data.get("invoices", [])),
                "pos": pd.DataFrame(extracted_data.get("pos", []))
            }
        else:
            return None
    except Exception as e:
        return None
