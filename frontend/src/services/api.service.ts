import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1'; // FastAPI default port

export interface CalendarEvent {
  id?: string;
  title: string;
  start?: string; // ISO datetime for concrete events
  end?: string;   // ISO datetime for concrete events
  allDay?: boolean;
  startTime?: string; // "HH:MM:SS" for recurring events
  endTime?: string;
  daysOfWeek?: number[]; // recurring days
  display?: string;
  color?: string;
  extendedProps?: any;
}

export interface FixedScheduleItem {
  date: string;
  day?: string;
  start_time?: string;
  end_time?: string;
  summary: string;
  type?: string;
}

export interface PlannerScheduleItem {
  Day?: string;
  Date: string;
  Start_Time?: string;
  End_Time?: string;
  Task: string;
  Category?: string;
}

export interface HelpResponse {
  help: string;
}

export interface FoodSuggestionResponse {
  suggestion: string;
}

const apiService = {
  // Get base calendar events
  getBaseEvents: async (): Promise<CalendarEvent[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/events/base`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch base events');
    }
  },

  // Upload PDF and get scheduled events
  uploadPDF: async (file: File): Promise<CalendarEvent[]> => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to upload and process PDF');
    }
  },

  // Upload assignment documents (PDF or DOCX) and get scheduled assignment events
  uploadAssignments: async (files: File[]): Promise<CalendarEvent[]> => {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));

    try {
      const response = await axios.post(`${API_BASE_URL}/upload_assignments`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to upload and schedule assignments');
    }
  },

  // Get help for a specific task
  getTaskHelp: async (taskTitle: string): Promise<HelpResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/help`, { taskTitle });
      return response.data;
    } catch (error) {
      throw new Error('Failed to get task help');
    }
  },

  // Get food suggestions
  getFoodSuggestion: async (mealType: string): Promise<FoodSuggestionResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/food`, { mealType });
      return response.data;
    } catch (error) {
      throw new Error('Failed to get food suggestion');
    }
  }
};

const plannerService = {
  parseSyllabus: async (file: File): Promise<FixedScheduleItem[]> => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post(`${API_BASE_URL}/planner/parse-syllabus`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to parse syllabus.');
    }
  },

  analyzeGoals: async (description: string): Promise<string> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/planner/analyze-goals`, { description });
      return response.data.analysis as string;
    } catch (error) {
      throw new Error('Failed to analyze goals.');
    }
  },

  analyzeFeedback: async (feedback: string): Promise<string> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/planner/analyze-feedback`, { feedback });
      return response.data.constraints as string;
    } catch (error) {
      throw new Error('Failed to analyze feedback.');
    }
  },

  generateSchedule: async (payload: {
    fixedSchedule: FixedScheduleItem[];
    goals: string;
    feedbackConstraints?: string;
    previousSchedule?: PlannerScheduleItem[];
  }): Promise<{ schedule: PlannerScheduleItem[]; reasoning?: string | null }> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/planner/generate`, {
        fixed_schedule: payload.fixedSchedule,
        goals: payload.goals,
        feedback_constraints: payload.feedbackConstraints,
        previous_schedule: payload.previousSchedule,
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to generate schedule.');
    }
  },

  createIcs: async (payload: {
    schedule: PlannerScheduleItem[];
    fixedSchedule: FixedScheduleItem[];
  }): Promise<string> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/planner/ics`, {
        schedule: payload.schedule,
        fixed_schedule: payload.fixedSchedule,
      });
      return response.data.ics as string;
    } catch (error) {
      throw new Error('Failed to generate ICS.');
    }
  },

  syncToGoogleCalendar: async (payload: {
    schedule: PlannerScheduleItem[];
    fixedSchedule: FixedScheduleItem[];
  }): Promise<{ message: string; eventsCreated: number }> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/planner/sync-to-google-calendar`, {
        schedule: payload.schedule,
        fixed_schedule: payload.fixedSchedule,
      });
      return response.data;
    } catch (error) {
      throw new Error('Failed to sync events to Google Calendar.');
    }
  },
};

export default apiService;
export { plannerService };