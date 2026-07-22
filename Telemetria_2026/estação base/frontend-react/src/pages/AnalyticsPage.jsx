import React from 'react';
import TelemetryCharts from '../components/TelemetryCharts';

export default function AnalyticsPage({ history }) {
  return (
    <div className="analytics-page" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: 'var(--primary)' }}>Análise de Telemetria</span>
        <span style={{ fontSize: '12px', color: 'var(--text-dim)', fontWeight: 'normal', backgroundColor: 'var(--bg-card)', padding: '2px 8px', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
          Histórico de Sessão
        </span>
      </h2>
      <div style={{ flex: 1, minHeight: '600px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <TelemetryCharts history={history} />
      </div>
    </div>
  );
}
