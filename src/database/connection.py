import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def collection():
    client = MongoClient(os.getenv("DB_URL"))
    db_name = os.getenv("DB_NAME")
    collection_invoice = client[db_name]["invoice"]
    collection_po = client[db_name]["pos"]

    return collection_invoice, collection_po

