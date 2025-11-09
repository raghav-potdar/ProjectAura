import { useMemo, useState, type ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCalendar } from '../context/CalendarContext';
import type { CalendarEvent, FixedScheduleItem, PlannerScheduleItem } from '../services/api.service';
import { plannerService } from '../services/api.service';

function normaliseTime(raw?: string) {
  if (!raw) return undefined;
  const value = raw.trim();
  if (!value) return undefined;
  const lower = value.toLowerCase();
  if (lower === 'all day' || lower === 'allday') return 'all-day';
  const match = value.match(/^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/i);
  if (!match) return value;
  let hours = parseInt(match[1], 10);
  const minutes = match[2] ? parseInt(match[2], 10) : 0;
  const meridiem = match[3]?.toLowerCase();
  if (meridiem === 'pm' && hours < 12) hours += 12;
  if (meridiem === 'am' && hours === 12) hours = 0;
  const hh = hours.toString().padStart(2, '0');
  const mm = minutes.toString().padStart(2, '0');
  return `${hh}:${mm}:00`;
}

function toCalendarEvents(schedule: PlannerScheduleItem[]): CalendarEvent[] {
  return schedule.map((item, index) => {
    const normalisedStart = normaliseTime(item.Start_Time);
    const normalisedEnd = normaliseTime(item.End_Time);
    const allDay =
      normalisedStart === 'all-day' ||
      normalisedEnd === 'all-day' ||
      !normalisedStart ||
      normalisedStart === '';
    const start =
      item.Date && normalisedStart && normalisedStart !== 'all-day'
        ? `${item.Date}T${normalisedStart}`
        : item.Date && allDay
          ? item.Date
          : undefined;
    const end =
      item.Date && normalisedEnd && normalisedEnd !== 'all-day'
        ? `${item.Date}T${normalisedEnd}`
        : undefined;
    return {
      id: `${item.Date ?? 'event'}-${index}`,
      title: item.Task ?? 'Planned Task',
      start,
      end,
      allDay,
      extendedProps: {
        category: item.Category,
        day: item.Day,
      },
    };
  });
}

type WizardStep = 'upload' | 'goals' | 'review';

