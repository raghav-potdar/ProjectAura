import { Route, Routes } from 'react-router-dom';
import ThemeLayout from './components/ThemeLayout';
import ScheduleUploadPage from './pages/ScheduleUploadPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ThemeLayout />} />
      <Route path="/upload" element={<ScheduleUploadPage />} />
    </Routes>
  );
}