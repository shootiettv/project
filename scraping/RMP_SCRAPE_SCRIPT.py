import requests
import json
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://machdavis2003_db_user:4j1WOOQz7HWJpZaT@data.2kqvcry.mongodb.net/?appName=data"
DB_NAME = "utep_professors"
COLLECTION = "professors"

WRITE_CHANGES = True    
TEST_LIMIT = None        


GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

session = requests.Session()
session.headers.update(HEADERS)


def gql(query, variables=None):
    r = session.post(GRAPHQL_URL, json={"query": query, "variables": variables or {}})
    try:
        return r.json()
    except:
        return {"error": "non-json", "text": r.text[:500]}


def get_utep_school_id():
    query = """
    query($text: String!) {
      newSearch {
        schools(query: { text: $text }) {
          edges { node { id name } }
        }
      }
    }
    """
    data = gql(query, {"text": "the university of texas at el paso"})
    return data["data"]["newSearch"]["schools"]["edges"][0]["node"]["id"]


def search_rmp_teacher(name, school_id):
    query = """
    query($text: String!, $schoolID: ID!) {
      newSearch {
        teachers(query: {
          text: $text,
          schoolID: $schoolID,
          fallback: true
        }) {
          edges {
            node {
              id
              firstName
              lastName
            }
          }
        }
      }
    }
    """
    data = gql(query, {"text": name, "schoolID": school_id})

    try:
        edges = data["data"]["newSearch"]["teachers"]["edges"]
        return [edge["node"] for edge in edges]
    except:
        return []


def fallback_html_search(name):
    print("Running fallback HTML search...")
    query = name.replace(" ", "+")
    url = f"https://www.ratemyprofessors.com/search/teachers?query={query}"
    html = session.get(url).text

    import re
    matches = re.findall(r'/professor/([A-Za-z0-9=]+)"', html)

    return matches[0] if matches else None


def get_rmp_profile(profile_id):
    query = """
    query GetTeacher($id: ID!) {
      node(id: $id) {
        ... on Teacher {
          id
          firstName
          lastName
          avgRating
          avgDifficulty
          wouldTakeAgainPercent
          numRatings
          ratings(first: 50) {
            edges {
              node {
                id
                date
                class
                clarityRating
                difficultyRating
                comment
              }
            }
          }
        }
      }
    }
    """

    data = gql(query, {"id": profile_id})

    teacher = data.get("data", {}).get("node")
    if teacher is None or teacher.get("avgRating") is None:
        return None

    reviews = []
    for edge in teacher["ratings"]["edges"]:
        reviews.append({
            "date": edge["node"]["date"],
            "class": edge["node"]["class"],
            "clarityRating": edge["node"]["clarityRating"],
            "difficultyRating": edge["node"]["difficultyRating"],
            "comment": edge["node"]["comment"] or "No Comments",
        })

    return {
        "avgRating": teacher["avgRating"],
        "avgDifficulty": teacher["avgDifficulty"],
        "numRatings": teacher["numRatings"],
        "wouldTakeAgainPercent": teacher["wouldTakeAgainPercent"],
        "reviews": reviews
    }


client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION]

print("Connecting to MongoDB...")
print("Finding UTEP school ID...")
school_id = get_utep_school_id()
print("UTEP ID =", school_id, "\n")

cursor = collection.find().limit(TEST_LIMIT) if TEST_LIMIT else collection.find()

count = 0

for prof in cursor:
    print(f"Processing {prof['full_name']} ({prof['_id']})")

    if "rmp" in prof and isinstance(prof["rmp"], dict):
        print("Already has RMP data — SKIPPING")
        continue

    full_name = f"{prof['first_name']} {prof['last_name']}"

    matches = search_rmp_teacher(full_name, school_id)

    if matches:
        profile_id = matches[0]["id"]
        print(f"Found via GraphQL: {profile_id}")
    else:
        print("Not found via GraphQL. Trying fallback...")
        profile_id = fallback_html_search(full_name)

        if profile_id:
            print(f"Found via fallback: {profile_id}")
        else:
            print("No RMP match found — SKIPPING")
            continue

    rmp_data = get_rmp_profile(profile_id)

    if not rmp_data:
        print("Could not fetch RMP profile — SKIPPING")
        continue

    print("Retrieved RMP data")

    if WRITE_CHANGES:
        collection.update_one(
            {"_id": prof["_id"]},
            {"$set": {"rmp": rmp_data}}
        )
        print("Saved to MongoDB")
    else:
        print("TEST MODE — not writing to DB")

    count += 1

print(f"Completed RMP update for {count} professors.")






