from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional


#Use to create an list of invoice for multiple rows and columnns in the extract PDF
class InvoiceItem(BaseModel):
    invoice_no: str = Field(..., description="The invoice number or confirmation number")
    po_no: str = Field(..., description="PO/Purchase Order number get number only")
    description: str = Field(..., description="Item description")
    quantity: str = Field(..., description="Number of items")
    date: str = Field(..., description="Invoice date in YYYY-MM-DD format")
    unit_price: str = Field(..., description="Price per unit without currency symbol")
    amount: str = Field(..., description="Total amount per item without currency symbol")
    total: str = Field(..., description="Total cost/ Gross Amount without currency symbol")
    email: Optional[str] = Field(None, description="Email address (if available)")
    phone_number: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Address")

class InvoiceList(BaseModel):
    items: List[InvoiceItem]  

class Schema:
    @staticmethod
    def create_schema():
        return PydanticOutputParser(pydantic_object=InvoiceList)
