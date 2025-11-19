import json
from pymongo import MongoClient

# ---- 1. Connect to MongoDB ----
client = MongoClient("mongodb+srv://machdavis2003_db_user:4j1WOOQz7HWJpZaT@data.2kqvcry.mongodb.net/?appName=data")   # change if using Atlas
db = client["utep_professors"]                          # your DB name
collection = db["classes"]         # your collection name

# ---- 2. Load JSON from file ----
json_path = "courses_by_subject_number.json"  # uploaded file path

with open(json_path, "r") as f:
    data = json.load(f)

# ---- 3. Insert into MongoDB ----
# data is a dict like:
# {
#   "ACCT2301": { ... },
#   "ACCT2302": { ... },
#   ...
# }
# Each key becomes its own MongoDB document.

documents = []
for course_code, course_data in data.items():
    doc = {"_id": course_code, **course_data}  # use ACCT2301, ACCT2302 as _id
    documents.append(doc)

# insert many (ignoring duplicates if collection already has data)
try:
    collection.insert_many(documents, ordered=False)
    print("Inserted all course documents successfully!")
except Exception as e:
    print("Some documents may already exist. Details:", e)
