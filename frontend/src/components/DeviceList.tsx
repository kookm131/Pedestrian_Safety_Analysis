import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Device {
  id: string;
  location: string;
  status: string;
  object_count: number;
}

const DeviceList: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);

  useEffect(() => {
    const fetchData = () => {
      axios.get('http://localhost:5000/api/devices')
        .then(res => setDevices(res.data))
        .catch(err => console.error('장치 목록 로드 실패:', err));
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead className="text-xs text-slate-500 uppercase border-b border-slate-700">
          <tr>
            <th className="py-2">ID</th>
            <th className="py-2">위치</th>
            <th className="py-2">상태</th>
            <th className="py-2">객체 수</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {devices.map(device => (
            <tr key={device.id} className="text-sm">
              <td className="py-3 font-medium text-slate-300">{device.id}</td>
              <td className="py-3 text-slate-400">{device.location}</td>
              <td className="py-3">
                <span className={`px-2 py-0.5 rounded-full text-[10px] ${device.status === '활성' ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'}`}>
                  {device.status}
                </span>
              </td>
              <td className="py-3 text-premium-accent font-bold">{device.object_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DeviceList;
