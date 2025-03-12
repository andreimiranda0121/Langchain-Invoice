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

def extract_files(upload_files):
    try:
        API_URL = os.getenv("API_URL")
        
        # Fix: Correctly format files
        files = [("files", (file.name, file.file.read(), file.content_type)) for file in upload_files]

        response = requests.post(f"{API_URL}/extract_files/", files=files)
        
        print(f"Status Code: {response.status_code}")  # Debugging
        print(f"Response Text: {response.text}")  # Debugging

        if response.status_code == 200:
            extract_data = response.json()
            return {pd.DataFrame(extract_data)}
        else:
            print(f"Error: {response.text}")  # Print API error response
            return None
    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return None


def chat_request(query,session_id):
    try:
        API_URL = os.getenv("API_URL")

        response = requests.post(f"{API_URL}/chat/", 
                                 json={
                                     "query": query,
                                     "session_id": session_id
                                 }
                                 )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None
    

def save_to_db(df_invoices, df_pos):
    try:
        API_URL = os.getenv("API_URL")
        data = {
            "invoices": df_invoices.to_dict(orient="records"),
            "pos": df_pos.to_dict(orient="records")
        }
        response = requests.post(f"{API_URL}/save_to_db/", json=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to save data"}
    except Exception as e:
        return {"error": str(e)}