export default function ScheduleUploadPage() {
  const navigate = useNavigate();
  const { addEvents } = useCalendar();

  const [step, setStep] = useState<WizardStep>('upload');
  const [fixedSchedule, setFixedSchedule] = useState<FixedScheduleItem[]>([]);
  const [goalsInput, setGoalsInput] = useState('');
  const [goalsSummary, setGoalsSummary] = useState('');
  const [schedule, setSchedule] = useState<PlannerScheduleItem[]>([]);
  const [scheduleNotes, setScheduleNotes] = useState('');
  const [feedbackInput, setFeedbackInput] = useState('');
  const [feedbackConstraints, setFeedbackConstraints] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState('');

  const hasSchedule = schedule.length > 0;
  const isBusy = Boolean(loadingMessage);
  const fixedPreview = useMemo(() => fixedSchedule.slice(0, 5), [fixedSchedule]);

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError('');
    setLoadingMessage('Parsing syllabus...');
    try {
      const parsed = await plannerService.parseSyllabus(file);
      if (!parsed.length) {
        throw new Error('No events found in the syllabus.');
      }
      setFixedSchedule(parsed);
      setStep('goals');
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Unable to parse syllabus.');
    } finally {
      setLoadingMessage('');
      event.target.value = '';
    }
  };

  const handleAnalyzeGoals = async () => {
    if (!goalsInput.trim()) {
      setError('Please describe your course goals before continuing.');
      return;
    }
    setError('');
    setLoadingMessage('Analyzing goals...');
    try {
      const summary = await plannerService.analyzeGoals(goalsInput);
      setGoalsSummary(summary);
      setStep('review');
      await handleGenerateSchedule(summary, null, []);
    } catch (goalError) {
      setError(goalError instanceof Error ? goalError.message : 'Unable to analyze goals.');
    } finally {
      setLoadingMessage('');
    }
  };

  const handleGenerateSchedule = async (
    goals: string,
    constraints: string | null,
    previous: PlannerScheduleItem[]
  ) => {
    setLoadingMessage('Generating schedule...');
    setError('');
    try {
      const response = await plannerService.generateSchedule({
        fixedSchedule,
        goals,
        feedbackConstraints: constraints ?? undefined,
        previousSchedule: previous.length ? previous : undefined,
      });
      setSchedule(response.schedule ?? []);
      setScheduleNotes(response.reasoning ?? '');
    } catch (scheduleError) {
      setError(scheduleError instanceof Error ? scheduleError.message : 'Unable to generate schedule.');
    } finally {
      setLoadingMessage('');
    }
  };

  const handleSubmitFeedback = async () => {
    if (!feedbackInput.trim()) {
      setError('Please enter feedback before refining the schedule.');
      return;
    }
    setError('');
    setLoadingMessage('Processing feedback...');
    try {
      const constraints = await plannerService.analyzeFeedback(feedbackInput);
      setFeedbackConstraints(constraints);
      await handleGenerateSchedule(goalsSummary || goalsInput, constraints, schedule);
      setFeedbackInput('');
    } catch (feedbackError) {
      setError(feedbackError instanceof Error ? feedbackError.message : 'Unable to process feedback.');
    } finally {
      setLoadingMessage('');
    }
  };

  const handleAcceptSchedule = async () => {
    if (!schedule.length) return;
    setError('');
    setLoadingMessage('Syncing events to Google Calendar...');
    try {
      const result = await plannerService.syncToGoogleCalendar({
        schedule,
        fixedSchedule,
      });
      
      const events = toCalendarEvents(schedule);
      addEvents(events);
      
      alert(`Success! ${result.eventsCreated} events added to Google Calendar.`);
      navigate('/');
    } catch (acceptError) {
      setError(acceptError instanceof Error ? acceptError.message : 'Unable to sync to Google Calendar.');
    } finally {
      setLoadingMessage('');
    }
  };

  const handleDownloadICS = async () => {
    if (!schedule.length) return;
    setError('');
    setLoadingMessage('Creating ICS file...');
    try {
      const ics = await plannerService.createIcs({
        schedule,
        fixedSchedule,
      });

      const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'aura-planner-schedule.ics';
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : 'Unable to export ICS file.');
    } finally {
      setLoadingMessage('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-10">
        <button
          type="button"
          onClick={() => navigate('/')}
          className="text-sm text-indigo-300 hover:text-indigo-200"
        >
          ← Back to dashboard
        </button>
        <div>
          <h1 className="text-3xl font-semibold">Create Your Course Plan</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">
            Upload your syllabus, outline your goals, and let Aura build a personalised learning plan. Review the
            proposed schedule, request adjustments, then export everything to your calendar.
          </p>
        </div>

        <div className="grid gap-6 rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
          <div className="grid gap-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">Step {step === 'upload' ? '1' : step === 'goals' ? '2' : '3'} of 3</p>
            <div className="flex flex-wrap gap-2 text-sm font-medium">
              <span className={`rounded-full px-3 py-1 ${step === 'upload' ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-300'}`}>
                Upload syllabus
              </span>
              <span className={`rounded-full px-3 py-1 ${step === 'goals' ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-300'}`}>
                Define goals
              </span>
              <span className={`rounded-full px-3 py-1 ${step === 'review' ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-300'}`}>
                Describe your weekly plan
              </span>
            </div>
          </div>

          {step === 'upload' && (
            <div className="grid gap-4">
              <label className="text-sm font-medium text-slate-200" htmlFor="syllabus-upload">
                Upload your course syllabus (PDF)
              </label>
              <input
                id="syllabus-upload"
                type="file"
                accept="application/pdf"
                onChange={handleUpload}
                disabled={isBusy}
                className="rounded border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-200"
              />
              {fixedSchedule.length > 0 && (
                <div className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-300">
                  <p className="font-medium text-slate-200">Preview</p>
                  <p className="mt-1 text-xs text-slate-400">First few detected events:</p>
                  <ul className="mt-2 grid gap-2 text-sm">
                    {fixedPreview.map((item, index) => (
                      <li key={`${item.summary}-${index}`} className="rounded-md bg-slate-800/60 px-3 py-2">
                        <p className="font-medium text-slate-100">{item.summary}</p>
                        <p className="text-xs text-slate-400">
                          {item.date} · {item.start_time ?? 'TBA'}{item.end_time ? ` – ${item.end_time}` : ''}
                        </p>
                      </li>
                    ))}
                    {fixedSchedule.length > fixedPreview.length && (
                      <li className="text-xs text-slate-500">+ {fixedSchedule.length - fixedPreview.length} more</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}

          {step === 'goals' && (
            <div className="grid gap-4">
              <label className="text-sm font-medium text-slate-200" htmlFor="goals-input">
                Describe what success looks like for this course
              </label>
              <textarea
                id="goals-input"
                value={goalsInput}
                onChange={(event) => setGoalsInput(event.target.value)}
                placeholder="E.g. focus on weekly reading summaries, prep for labs earlier, keep weekends light..."
                rows={6}
                className="rounded border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-200"
              />
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleAnalyzeGoals}
                  disabled={isBusy}
                  className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 disabled:opacity-40"
                >
                  Continue to schedule
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setStep('upload');
                    setGoalsInput('');
                    setGoalsSummary('');
                    setFixedSchedule([]);
                    setSchedule([]);
                    setScheduleNotes('');
                    setFeedbackInput('');
                    setFeedbackConstraints(null);
                    setError('');
                    setLoadingMessage('');
                  }}
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
                >
                  Start over
                </button>
              </div>
            </div>
          )}

          {step === 'review' && (
            <div className="grid gap-6">
              {goalsSummary && (
                <div className="rounded-xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm">
                  <p className="font-medium text-slate-200">Goals summary</p>
                  <p className="mt-1 text-slate-300 whitespace-pre-line text-sm">{goalsSummary}</p>
                </div>
              )}

              <div className="grid gap-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-slate-100">Proposed schedule</h2>
                  <button
                    type="button"
                    onClick={() => handleGenerateSchedule(goalsSummary || goalsInput, feedbackConstraints, schedule)}
                    disabled={isBusy}
                    className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-40"
                  >
                    Regenerate
                  </button>
                </div>
                <div className="overflow-x-auto rounded-xl border border-slate-800">
                  <table className="min-w-full divide-y divide-slate-800 text-left text-sm text-slate-200">
                    <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
                      <tr>
                        <th className="px-4 py-2">Date</th>
                        <th className="px-4 py-2">Time</th>
                        <th className="px-4 py-2">Task</th>
                        <th className="px-4 py-2">Category</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {hasSchedule ? (
                        schedule.map((item, index) => (
                          <tr key={`${item.Task}-${index}`} className="bg-slate-900/40">
                            <td className="px-4 py-3 text-sm text-slate-200">
                              <div className="font-medium">{item.Date ?? 'TBD'}</div>
                              <div className="text-xs text-slate-400">{item.Day ?? ''}</div>
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-200">
                              {item.Start_Time ? `${item.Start_Time}` : '—'}
                              {item.End_Time ? ` – ${item.End_Time}` : ''}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-100">{item.Task}</td>
                            <td className="px-4 py-3 text-sm text-slate-300">{item.Category ?? 'General'}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td className="px-4 py-6 text-center text-sm text-slate-400" colSpan={4}>
                            No schedule yet. Click regenerate to try again.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
                {scheduleNotes && (
                  <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/10 px-4 py-3 text-sm text-indigo-200">
                    <p className="font-medium">Planner notes</p>
                    <p className="mt-1 whitespace-pre-line text-sm">{scheduleNotes}</p>
                  </div>
                )}
              </div>

              <div className="grid gap-3">
                <label className="text-sm font-medium text-slate-200" htmlFor="feedback-input">
                  Need adjustments? Let Aura know what to change.
                </label>
                <textarea
                  id="feedback-input"
                  value={feedbackInput}
                  onChange={(event) => setFeedbackInput(event.target.value)}
                  placeholder="E.g. shift evening study sessions earlier, add buffer before exams..."
                  rows={4}
                  className="rounded border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-slate-200"
                />
                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    disabled={!hasSchedule || isBusy}
                    onClick={handleSubmitFeedback}
                    className="rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-700 disabled:opacity-40"
                  >
                    Apply feedback
                  </button>
                  <button
                    type="button"
                    disabled={!hasSchedule || isBusy}
                    onClick={handleAcceptSchedule}
                    className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 disabled:opacity-40"
                  >
                    Accept & export to Google Calendar
                  </button>
                  <button
                    type="button"
                    disabled={!hasSchedule || isBusy}
                    onClick={handleDownloadICS}
                    className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-40"
                  >
                    Download ICS
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {(loadingMessage || error) && (
          <div className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm">
            {loadingMessage && <p className="text-indigo-300">{loadingMessage}</p>}
            {error && <p className="text-rose-300">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
