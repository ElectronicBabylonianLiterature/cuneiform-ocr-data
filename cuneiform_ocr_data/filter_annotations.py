import json
from pymongo import MongoClient
import os

CONNECTION = os.environ.get('MONGODB_CONNECTION', '') #Your MONGODB Connection string

client = MongoClient(CONNECTION)
db = client['ebl']

def keep_fragments(directory, collection_name):
    # List to store the fragments that meet the criteria
    valid_fragments = []
    
    # Access the MongoDB collection
    collection = db[collection_name]
    
    # Loop through all the files in the directory
    for filename in os.listdir(directory):
        if filename.startswith('gt_') and filename.endswith('.txt'):
            fragment_name = filename.split('gt_')[1][:-4]
            
            # Full path to the file
            filepath = os.path.join(directory, filename)
            
            # Read the content of the file
            with open(filepath, 'r', encoding='utf-8') as file:
                annotations = file.read().strip().split('\n')
            
            # Query MongoDB to find the documents that match the fragment_name in 'signs'
                pipeline = [
                    { "$match": { "_id": f"{fragment_name}" } },
                    { "$unwind": "$text.lines" },
                    { "$unwind": "$text.lines.content" },
                    { "$unwind": "$text.lines.content.parts" },
                    { "$match": { 
                        "text.lines.content.parts.enclosureType": { "$ne": "BROKEN_AWAY" },
                        "$or": [
                            { "text.lines.content.parts.type": "Reading" },
                            { "text.lines.content.parts.type": "Logogram" }
                        ]
                    } },
                    { "$count": "count" }
                ]
                result = collection.aggregate(pipeline)
                for doc in result:
                    signs = doc['count']
                print(signs, end=' ', flush=True)

            
            # If more than 50% match, keep this fragment
                fraction = len(annotations) / signs
                if fraction > 0.4:
                    valid_fragments.append(fragment_name)
    
    return valid_fragments

# Directory containing the annotation files (can be overridden by environment variable)
directory = os.environ.get('ANNOTATIONS_DIRECTORY', 'annotations')

# Collection name in MongoDB
collection_name = 'fragments'  # replace with your actual collection name

# Call the function
valid_fragments = keep_fragments(directory, collection_name)
output_json_path = 'valid_fragments.json'

# Save the valid fragments to a JSON file
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(valid_fragments, json_file, ensure_ascii=False, indent=4)
