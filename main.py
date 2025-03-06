from fastapi import FastAPI, File, UploadFile
from typing import List
from src.utils import FilePipeline

app = FastAPI()

@app.post("/upload_file/")
async def upload_file(files: List[UploadFile] = File(...)):
    fp = FilePipeline()
    
    #Read file contents into a list of tuples (filename, bytes)
    file_contents = [(file.filename, await file.read()) for file in files]

    response = fp.create_docs(file_contents)

    return response
