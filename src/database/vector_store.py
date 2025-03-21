from .connection import collection
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import json

class VectorStore:
    def __init__(self):
        self.collection_invoice, self.collection_po = collection()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004"
        )

    def get_vector_store(self, collection, vector_index):
        return MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=self.embeddings,
            index_name=vector_index
        )
    
    def query_vector_store(self, query):
        invoice_store = self.get_vector_store(self.collection_invoice, "vector_index_invoice")
        po_store = self.get_vector_store(self.collection_po, "vector_index_po")
        docs_invoice = invoice_store.similarity_search(query, k=1)
        docs_pos = po_store.similarity_search(query, k=1)
        context = " ".join([doc.page_content for doc in (docs_invoice + docs_pos)])

        return context
        
    # Check if a document with the same text already exists.
    def check_duplicate(self, collection, doc_text):
        existing_doc = collection.find_one({"text": json.dumps(doc_text)})
        return existing_doc is not None  # Returns True if duplicate exists

    def create_vector_store(self, invoice_docs=None, po_docs=None):
        invoice_store = self.get_vector_store(self.collection_invoice, "vector_index_invoice")
        po_store = self.get_vector_store(self.collection_po, "vector_index_po")

        print(f"Invoice Docs: {invoice_docs}")
        print(f"PO DOCS: {po_docs}")

        new_invoices = []
        duplicate_invoices = []
        new_pos = []
        duplicate_pos = []

        # Check for duplicate invoices before adding
        for doc in invoice_docs:
            if self.check_duplicate(self.collection_invoice, doc):
                filename = doc.get("filename", "Unknown Filename")  # Avoid KeyError
                duplicate_invoices.append(filename)
                print(f"Duplicate Invoice Found: {filename}")
            else:
                new_invoices.append(doc)

        # Check for duplicate POs before adding
        for doc in po_docs:
            if self.check_duplicate(self.collection_po, doc):
                filename = doc.get("filename", "Unknown Filename")  # Avoid KeyError
                duplicate_pos.append(filename)
                print(f"Duplicate PO Found: {filename}")
            else:
                new_pos.append(doc)

        # Store only non-duplicate invoices
        if new_invoices:
            invoice_store.add_texts(
                texts=[json.dumps(doc) for doc in new_invoices],
                metadatas=[{"type": "invoice"} for _ in new_invoices]
            )

        # Store only non-duplicate POs
        if new_pos:
            po_store.add_texts(
                texts=[json.dumps(doc) for doc in new_pos],
                metadatas=[{"type": "po"} for _ in new_pos]
            )

        return {  
            "new_invoices": len(new_invoices),
            "duplicate_invoices": {
                "count": len(duplicate_invoices),
                "filenames": duplicate_invoices
            },
            "new_pos": len(new_pos),
            "duplicate_pos": {
                "count": len(duplicate_pos),
                "filenames": duplicate_pos
            }
        }
