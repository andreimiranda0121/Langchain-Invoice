from fastapi import APIRouter, File, UploadFile, Depends
from typing import List
from src.services.file_processing import FilePipeline
from src.services.chain import Chaining
from .models import FileUploadRequest, ChatRequest

router = APIRouter()

@router.post("/upload_files/")
async def upload_files(
    invoices: List[UploadFile] = File(...),
    pos: List[UploadFile] = File(...),
    file_data: FileUploadRequest = Depends()
):
    fp = FilePipeline()

    # Validate uploaded filenames against provided filenames
    uploaded_invoice_names = {file.filename for file in invoices}
    uploaded_po_names = {file.filename for file in pos}

    if set(file_data.invoice_files) != uploaded_invoice_names:
        return {"error": "Mismatch between provided invoice filenames and uploaded invoices"}
    if set(file_data.po_files) != uploaded_po_names:
        return {"error": "Mismatch between provided PO filenames and uploaded POs"}

    # Process invoices and POs separately
    invoice_contents = [(file.filename, await file.read()) for file in invoices]
    po_contents = [(file.filename, await file.read()) for file in pos]

    invoices_response = fp.create_docs(invoice_contents)
    pos_response = fp.create_docs(po_contents)

    return {
        "invoices": invoices_response,
        "pos": pos_response
    }

@router.post("/chat/")
async def chat(request: ChatRequest):
    ch = Chaining()
    response = ch.chat_response(request.query)
    print(request.session_id)
    return response