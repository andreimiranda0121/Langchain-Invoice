import io
import pandas as pd
import re
import json
import xml.etree.ElementTree as ET
from pypdf import PdfReader
from backend.services import Chaining
from PIL import Image


class FilePipeline:
    def __init__(self):
        self.chain = Chaining()

    def get_pdf_text(self, pdf_bytes):
        """Extract text from a PDF file (using bytes)."""
        text = ""
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))  
        for page in pdf_reader.pages:
            text += page.extract_text() or "" 
        return text

    def extract_text_from_xml(self, file_bytes):
        """Extract structured text from an XML file."""
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
        text = image
        return text

    def clean_number(self, value):
        if not value or str(value).strip() == "":
            return 0.0  

        # Remove all non-numeric characters except dots and commas
        cleaned_value = re.sub(r"[^\d.,]", "", value)

        # If both comma and dot exist, assume comma is the thousand separator and remove it
        if "," in cleaned_value and "." in cleaned_value:
            cleaned_value = cleaned_value.replace(",", "") 

        # If only comma exists, assume it's a decimal separator and convert it to dot
        elif "," in cleaned_value and "." not in cleaned_value:
            cleaned_value = cleaned_value.replace(",", ".")

        try:
            return float(cleaned_value)
        except ValueError:
            print(f"Conversion Error: {value} -> {cleaned_value}")
        return 0.0

    def create_docs(self, file_contents):
        """Process uploaded invoices and extract structured data."""

        #Create a standardized DataFrame matching schema.py keys
        df = pd.DataFrame(
            {
                "invoice_no": pd.Series(dtype="str"),
                "po_no": pd.Series(dtype="str"),
                "description": pd.Series(dtype="str"),
                "quantity": pd.Series(dtype="str"),  # 🔹 Keep as string to prevent conversion errors
                "date": pd.Series(dtype="str"),
                "unit_price": pd.Series(dtype="float"),
                "amount": pd.Series(dtype="float"),
                "total": pd.Series(dtype="float"),
                "email": pd.Series(dtype="str"),
                "phone_number": pd.Series(dtype="str"),
                "address": pd.Series(dtype="str"),
            }
        )

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

            #Call LLM to extract structured invoice data
            llm_extracted_data = self.chain.response(raw_data)

            # extract the data properly
            if hasattr(llm_extracted_data, "items"):  
                llm_extracted_data = llm_extracted_data.items  # Extract the actual list

            if not isinstance(llm_extracted_data, list):
                print(f"Unexpected LLM output format: {type(llm_extracted_data)}")
                continue

            #Convert extracted items to dictionaries before adding to DataFrame
            standardized_data = []
            for entry in llm_extracted_data:
                if hasattr(entry, "__dict__"): 
                    entry_dict = entry.__dict__
                else:
                    entry_dict = entry  # Already a dictionary

                try:
                    standardized_entry = {
                        "invoice_no": entry_dict.get("invoice_no", ""),
                        "po_no": entry_dict.get("po_no", ""),
                        "description": entry_dict.get("description", ""),
                        "quantity": str(entry_dict.get("quantity", "0")), 
                        "date": entry_dict.get("date", ""),
                        "unit_price": self.clean_number(entry_dict.get("unit_price", "0")), 
                        "amount": self.clean_number(entry_dict.get("amount", "0")),  
                        "total": self.clean_number(entry_dict.get("total", "0")),
                        "email": entry_dict.get("email", ""),
                        "phone_number": entry_dict.get("phone_number", ""),
                        "address": entry_dict.get("address", ""),
                        "filename": filename
                    }
                    standardized_data.append(standardized_entry)
                except ValueError as e:
                    print(f"Data Conversion Error: {e}")

            if standardized_data:
                df_new = pd.DataFrame(standardized_data)  
                df = pd.concat([df, df_new], ignore_index=True)  
            else:
                print("No structured data extracted.")

        return df.fillna("")  # Fill missing values with empty strings
