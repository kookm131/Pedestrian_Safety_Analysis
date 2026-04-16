import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const DensityHeatmap: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 400;
    const height = 240;
    
    // 더미 데이터 생성
    const data = Array.from({ length: 50 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      value: Math.random()
    }));

    const color = d3.scaleSequential(d3.interpolateInferno)
      .domain([0, 1]);

    svg.selectAll('circle')
      .data(data)
      .enter()
      .append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', 15)
      .attr('fill', d => color(d.value))
      .attr('opacity', 0.6)
      .attr('filter', 'blur(8px)');

  }, []);

  return (
    <svg ref={svgRef} width="100%" height="100%" viewBox="0 0 400 240" preserveAspectRatio="xMidYMid meet" />
  );
};

export default DensityHeatmap;
