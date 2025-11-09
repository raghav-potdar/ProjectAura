import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api/v1';

interface ICSUploadResponse {
  success: boolean;
  events: Array<{
    title: string;
    start: string;
    end: string;
    display?: string;
    color?: string;
    category?: string;
  }>;
}

export async function uploadICSFile(file: File): Promise<ICSUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post<ICSUploadResponse>(
      `${API_BASE_URL}/ics`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    throw new Error('Failed to upload ICS file');
  }
}