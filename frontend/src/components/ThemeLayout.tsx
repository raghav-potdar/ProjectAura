import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import GoogleCalendarEmbed from './GoogleCalendarEmbed';
import UploadSection from './UploadSection';
import { useCalendar } from '../context/CalendarContext';

export default function ThemeLayout() {
  const [selectedDate, setSelectedDate] = useState(() => new Date());
  const navigate = useNavigate();
  const { events } = useCalendar();
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-[1400px] mx-auto p-6">
        <Navbar />
        <div className="mt-6">
          {/* Main Content */}
          <div className="flex gap-6">
            <Sidebar selectedDate={selectedDate} onSelectDate={setSelectedDate}>
              <UploadSection />
            </Sidebar>
            <main className="flex-1">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Schedule</h2>
                  <button
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    onClick={() => navigate('/upload')}
                  >
                    <i className="fas fa-upload mr-2" />
                    Upload Schedule
                  </button>
                </div>
                <GoogleCalendarEmbed height="700px" />
              </div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}
