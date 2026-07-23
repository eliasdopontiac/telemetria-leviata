import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Lightning, ChartLineUp } from '@phosphor-icons/react';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function TelemetryCharts({ history = [] }) {
  const d = history.slice(-40);
  const labels = d.map(i => i.nav?.gps_hora || i.gps_hora || (i.timestamp_iso ? new Date(i.timestamp_iso).toLocaleTimeString('pt-BR') : ''));

  const opts = {
    responsive: true, maintainAspectRatio: false, animation: { duration: 250 },
    layout: { padding: { top: 4, bottom: 0, left: 0, right: 4 } },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9 } } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 9 } } }
    },
    plugins: {
      legend: { position: 'top', labels: { color: '#cbd5e1', font: { family: 'Inter', size: 10 }, boxWidth: 10, padding: 4 } },
      tooltip: { backgroundColor: '#0f172a', titleColor: '#00f2fe', bodyColor: '#f8fafc', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 }
    }
  };

  const energyData = {
    labels,
    datasets: [
      { label: 'Solar (A)', data: d.map(i => i.solar?.corrente ?? i.i_solar ?? (i.solar?.pot ? i.solar.pot / 46.5 : 0)), borderColor: '#ffb703', backgroundColor: 'rgba(255,183,3,0.1)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 0 },
      { label: 'Motor (A)', data: d.map(i => i.prop?.i_motor ?? i.i_motor ?? 0), borderColor: '#00f2fe', backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 0 },
      { label: 'Bateria Liq. (A)', data: d.map(i => i.bateria?.corrente_liq ?? i.i_liq ?? 0), borderColor: '#00e676', backgroundColor: 'transparent', borderWidth: 1.5, borderDash: [3, 3], tension: 0.3, pointRadius: 0 },
    ]
  };

  const tempData = {
    labels,
    datasets: [
      { label: 'Motor (°C)', data: d.map(i => i.prop?.t_motor ?? i.t_motor ?? 0), borderColor: '#ff1744', backgroundColor: 'rgba(255,23,68,0.08)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 0 },
      { label: 'Ctrl (°C)', data: d.map(i => i.prop?.t_ctrl ?? i.t_ctrl ?? 0), borderColor: '#ff9100', backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 0 },
      { label: 'RPM (/100)', data: d.map(i => (i.prop?.rpm ?? i.rpm ?? 0) / 100), borderColor: '#38bdf8', backgroundColor: 'transparent', borderWidth: 1.5, borderDash: [3, 3], tension: 0.3, pointRadius: 0 },
    ]
  };

  return (
    <div className="charts-row">
      <div className="chart-card">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Lightning size={14} weight="duotone" color="#ffb703" />
            <span className="card-title">Geração & Consumo</span>
          </div>
          <span style={{ fontSize: 9, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>Live</span>
        </div>
        <div className="chart-body"><Line data={energyData} options={opts} /></div>
      </div>
      <div className="chart-card">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <ChartLineUp size={14} weight="duotone" color="#00f2fe" />
            <span className="card-title">Térmico & RPM</span>
          </div>
          <span style={{ fontSize: 9, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>Live</span>
        </div>
        <div className="chart-body"><Line data={tempData} options={opts} /></div>
      </div>
    </div>
  );
}
