# standard imports
import os
# package imports
from dotenv import load_dotenv
from pymongo import MongoClient
########################################################
load_dotenv()
def get_connection():
    """Return MongoClient"""
    mongodb_uri = os.getenv('MONGODB_URI', '')
    client = MongoClient(mongodb_uri)
    return client
