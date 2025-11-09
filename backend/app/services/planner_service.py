import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai import types

from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
    except Exception as exc:  # pragma: no cover - configuration failure
        print(f"Failed to configure Gemini: {exc}")

SAFETY_SETTINGS: List[Dict[str, str]] = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

TEXT_GENERATION_CONFIG = types.GenerationConfig(
    temperature=0.7,
    top_p=1,
    top_k=1,
    max_output_tokens=2048,
)

JSON_GENERATION_CONFIG = types.GenerationConfig(
    temperature=0.2,
    response_mime_type="application/json",
)


def _ensure_model() -> genai.GenerativeModel:
    if not model:
        raise RuntimeError("Gemini model not configured. Set GEMINI_API_KEY or GOOGLE_API_KEY.")
    return model


def _clean_json_text(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):]
    if cleaned.startswith("```"):
        cleaned = cleaned[len("```"):]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-len("```")] \
            .strip()
    return cleaned.strip()


def _content_blocks(system_prompt: str, user_prompt: str) -> List[Dict[str, Any]]:
    return [
        {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]},
    ]


async def parse_syllabus(pdf_text: str) -> List[Dict[str, Any]]:
    prompt = (
        "You are an expert data extractor. Parse the following raw text from a syllabus PDF "
        "into a structured JSON array of schedule events. Infer dates and event types (Class, "
        "Exam, Deadline, Break). Use this JSON format: [{\"date\": \"YYYY-MM-DD\", "
        "\"day\": \"DayOfWeek\", \"start_time\": \"HH:MM\", \"end_time\": \"HH:MM\", "
        "\"summary\": \"Event Title\", \"type\": \"Class/Exam/Deadline/Break\"}]. "
        "For all-day events or deadlines you may omit start_time and end_time. Only output the JSON array."
    )
    try:
        response = await _ensure_model().generate_content_async(
            _content_blocks(prompt, pdf_text),
            generation_config=JSON_GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
        )
        cleaned = _clean_json_text(response.text)
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except Exception as exc:
        print(f"Planner parse_syllabus error: {exc}")
    return []


async def analyze_goals(description: str) -> str:
    prompt = (
        "You are a helpful scheduling assistant. Receive a user's description of their weekly goals "
        "and break it down into two sections: GOALS (concrete, quantifiable tasks) and CONSTRAINTS "
        "(specific time blocks or rules). Keep the response concise."
    )
    try:
        response = await _ensure_model().generate_content_async(
            _content_blocks(prompt, description),
            generation_config=TEXT_GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
        )
        return response.text.strip()
    except Exception as exc:
        print(f"Planner analyze_goals error: {exc}")
        return ""


async def analyze_feedback(feedback: str) -> str:
    prompt = (
        "You previously proposed a schedule to a student. They now provided feedback explaining what "
        "needs to change. Extract the new explicit constraints from the feedback. Start the response with "
        "NEW CONSTRAINTS: followed by a numbered list."
    )
    try:
        response = await _ensure_model().generate_content_async(
            _content_blocks(prompt, feedback),
            generation_config=TEXT_GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
        )
        return response.text.strip()
    except Exception as exc:
        print(f"Planner analyze_feedback error: {exc}")
        return ""


