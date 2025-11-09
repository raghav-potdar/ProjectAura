import google.generativeai as genai
import os
from typing import List

# Maps to Task 4, 7, 8
# This is Person 3's file
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini client
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-pro') # Use a fast model
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    # Handle the case where the API key is not set
    model = None 

# --- Task 4: Propose Tasks ---
async def generate_tasks(pdf_text: str) -> str:
    if not model:
        return "[]" # Return empty list if model isn't configured

    prompt = f"""
    You are a class schedule parser. Analyze the following text and extract all class schedules.
    For each class found, identify:
    1. Class name and code (e.g., "CSE 611 - Algorithms")
    2. Days of the week (as numbers: 0=Sunday, 1=Monday, ..., 6=Saturday)
    3. Start time (in 24-hour format HH:MM)
    4. End time (in 24-hour format HH:MM)
    
    Return a JSON array of objects with this structure:
    [
      {{
        "title": "Class name and code",
        "daysOfWeek": [day numbers],
        "startTime": "HH:MM",
        "endTime": "HH:MM"
      }}
    ]
    
    Return ONLY the JSON array (no markdown, no extra text).
    If no classes are found, return an empty array [].

    TEXT:
    ---
    {pdf_text}
    ---
    """
    
    try:
        response = await model.generate_content_async(prompt)
        # Clean the response just in case
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        if not cleaned_text.startswith("["):
            return "[]"
        return cleaned_text
    except Exception as e:
        print(f"Agent 1 Error (generate_tasks): {e}")
        return "[]"


async def generate_assignment_tasks(doc_text: str) -> str:
        """
        Parse an assignment/project document and return a JSON array describing
        assignments and their phases. Expected output format:

        [
            {
                "title": "Assignment 1 - Project",
                "due_date": "YYYY-MM-DD",
                "phases": [
                    {"title": "Research", "duration_minutes": 120, "intensity": "High"},
                    {"title": "Draft", "duration_minutes": 60, "intensity": "Medium"}
                ]
            }
        ]

        The model should return ONLY the JSON array.
        """
        if not model:
                return "[]"

        prompt = f"""
        You are an assistant that extracts assignments, projects, and deliverables from a document.
        For each assignment or project in the text, extract:
            - title (brief name)
            - due_date in YYYY-MM-DD format (if present; if not, estimate/say null)
            - phases: an ordered array of phases with keys: title, duration_minutes (estimate), intensity (Low/Medium/High)

        Return a JSON array with that structure and nothing else. If none found return [].

        DOCUMENT:
        ---
        {doc_text}
        ---
        """

        try:
                response = await model.generate_content_async(prompt)
                cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                if not cleaned_text.startswith("["):
                        return "[]"
                return cleaned_text
        except Exception as e:
                print(f"Agent 1 Error (generate_assignment_tasks): {e}")
                return "[]"

# --- Task 7: AI Tutor ---
async def get_help(task_title: str, pdf_text: str) -> str:
    if not model:
        return "AI model not configured."

    prompt = f"""
    You are an AI tutor. A student is working on the task: '{task_title}'.
    This task is from the following document:
    ---
    {pdf_text}
    ---
    Give them a 3-bullet-point summary of actionable advice to get started on this specific task.
    """
    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Agent 1 Error (get_help): {e}")
        return "Error getting help from AI."

# --- Task 8: AI Chef ---
async def get_food_suggestion(meal_type: str) -> str:
    if not model:
        return "AI model not configured."

    prompt = f"You are an AI chef. A busy student needs 3 simple, 15-minute recipe ideas for {meal_type}."
    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Agent 1 Error (get_food_suggestion): {e}")
        return "Error getting suggestions from AI."