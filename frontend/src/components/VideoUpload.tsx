import React, { useState } from 'react';
import axios from 'axios';

const VideoUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setMessage('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage(response.data.message);
      setFile(null);
    } catch (error) {
      console.error('Upload failed:', error);
      setMessage('업로드 중 오류가 발생했습니다.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <input 
          type="file" 
          accept="video/*" 
          onChange={handleFileChange}
          className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-premium-accent/10 file:text-premium-accent hover:file:bg-premium-accent/20 cursor-pointer"
        />
      </div>
      <button 
        onClick={handleUpload}
        disabled={!file || uploading}
        className={`w-full py-2 px-4 rounded-lg font-bold transition-all ${!file || uploading ? 'bg-slate-700 text-slate-500 cursor-not-allowed' : 'bg-premium-accent text-slate-900 hover:bg-premium-accent/80 shadow-[0_0_15px_rgba(56,189,248,0.3)]'}`}
      >
        {uploading ? '업로드 중...' : '동영상 분석 시작'}
      </button>
      {message && <p className={`text-sm ${message.includes('성공') ? 'text-green-400' : 'text-red-400'}`}>{message}</p>}
    </div>
  );
};

export default VideoUpload;
