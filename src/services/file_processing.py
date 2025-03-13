import io
import pandas as pd
import re
import json
import xml.etree.ElementTree as ET
from pypdf import PdfReader
from PIL import Image
from .chain import Chaining
from src.utils.dataframe import DataFrame
from src.utils.schema import Schema  # Import schema dynamically
import numpy as np

class FilePipeline:
    def __init__(self):
        self.chain = Chaining()

    def get_pdf_text(self, pdf_bytes):
        text = ""
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))  
        for page in pdf_reader.pages:
            text += page.extract_text() or "" 
        return text

    def extract_text_from_xml(self, file_bytes):
        try:
            tree = ET.ElementTree(ET.fromstring(file_bytes.decode("utf-8")))
            root = tree.getroot()
            xml_dict = {elem.tag: elem.text.strip() if elem.text else "" for elem in root.iter()}
            return json.dumps(xml_dict)  # Convert to JSON for structured processing
        except ET.ParseError as e:
            print(f"XML Parsing Error: {e}")
            return "{}"

    def extract_text_from_image(self, file_bytes):
        image = Image.open(io.BytesIO(file_bytes))
        text = image  # Replace this with OCR processing if needed
        return text

    def clean_number(self, value):
        if not value or str(value).strip() == "":
            return 0.0  

        cleaned_value = re.sub(r"[^\d.,]", "", value)  # Remove non-numeric characters

        if "," in cleaned_value and "." in cleaned_value:
            cleaned_value = cleaned_value.replace(",", "")  # Assume comma is a thousand separator
        elif "," in cleaned_value and "." not in cleaned_value:
            cleaned_value = cleaned_value.replace(",", ".")

        try:
            return float(cleaned_value)
        except ValueError:
            print(f"Conversion Error: {value} -> {cleaned_value}")
        return 0.0
    
    def convert_numpy_types(self,data):
        """Convert numpy data types to native Python types"""
        if isinstance(data, np.integer):
            return int(data)
        elif isinstance(data, np.floating):
            return float(data)
        elif isinstance(data, dict):
            return {k: self.convert_numpy_types(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_numpy_types(i) for i in data]
        return data
    
    def create_docs(self, file_contents, company_name):

        df = DataFrame.select_dataframe(company_name)  # Get company-specific DataFrame
        extracted_data_list = []  # Store extracted data before creating a DataFrame

        for filename, file_bytes in file_contents:
            raw_data = ""
            file_extension = filename.split(".")[-1].lower()

            if file_extension == "pdf":
                raw_data = self.get_pdf_text(file_bytes)
            elif file_extension == "xml":
                raw_data = self.extract_text_from_xml(file_bytes)
            elif file_extension in ["jpeg", "png"]:
                raw_data = self.extract_text_from_image(file_bytes)
            else:
                print(f"Unsupported file format: {filename}")
                continue

            if not raw_data or raw_data == "{}":
                print(f"Skipping invalid file: {filename}")
                continue

            # Call LLM to extract structured invoice data
            llm_extracted_data = self.chain.response(raw_data, company_name)

            if not llm_extracted_data:
                print(f"Skipping file due to extraction failure: {filename}")
                continue

            # Convert extracted Pydantic model data into a list of dictionaries
            extracted_data_list.extend([self.convert_numpy_types(item.dict()) for item in llm_extracted_data.items])

        # Append extracted data to the DataFrame
        if extracted_data_list:
            extracted_df = pd.DataFrame.from_records(extracted_data_list)

            # Ensure the extracted DataFrame columns match the selected company schema
            df = pd.concat([df, extracted_df], ignore_index=True)

        return df.fillna("")  # Fill missing values with empty strings