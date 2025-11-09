import { useEffect, useState } from 'react';
import axios from 'axios';

interface GoogleCalendarEmbedProps {
  width?: string;
  height?: string;
}

export default function GoogleCalendarEmbed({ 
  width = "100%", 
  height = "600px" 
}: GoogleCalendarEmbedProps) {
  const [embedUrl, setEmbedUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEmbedUrl = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/calendar/embed-url');
        setEmbedUrl(response.data.embedUrl);
        setLoading(false);
      } catch (err: any) {
        console.error('Error fetching calendar embed URL:', err);
        setError(err.response?.data?.detail || 'Failed to load calendar');
        setLoading(false);
      }
    };

    fetchEmbedUrl();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading calendar...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <i className="fas fa-exclamation-circle text-red-500 text-4xl mb-4"></i>
          <h3 className="text-lg font-semibold text-red-800 mb-2">Calendar Not Available</h3>
          <p className="text-red-600 mb-4">{error}</p>
          <p className="text-sm text-gray-600">
            Please ensure Google Calendar credentials are configured in the backend.
          </p>
        </div>
      </div>
    );
  }

  if (!embedUrl) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <p className="text-gray-500">Calendar URL not available</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <iframe
        src={embedUrl}
        style={{ 
          border: 0, 
          width, 
          height,
          borderRadius: '0.5rem'
        }}
        frameBorder="0"
        scrolling="no"
        title="Aura Event Schedule"
        className="shadow-sm"
      />
    </div>
  );
}
