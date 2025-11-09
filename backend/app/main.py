from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
import pymupdf as fitz  # PyMuPDF
import os

# Import all our models and services
from .models import CalendarEvent, VerifiedTask
from .services import (
    agent1_ingestor,
    agent2_verifier,
    agent3_scheduler,
    base_layer,
    cache
)
from .services.google_calendar_service import google_calendar_service
from .routers import planner

# Load .env file (for GEMINI_API_KEY)
load_dotenv()

app = FastAPI(title="Aura AI Scheduler")

# --- CORS Middleware ---
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize Google Calendar on startup"""
    print("Initializing Google Calendar service...")
    if google_calendar_service.initialize_service():
        # Try to create a new public calendar
        calendar_id = google_calendar_service.create_public_calendar(
            summary="Aura Event Schedule",
            description="All events and schedules managed by Aura AI Scheduler",
            timezone="America/New_York"
        )
        if calendar_id:
            print(f"Successfully created and configured public calendar: {calendar_id}")
            embed_url = google_calendar_service.get_embed_url()
            print(f"Embed URL: {embed_url}")
        else:
            print("Failed to create calendar. Check your credentials.")
    else:
        print("Google Calendar service initialization failed. Calendar features will be disabled.")

app.include_router(planner.router)

# Task 3, 4, 5, 6, 7: The Main Pipeline
@app.post("/api/v1/upload", response_model=List[CalendarEvent])
async def upload_and_schedule(file: UploadFile = File(...)):
    """
    The main pipeline.
    Receives a PDF (class schedule), runs the ingestor and verifier and returns recurring class events.
    """
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # --- Task 3: Ingest PDF ---
        pdf_bytes = await file.read()
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pdf_text = ""
            for page in doc:
                pdf_text += page.get_text()
            doc.close()
        except Exception as pdf_error:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process PDF: {str(pdf_error)}"
            )

        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        # Cache raw class text
        cache.set('user_1', pdf_text)

        # --- Agent 1: Parse classes ---
        classes_json = await agent1_ingestor.generate_tasks(pdf_text)

        # --- Agent 2: Verify/convert into CalendarEvent objects ---
        class_events = agent2_verifier.verify_tasks(classes_json)

        if not class_events:
            return base_layer.get_base_events()

        # Cache class events for later assignment scheduling
        cache.set('user_1_classes', class_events)

        return class_events

    except Exception as e:
        print(f"Error in /upload pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during scheduling: {str(e)}")


@app.post("/api/v1/upload_assignments", response_model=List[CalendarEvent])
async def upload_assignments(files: List[UploadFile] = File(...)):
    """
    Upload one or more assignment/project documents (PDF or DOCX). The endpoint
    will extract text, ask the ingestor to parse assignment phases, verify them
    and schedule them into the next week's free slots (respecting classes).
    """
    try:
        combined_text = ""
        for f in files:
            filename = f.filename or ''
            content_type = f.content_type or ''
            data = await f.read()

            if 'pdf' in content_type or filename.lower().endswith('.pdf'):
                try:
                    doc = fitz.open(stream=data, filetype='pdf')
                    txt = ''
                    for page in doc:
                        txt += page.get_text()
                    doc.close()
                    combined_text += '\n' + txt
                except Exception as e:
                    print(f"Failed to read uploaded PDF {filename}: {e}")
                    continue
            elif 'word' in content_type or filename.lower().endswith('.docx'):
                try:
                    import docx
                    from io import BytesIO
                    doc = docx.Document(BytesIO(data))
                    txt = '\n'.join(p.text for p in doc.paragraphs)
                    combined_text += '\n' + txt
                except Exception as e:
                    print(f"Failed to read uploaded DOCX {filename}: {e}")
                    continue
            else:
                try:
                    combined_text += '\n' + data.decode('utf-8')
                except Exception:
                    print(f"Skipping unsupported file type: {filename}")
                    continue

        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from uploaded files.")

        # cache raw assignment text
        cache.set('user_1_assignments_text', combined_text)

        # Ask agent1 to parse assignments
        assignments_json = await agent1_ingestor.generate_assignment_tasks(combined_text)

        # Verify / clean the parsed assignments
        assignments = agent2_verifier.verify_assignments(assignments_json)

        # Get class events from cache (if user uploaded classes earlier)
        class_events = cache.get('user_1_classes') or base_layer.get_base_events()

        # Schedule assignment phases
        scheduled = agent3_scheduler.schedule_assignments(assignments, class_events)

        # Return combined view: class events (recurring) + scheduled concrete assignment events
        combined = list(class_events) + list(scheduled)
        return combined

    except Exception as e:
        print(f"Error in /upload_assignments pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during assignment scheduling: {str(e)}")
    # end of upload_assignments endpoint

# Task 7: AI Tutor
@app.post("/api/v1/help")
async def get_help(data: dict = Body(...)):
    """
    Provides AI-powered help for a specific task.
    """
    task_title = data.get('taskTitle')
    if not task_title:
        raise HTTPException(status_code=400, detail="No task title provided.")

    pdf_text = cache.get('user_1') # Get cached PDF text
    if not pdf_text:
        raise HTTPException(status_code=404, detail="No document found. Please upload an assignment first.")
        
    help_text = await agent1_ingestor.get_help(task_title, pdf_text)
    return {"help": help_text}

# Task 8: Food Suggestion
@app.post("/api/v1/food")
async def get_food(data: dict = Body(...)):
    """
    Provides AI-powered food suggestions.
    """
    meal_type = data.get('mealType')
    if not meal_type:
         raise HTTPException(status_code=400, detail="No meal type provided.")

    suggestion = await agent1_ingestor.get_food_suggestion(meal_type)
    return {"suggestion": suggestion}

# Get Google Calendar Embed URL
@app.get("/api/v1/calendar/embed-url")
async def get_calendar_embed_url():
    """
    Returns the Google Calendar embed URL for iframe integration
    """
    embed_url = google_calendar_service.get_embed_url()
    calendar_id = google_calendar_service.calendar_id
    
    if not embed_url or not calendar_id:
        raise HTTPException(
            status_code=503, 
            detail="Google Calendar not initialized. Check backend logs for credentials setup."
        )
    
    return {
        "embedUrl": embed_url,
        "calendarId": calendar_id
    }

# --- How to Run ---
# In your terminal, from the `aura-backend` directory, run:
# uvicorn app.main:app --reload