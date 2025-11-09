# Aura Backend

AI-powered scheduling backend that parses academic syllabi and generates optimized study schedules integrated with Google Calendar.

## 🚀 Features

- **Syllabus Parsing**: Extract course information from PDF and DOCX files
- **AI Schedule Generation**: Uses Google Gemini AI to create personalized study plans
- **Google Calendar Integration**: Automatic sync of events to Google Calendar
- **ICS Export**: Download schedules in standard iCalendar format
- **Multi-Agent Architecture**: 
  - Agent 1: Document ingestion and parsing
  - Agent 2: Schedule verification and validation
  - Agent 3: Intelligent task scheduling
- **FastAPI Framework**: High-performance async API with automatic documentation

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Platform account with Calendar API enabled
- Google Generative AI API key

## 🛠️ Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv aura_venv
   .\aura_venv\Scripts\Activate.ps1

   # macOS/Linux
   python3 -m venv aura_venv
   source aura_venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the backend directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project",...}
   ```

## 🔑 Google Calendar API Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Calendar API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and enable it

3. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create

4. **Generate Service Account Key**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key" > JSON
   - Download the JSON file

5. **Set Environment Variable**
   - Copy the entire JSON content (minified, single line)
   - Set as `GOOGLE_CALENDAR_SERVICE_ACCOUNT_JSON` in `.env`

## 🚀 Running the Server

**Development mode with auto-reload:**
```bash
python -m uvicorn app.main:app --reload
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Interactive API documentation is automatically available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Events
- `POST /api/v1/events/upload` - Upload syllabus file
- `POST /api/v1/events/process` - Process uploaded syllabus and extract events

### Planner
- `POST /api/v1/planner/generate` - Generate AI-optimized schedule
- `POST /api/v1/planner/feedback` - Apply user feedback to schedule
- `POST /api/v1/planner/create-ics` - Export schedule as ICS file
- `POST /api/v1/planner/sync-to-google-calendar` - Sync schedule to Google Calendar

### Calendar
- `GET /api/v1/calendar/embed-url` - Get Google Calendar embed URL

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── events.py           # Event upload and processing endpoints
│   │   └── planner.py          # Schedule generation endpoints
│   └── services/
│       ├── __init__.py
│       ├── agent1_ingestor.py  # Document parsing agent
│       ├── agent2_verifier.py  # Schedule verification agent
│       ├── agent3_scheduler.py # Task scheduling agent
│       ├── base_layer.py       # Shared utilities
│       ├── cache.py            # Caching service
│       ├── google_calendar_service.py  # Google Calendar integration
│       └── planner_service.py  # Main scheduling service
├── requirements.txt
└── README.md
```

## 🧠 AI Agents

### Agent 1: Ingestor
- Extracts text from PDF/DOCX files
- Parses course information, assignments, exams
- Structures data for downstream processing

### Agent 2: Verifier
- Validates extracted information
- Checks for conflicts and inconsistencies
- Ensures schedule feasibility

### Agent 3: Scheduler
- Generates optimized study schedules
- Considers deadlines, priorities, and workload
- Creates balanced time allocations

## 🔧 Configuration

### Timezone
Default timezone is set to `America/New_York`. To change:
```python
# In google_calendar_service.py and planner.py
TIMEZONE = pytz.timezone('Your/Timezone')
```

### AI Model
Gemini model can be configured in `planner_service.py`:
```python
model = genai.GenerativeModel("gemini-1.5-flash")
```

## 🐛 Troubleshooting

### Google Calendar 400 Error
Ensure datetime format includes timezone offset (RFC3339):
```python
# Correct format
"2025-11-20T10:00:00-05:00"

# Incorrect format
"2025-11-20T10:00:00"
```

### Service Account Permissions
If calendar sync fails, ensure:
1. Service account JSON is correctly formatted
2. Calendar API is enabled in GCP project
3. Calendar is created with public permissions

### Module Import Errors
Run from backend directory:
```bash
python -m uvicorn app.main:app --reload
```

## 📦 Dependencies

Key packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-generativeai` - Gemini AI integration
- `google-api-python-client` - Google Calendar API
- `PyMuPDF` - PDF parsing
- `python-docx` - DOCX parsing
- `pytz` - Timezone handling
- `pydantic` - Data validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Related

- [Frontend README](../frontend/README.md)
- [Main Project README](../README.md)
