Dynamic Week Scheduler (PDF-to-Calendar)

Upload your syllabus, and our AI instantly extracts your schedule. Our AI assistant then uses your simple feedback (AOT/COT) to plan your specific study goals around your classes. Get a perfectly planned week, instantly exported to your calendar.

How to Use (No Installation Required)

This application is a single HTML file (scheduler.html) that runs entirely in your browser.

Get a Google API Key:

Go to Google AI Studio and create an API key.

Make sure your key is enabled to use the "Gemini API".

Edit the File:

Open scheduler.html in any text editor (like VS Code, Notepad, or TextEdit).

Find the line that says const API_KEY = ""; (around line 38).

Paste your API key inside the quotes.

Run the App:

Save the file and double-click scheduler.html to open it in your web browser (e.g., Chrome, Firefox).

Follow the Steps:

Step 1: Upload your syllabus PDF. The app will scan it and extract your fixed schedule (classes, exams, etc.).

Step 2: Choose your method:

Text Description: Write your goals in a single sentence (e.g., "I need to study for 10 hours and finish my project").

Guided Questions: Answer prompts to build your goals step-by-step.

Step 3: The AI will generate a draft of your weekly schedule.

Step 4: Review the schedule.

If you like it, click "Accept & Download .ics".

If you don't, click "Reject & Revise", provide feedback (e.g., "Study sessions are too long"), and the AI will generate a new version.

Step 5: Import the downloaded .ics file into your Google Calendar, Apple Calendar, or Outlook.

Architecture

This application uses a five-stage, interactive pipeline to turn a PDF and a simple user goal into a complete calendar.

PDF Schedule Extraction: The app uses pdf.js to scan the uploaded PDF for schedule-related keywords. It sends only the relevant page's text to the Gemini API, which parses it into a structured JSON "fixed schedule."

Dynamic Goal Input (AOT): The user provides their weekly goals.

Text Mode: The user's text is sent to the Gemini API, which acts as an "Atom of Thoughts" (AOT) assistant, breaking the goal into small, structured tasks (e.g., {"task": "study", "hours": 10}).

Wizard Mode: The user's answers are formatted directly into this structured goal format, skipping the AOT API call.

Initial Schedule Generation: The main scheduling LLM receives the Fixed Schedule and the AOT Goals. It generates a de-conflicted, dynamic weekly schedule in JSON format.

Interactive Refinement (COT Loop):

The user reviews the JSON schedule.

If Rejected, the user's text feedback is sent to the AOT assistant to be converted into new structured constraints (e.g., {"constraint": "max_study_block", "hours": 2}).

The main LLM is called again in Chain of Thought (COT) mode. It receives the original goals, the rejected plan, and the new constraints, forcing it to reason about the mistake and generate a corrected schedule.

Finalization: Once Accepted, the app merges the fixedSchedule.json and the dynamicSchedule.json and uses ical-generator.js to create and download a single, combined .ics calendar file.

Core Components

scheduler.html: A single, standalone HTML file that runs the entire React application using CDN-loaded libraries.

React & Tailwind CSS: Used to build a clean, responsive, and stateful user interface.

PDF.js (pdf.js): A client-side library used to read the raw text content from the user's uploaded PDF.

Gemini API (gemini-2.5-flash-preview-09-2025): The core intelligence of the app, used for all three LLM roles:

PDF Parser: Extracts structured JSON from raw PDF text.

AOT Assistant: Converts user goals and feedback into structured data.

Scheduler LLM: Generates and refines the final timetable using COT logic.

iCal-Generator (ical-generator.js): A client-side library used to generate the final, downloadable .ics file.

Future Updates

Fine-Tuning: Fine-tune the AOT assistant model on a custom dataset of diverse, vague, and complex text descriptions to improve its goal-extraction accuracy.

Live Calendar Integration: Add support for Google Calendar or Outlook Calendar APIs to read/write events directly, rather than relying on .ics file imports.

Expanded File Support: Add support for other document types beyond PDF, such as .docx, .txt, or even screenshots of a schedule.
