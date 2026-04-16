import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DeviceList from './components/DeviceList';
import ObjectChart from './components/ObjectChart';
import DensityHeatmap from './components/DensityHeatmap';
import VideoUpload from './components/VideoUpload';
import AnalysisResults from './components/AnalysisResults';

const App: React.FC = () => {
  const [status, setStatus] = useState<string>('연결 중...');

  useEffect(() => {
    axios.get('http://localhost:5000/api/status')
      .then(res => setStatus(res.data.status))
      .catch(() => setStatus('연결 실패'));
  }, []);

  return (
    <div className="min-h-screen bg-premium-dark text-slate-100 p-6">
      <header className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-premium-accent">CAPS: 보행자 안전 분석 플랫폼</h1>
          <p className="text-slate-400">실시간 도시 밀집도 및 위험 상황 모니터링</p>
        </div>
        <div className="flex items-center space-x-4">
          <span className={`px-3 py-1 rounded-full text-sm ${status === '정상' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
            시스템 상태: {status}
          </span>
          <div className="text-right">
            <p className="text-sm font-medium">관리자님, 안녕하세요</p>
            <p className="text-xs text-slate-500">마지막 업데이트: {new Date().toLocaleTimeString('ko-KR')}</p>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-2 space-y-6">
          <div className="bg-premium-card p-6 rounded-xl shadow-lg border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 border-l-4 border-premium-accent pl-3">실시간 보행자 밀집도 (D3)</h2>
            <div className="h-80 w-full flex items-center justify-center bg-slate-900/50 rounded-lg">
              <DensityHeatmap />
            </div>
          </div>
          
          <div className="bg-premium-card p-6 rounded-xl shadow-lg border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 border-l-4 border-premium-accent pl-3">객체 탐지 트렌드 (Plotly)</h2>
            <div className="h-80 w-full">
              <ObjectChart />
            </div>
          </div>
        </section>

        <section className="space-y-6">
          <div className="bg-premium-card p-6 rounded-xl shadow-lg border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 border-l-4 border-premium-accent pl-3">연결된 장치 현황</h2>
            <DeviceList />
          </div>

          <div className="bg-premium-card p-6 rounded-xl shadow-lg border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 border-l-4 border-premium-accent pl-3">동영상 분석 요청</h2>
            <VideoUpload />
          </div>

          <div className="bg-premium-card p-6 rounded-xl shadow-lg border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 border-l-4 border-premium-accent pl-3">최근 분석 내역</h2>
            <AnalysisResults />
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
