from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI', '')
mongodb_username = os.getenv('MONGODB_USERNAME', '')
mongodb_password = os.getenv('MONGODB_PASSWORD', '')
client = MongoClient(mongodb_uri, username=mongodb_username, password=mongodb_password)
db = client['ebl']
fragments = db['fragments']
