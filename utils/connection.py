from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv('MONGODB_URI', '')
client = MongoClient(mongodb_uri)
db = client['ebl']
fragments = db['fragments']

# find fragments with no transliteration
empty_fragments = fragments.find({"text.lines.0": {"$exists": False}})
