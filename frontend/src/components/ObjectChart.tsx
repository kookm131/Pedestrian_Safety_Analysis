import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

// react-plotly.js는 내부적으로 plotly.js를 사용하지만, plotly.js-dist-min을 직접 쓸 경우 컴포넌트 래퍼가 필요할 수 있습니다.
// 여기서는 간단하게 Plotly 라이브러리를 직접 호출하거나 react-plotly.js를 사용한다고 가정합니다.
// 하지만 package.json에는 plotly.js-dist-min만 있으므로, 간단한 div를 사용한 직접 렌더링을 구현합니다.

declare const Plotly: any;

const ObjectChart: React.FC = () => {
  useEffect(() => {
    const trace1 = {
      x: ['17:00', '17:10', '17:20', '17:30', '17:40', '17:50'],
      y: [12, 18, 29, 45, 34, 42],
      type: 'scatter',
      mode: 'lines+markers',
      name: '보행자',
      line: { color: '#38bdf8', width: 3 },
      marker: { size: 8 }
    };

    const trace2 = {
      x: ['17:00', '17:10', '17:20', '17:30', '17:40', '17:50'],
      y: [2, 5, 3, 10, 8, 12],
      type: 'scatter',
      mode: 'lines+markers',
      name: '차량',
      line: { color: '#facc15', width: 3 },
      marker: { size: 8 }
    };

    const layout = {
      autosize: true,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#94a3b8', family: 'Inter' },
      margin: { l: 40, r: 20, t: 30, b: 40 },
      xaxis: { gridcolor: '#334155' },
      yaxis: { gridcolor: '#334155' },
      legend: { orientation: 'h', y: -0.2 }
    };

    const config = { responsive: true, displayModeBar: false };

    if ((window as any).Plotly) {
      (window as any).Plotly.newPlot('plotly-chart', [trace1, trace2], layout, config);
    }
  }, []);

  return <div id="plotly-chart" className="w-full h-full" />;
};

export default ObjectChart;
