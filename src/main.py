from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from src.extract_classes import extract_classes_from_pdf
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

client = MongoClient("mongodb+srv://machdavis2003_db_user:4j1WOOQz7HWJpZaT@data.2kqvcry.mongodb.net/?appName=data")

db = client["utep_professors"]
professors_collection = db["professors"]
courses_collection = db["classes"] 

# ----------------------------
# CORS — allow Vite/React
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Example class model (to match your frontend)
# -------------------------------------------------
class Course(BaseModel):
    code: str
    name: str
    department: str


# -------------------------------------------------
# 1. Endpoint: Upload file (from UploadPage.tsx)
# -------------------------------------------------
@app.post("/upload-degree-eval")
async def upload_degree_eval(file: UploadFile = File(...)):
    # Read file bytes
    file_bytes = await file.read()

    # Call your extraction function
    extracted = extract_classes_from_pdf(file_bytes)

    # Return result to frontend
    return {"classes": extracted}


# -------------------------------------------------
# 2. Optional: store the selected classes
# -------------------------------------------------
class Selected(BaseModel):
    selected: List[str]


@app.post("/submit-selected-classes")
async def selected_classes(data: Selected):
    print("User selected:", data.selected)
    return { "status": "ok", "message": "Classes received." }

class ClassRequest(BaseModel):
    class_ids: List[str]

def convert_objectid(doc):
    """Recursively convert ObjectId to string so FastAPI can serialize."""
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, list):
        return [convert_objectid(item) for item in doc]
    if isinstance(doc, dict):
        return {key: convert_objectid(value) for key, value in doc.items()}
    return doc


@app.post("/get-professors")
async def get_professors(req: ClassRequest):
    """
    For each requested class_id (e.g. 'CS1301'):

    - Look up the course in the Mongo 'classes' collection
    - Extract the instructors and, for each instructor, their sections +
      meeting times for THIS class
    - Join that data with the professor docs (RMP info) from the 'professors'
      collection
    - Attach the schedule as `class_sections` on each returned professor
    """
    result = {}  # key: course _id, value: list of professors

    for class_id in req.class_ids:
        # 1) Find the course document
        class_doc = courses_collection.find_one({"_id": class_id})
        if not class_doc:
            print(f"⚠️  No course document found in 'classes' for {class_id}")
            result[class_id] = []
            continue

        professors_list = class_doc.get("professors", []) or []

        # 2) Build mapping instructor_id -> sections (with meeting times)
        schedule_by_instructor = {}
        instructor_usernames = []

        for prof_entry in professors_list:
            instructor_id = prof_entry.get("instructor_id")
            if not instructor_id:
                continue

            instructor_usernames.append(instructor_id)

            sections_info = []
            for section in prof_entry.get("sections", []) or []:
                class_info = section.get("class_info", {}) or {}
                meeting_times = class_info.get("meeting_times", []) or []

                sections_info.append(
                    {
                        "crn": section.get("crn"),
                        "section": section.get("section"),
                        # meeting_times is an array like:
                        # { days: ["M","R"], time: "1:30 pm - 2:50 pm", location_building: "...", location_room: "..." }
                        "meeting_times": meeting_times,
                    }
                )

            schedule_by_instructor[instructor_id] = sections_info

        if not instructor_usernames:
            print(f"⚠️  Class {class_id} has no instructors in 'professors' array")
            result[class_id] = []
            continue

        print(f"📌 Class {class_id} has instructor usernames:", instructor_usernames)

        # 3) Fetch professor docs (RMP + static info)
        professor_docs = list(
            professors_collection.find(
                {"username": {"$in": instructor_usernames}},
                {
                    "_id": 1,
                    "username": 1,
                    "college": 1,
                    "department": 1,
                    "first_name": 1,
                    "full_name": 1,
                    "last_name": 1,
                    "last_updated": 1,
                    "middle_initial": 1,
                    "profile_url": 1,
                    "title": 1,
                    "rmp": 1,
                },
            )
        )

        # 4) Attach schedule for THIS class to each professor
        for prof in professor_docs:
            uname = prof.get("username")
            if uname in schedule_by_instructor:
                # This field will be consumed directly in the React app
                prof["class_sections"] = schedule_by_instructor[uname]

        print(f"📚 Found {len(professor_docs)} professors for class {class_id}")

        # 5) Convert ObjectIds before sending to frontend
        professor_docs = convert_objectid(professor_docs)
        result[class_id] = professor_docs

    return {"professors_by_class": result}
