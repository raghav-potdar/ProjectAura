import { useNavigate } from 'react-router-dom';

export default function UploadSection() {
  const navigate = useNavigate();

  return (
    <div className="p-6 bg-gradient-to-br from-white to-slate-50 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-2">Smart Scheduler</h3>
      <p className="text-sm text-slate-600 mb-4">
        Upload your syllabus, describe your goals, and let Aura build a personalised weekly plan. You can tweak it with feedback before adding it to the calendar.
      </p>
      <button
        onClick={() => navigate('/upload')}
        className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
      >
        <i className="fas fa-magic mr-2" />
        Launch Scheduler
      </button>
    </div>
  );
}
