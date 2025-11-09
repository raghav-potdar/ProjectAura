import React, { useCallback } from 'react';
import { uploadICSFile } from '../services/ics.service';

export default function ICSUploadSection() {
  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const icsFiles = Array.from(files).filter(f => f.name.endsWith('.ics'));
    if (icsFiles.length !== files.length) {
      alert('Please upload only .ics files');
      return;
    }

    try {
      for (const file of icsFiles) {
        const result = await uploadICSFile(file);
        console.log('Uploaded events:', result.events);
        // TODO: Add events to calendar state
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload ICS file');
    }
  }, []);

  return (
    <label className="block">
      <div className="flex items-center justify-center w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition cursor-pointer">
        <i className="fas fa-calendar text-gray-400 mr-2" />
        <span className="text-sm text-gray-600">Choose ICS Files</span>
        <input
          type="file"
          accept=".ics"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
    </label>
  );
}