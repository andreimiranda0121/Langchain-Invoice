from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


# Define different schemas for different companies
class InvoiceItemA(BaseModel):
    invoice_no: str = Field(..., description="The invoice number or confirmation number")
    po_no: str = Field(..., description="PO/Purchase Number without characters like 'PO'")
    description: str = Field(..., description="Item description")
    quantity: float = Field(..., description="Number of items")
    date: str = Field(..., description="Invoice date in YYYY-MM-DD format")
    unit_price: str = Field(..., description="Price per unit without currency symbol")
    amount: float = Field(..., description="Total amount per item without currency symbol")
    total: float = Field(..., description="Total cost/ Gross Amount without currency symbol")


class InvoiceItemB(BaseModel):
    invoice_no: str = Field(..., description="Unique Invoice ID")
    po_no: str = Field(..., description="Order reference number")
    description: str = Field(..., description="Product details")
    quantity: str = Field(..., description="Item count")
    unit_price: float = Field(..., description="Cost per item")
    total_cost: float = Field(..., description="Total invoice cost")
    currency: str = Field(..., description="Currency type")
    supplier_email: str = Field(..., description="Supplier email")
    supplier_contact: str = Field(..., description="Supplier contact number")


class InvoiceListA(BaseModel):
    items: List[InvoiceItemA]


class InvoiceListB(BaseModel):
    items: List[InvoiceItemB]


class Schema:
    @staticmethod
    def create_schema(company_name):
        schemas = {
            "Company A": InvoiceListA,
            "Company B": InvoiceListB,  # Company B has a different schema
            "Company C": InvoiceListA,  # Company C reuses Company A's schema
        }
        return PydanticOutputParser(pydantic_object=schemas.get(company_name, InvoiceListA))