async def generate_schedule(
    goals: str,
    fixed_schedule: List[Dict[str, Any]],
    *,
    feedback_constraints: Optional[str] = None,
    previous_schedule: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    fixed_json = json.dumps(fixed_schedule, ensure_ascii=False, indent=2)
    if feedback_constraints and previous_schedule:
        previous_json = json.dumps(previous_schedule, ensure_ascii=False, indent=2)
        prompt = (
            "You are a meticulous scheduling assistant in refinement mode. Produce a JSON object with two keys: "
            "reasoning (string explaining how the feedback was addressed) and schedule (an array following the schema "
            "[{\"Day\":\"Monday\",\"Date\":\"YYYY-MM-DD\",\"Start_Time\":\"HH:MM\",\"End_Time\":\"HH:MM\",\"Task\":\"Description\",\"Category\":\"Study/Project/Personal\"}])."
        )
        user_prompt = (
            f"FIXED_SCHEDULE (Do Not Overlap):\n{fixed_json}\n\n"
            f"ORIGINAL_AOT_GOALS (Must Fulfill):\n{goals}\n\n"
            f"REJECTED_PLAN (The one that failed):\n{previous_json}\n\n"
            f"AOT_FEEDBACK (New rules you MUST follow):\n{feedback_constraints}\n\n"
            "Generate the JSON object now."
        )
        try:
            response = await _ensure_model().generate_content_async(
                _content_blocks(prompt, user_prompt),
                generation_config=JSON_GENERATION_CONFIG,
                safety_settings=SAFETY_SETTINGS,
            )
            cleaned = _clean_json_text(response.text)
            payload = json.loads(cleaned)
            schedule = payload.get("schedule", [])
            reasoning = payload.get("reasoning")
            if not isinstance(schedule, list):
                schedule = []
            return {"schedule": schedule, "reasoning": reasoning}
        except Exception as exc:
            print(f"Planner generate_schedule refinement error: {exc}")
            return {"schedule": [], "reasoning": "Failed to generate revised schedule."}

    prompt = (
        "You are a meticulous scheduling assistant. Generate a weekly timetable that obeys all goals "
        "and constraints, and does not conflict with the provided fixed schedule. Return only a JSON array "
        "matching the schema [{\"Day\":\"Monday\",\"Date\":\"YYYY-MM-DD\",\"Start_Time\":\"HH:MM\",\"End_Time\":\"HH:MM\",\"Task\":\"Description\",\"Category\":\"Study/Project/Personal\"}]."
    )
    user_prompt = (
        f"FIXED_SCHEDULE (Do Not Overlap):\n{fixed_json}\n\n"
        f"AOT_GOALS (Must Fulfill):\n{goals}\n\n"
        "Generate the JSON schedule now."
    )
    try:
        response = await _ensure_model().generate_content_async(
            _content_blocks(prompt, user_prompt),
            generation_config=JSON_GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
        )
        cleaned = _clean_json_text(response.text)
        schedule = json.loads(cleaned)
        if not isinstance(schedule, list):
            schedule = []
        return {"schedule": schedule, "reasoning": None}
    except Exception as exc:
        print(f"Planner generate_schedule error: {exc}")
        return {"schedule": [], "reasoning": "Failed to generate schedule."}


def create_ics(schedule: List[Dict[str, Any]], fixed_schedule: List[Dict[str, Any]], timezone: str = "America/New_York") -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Aura Planner//EN",
        f"X-WR-TIMEZONE:{timezone}",
    ]

    def _format_dt(date_str: str, time_str: Optional[str] = None) -> str:
        if not time_str:
            return date_str.replace("-", "")
        return f"{date_str.replace('-', '')}T{time_str.replace(':', '')}00"

    def _event_uid(prefix: str, index: int) -> str:
        return f"{prefix}-{index}-{int(datetime.utcnow().timestamp())}"

    for idx, item in enumerate(schedule):
        date = item.get("Date")
        start_time = item.get("Start_Time")
        end_time = item.get("End_Time")
        task = item.get("Task", "Scheduled Task")
        category = item.get("Category")
        if not date or not start_time or not end_time:
            continue
        summary = f"[{category}] {task}" if category else task
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{_event_uid('dynamic', idx)}",
            f"SUMMARY:{summary}",
            f"DTSTART;TZID={timezone}:{_format_dt(date, start_time)}",
            f"DTEND;TZID={timezone}:{_format_dt(date, end_time)}",
            "END:VEVENT",
        ])

    for idx, item in enumerate(fixed_schedule):
        date = item.get("date")
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        summary = item.get("summary", "Fixed Event")
        if not date:
            continue
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{_event_uid('fixed', idx)}")
        lines.append(f"SUMMARY:{summary}")
        if start_time and end_time:
            lines.append(f"DTSTART;TZID={timezone}:{_format_dt(date, start_time)}")
            lines.append(f"DTEND;TZID={timezone}:{_format_dt(date, end_time)}")
        else:
            start_dt = datetime.strptime(date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
            lines.append(f"DTSTART;VALUE=DATE:{start_dt.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{end_dt.strftime('%Y%m%d')}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
