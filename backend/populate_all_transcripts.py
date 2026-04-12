import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import urllib.parse

# Load environment
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def extract_video_id(url_str):
    if not url_str: return None
    patterns = [
        r"(?:v=|\/)([a-zA-Z0-9_-]{11})(?:\?|&|$)",
        r"youtu\.be\/([a-zA-Z0-9_-]{11})"
    ]
    for p in patterns:
        match = re.search(p, url_str)
        if match: return match.group(1)
    return None

def get_placeholder_transcript(title):
    t = title.lower()
    if 'java' in t and 'javascript' not in t:
        topic = "the Java Programming Language"
        details = "Object-Oriented Programming (OOP), Classes, Objects, Inheritance, and Polymorphism. We will cover environment setup with JDK and writing your first 'Hello World' program."
    elif 'javascript' in t:
        topic = "JavaScript and Web development"
        details = "Variables (let, const, var), DOM manipulation, Event Listeners, and the Fetch API. We will build interactive elements and learn how to make your websites come alive."
    elif 'css' in t:
        topic = "CSS (Cascading Style Sheets)"
        details = "The Box Model, Flexbox, CSS Grid, and Responsive Design. We will learn how to style your HTML elements with colors, layouts, and beautiful animations."
    elif 'mysql' in t or 'sql' in t:
        topic = "Database Management with SQL"
        details = "SELECT statements, JOINs, Indexing, and Schema Design. We will learn how to efficiently store and retrieve data from relational databases using standard SQL syntax."
    elif 'php' in t:
        topic = "Server-side programming with PHP"
        details = "Server-side logic, handling form submissions, and interacting with databases. We will build dynamic web applications that process data on the server."
    elif 'c++' in t:
        topic = "System-level programming with C++"
        details = "Pointers, Memory management, Templates, and the Standard Template Library (STL). This course covers high-performance application development."
    elif 'algebra' in t:
        topic = "Algebraic Fundamentals"
        details = "Variables, linear equations, solving for X, and quadratic formulas. These mathematical foundations are essential for all advanced science and engineering fields."
    elif 'geometry' in t:
        topic = "Geometry and Spatial Reasoning"
        details = "Points, lines, planes, angles, and 3D shapes. We will explore the Pythagorean theorem, area calculations, and the properties of triangles and circles."
    elif 'calculus' in t or 'differentiation' in t or 'integration' in t:
        topic = "Mathematical Calculus"
        details = "Limits, Derivatives, and Integrals. We will learn how to calculate rates of change andareas under curves, forming the basis of modern physics and optimization."
    elif 'physics' in t:
        topic = "Physics and Mechanics"
        details = "Newton's laws of motion, Energy conservation, Thermodynamics, and Electromagnetism. We explore how the physical universe behaves through mathematical laws."
    elif 'chemistry' in t:
        topic = "Chemical Principles"
        details = "The Periodic Table, Atomic structure, Chemical bonding, and Stoichiometry. We will study how matter interacts and transforms during chemical reactions."
    elif 'biology' in t:
        topic = "Biological Sciences"
        details = "Cell biology, Genetics, Evolution, and Human Anatomy. We will explore the complex logic of living organisms from the molecular level to entire ecosystems."
    else:
        topic = "this educational topic"
        details = "The core fundamental concepts involved in this subject. We will go through the basics and gradually move to intermediate levels with practical examples."

    return f"Welcome to this comprehensive course on {topic}! \n\nIn this lesson, we will be diving deep into {details}. \n\nThis transcript is provided as a pre-loaded learning track to ensure your RAG (Retrieval-Augmented Generation) pipeline has high-quality context for testing and interaction. Feel free to use the 'AI Learn' button to process this data into your knowledge base!"

def populate():
    print("Fetching video list from database...")
    v_res = supabase.table("videos").select("id, url, title").execute()
    videos = v_res.data
    print(f"Found {len(videos)} videos.")

    skipped = 0
    updated = 0

    for v in videos:
        v_id = extract_video_id(v['url'])
        if not v_id:
            print(f"  [Error] Could not extract ID from {v['url']}")
            continue

        # Check if already has a real transcript
        existing = supabase.table("ai_video_table").select("transcript_raw").eq("video_id", v_id).execute()
        if existing.data and existing.data[0].get('transcript_raw') and "Welcome" not in existing.data[0]['transcript_raw']:
            print(f"  [Skip] Real transcript already exists for {v['title']}")
            skipped += 1
            continue

        # Populate with themed placeholder
        transcript = get_placeholder_transcript(v['title'])
        data = {
            "video_id": v_id,
            "transcript_raw": transcript,
            "summarized_segments": [f"Introduction to {v['title']}", "Core concept summary"],
            "master_knowledge_base": f"Pre-loaded context for {v['title']}",
            "status": "pending",
            "bucket_file_name": "awaiting_processing", # satisfy NOT NULL if exists
            "updated_at": datetime.now().isoformat()
        }

        try:
            supabase.table("ai_video_table").upsert(data).execute()
            print(f"  [Success] Loaded transcript for: {v['title']}")
            updated += 1
        except Exception as e:
            print(f"  [Failed] Error updating {v['title']}: {e}")

    print(f"\nMigration Finished!")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")

if __name__ == "__main__":
    populate()
