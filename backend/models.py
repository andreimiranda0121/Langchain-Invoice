from pydantic import BaseModel, Field
from typing import List


class FileUploadRequest(BaseModel):
    invoice_files: List[str] = Field(..., description="List of expected invoice filenames")
    po_files: List[str] = Field(..., description="List of expected PO filenames")

class ChatRequest(BaseModel):
    query: str
    session_id: str