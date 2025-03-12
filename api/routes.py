from fastapi import APIRouter, File, UploadFile, Depends
from typing import List
from src.services.file_processing import FilePipeline
from src.services.chain import Chaining
from .models import FileUploadRequest, ChatRequest,SaveRequest
from src.database.vector_store import VectorStore

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

@router.post("/save_to_db/")
async def save_to_db(data: SaveRequest):
    vector_store = VectorStore()  # Initialize vector store

    result = vector_store.create_vector_store(data.invoices, data.pos)

    return {  
        "message": "Data processed",
        "new_vectorized_invoices": result["new_invoices"],
        "duplicate_invoices": result["duplicate_invoices"]["count"],
        "duplicate_invoice_files": result["duplicate_invoices"]["filenames"],
        "new_vectorized_pos": result["new_pos"],
        "duplicate_pos": result["duplicate_pos"]["count"],
        "duplicate_pos_files": result["duplicate_pos"]["filenames"],
    }


@router.post("/extract_files/")
async def extract_file(files: List[UploadFile] = File(...)):

    fp = FilePipeline()
    extract_contents = [(file.filename, await file.read()) for file in files]

    response = fp.create_docs(extract_contents)

    return response
