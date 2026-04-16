import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface AnalysisResult {
  id: number;
  file_id: string;
  filename: string;
  analysis_data: {
    summary: Array<Record<string, number>>;
    status: string;
  };
  created_at: string;
}

const AnalysisResults: React.FC = () => {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchResults = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/results');
      setResults(response.data);
    } catch (error) {
      console.error('Failed to fetch results:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResults();
    const interval = setInterval(fetchResults, 5000); // 5초마다 갱신
    return () => clearInterval(interval);
  }, []);

  if (loading) return <p className="text-slate-500 text-center py-4">조회 중...</p>;

  return (
    <div className="space-y-3">
      {results.length === 0 ? (
        <p className="text-slate-500 text-center py-4 text-sm">최근 분석 내역이 없습니다.</p>
      ) : (
        results.map(res => (
          <div key={res.id} className="bg-slate-800/40 border border-slate-700/50 p-3 rounded-lg hover:border-premium-accent/30 transition-colors">
            <div className="flex justify-between items-start mb-2">
              <p className="font-semibold text-sm truncate max-w-[180px]">{res.filename}</p>
              <span className="text-[10px] text-slate-500">{new Date(res.created_at).toLocaleString()}</span>
            </div>
            <div className="flex flex-wrap gap-1 mt-2">
              {res.analysis_data.summary.map((frame, idx) => (
                Object.entries(frame).map(([label, count]) => (
                  <span key={`${idx}-${label}`} className="bg-premium-accent/10 text-premium-accent text-[10px] px-1.5 py-0.5 rounded">
                    {label}: {count}
                  </span>
                ))
              )).slice(0, 5) /* 처음 5개 태그만 표시 */}
              {res.analysis_data.summary.length > 0 && <span className="text-[10px] text-slate-500">...</span>}
            </div>
            <div className="mt-2 text-right">
              <button className="text-[10px] text-premium-accent hover:underline">상세 정보 보기</button>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default AnalysisResults;
