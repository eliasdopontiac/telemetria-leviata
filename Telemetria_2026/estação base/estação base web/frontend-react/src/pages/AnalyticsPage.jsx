import React from 'react';
import { ChartLineUp } from '@phosphor-icons/react';
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
        {history && history.length > 0 ? (
          <TelemetryCharts history={history} />
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-card)', borderRadius: '16px', border: '1px solid var(--border-glass)', boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.04)' }}>
            <div style={{ padding: '24px', textAlign: 'center', opacity: 0.6 }}>
              <ChartLineUp size={48} weight="duotone" className="text-slate-500" style={{ margin: '0 auto 16px auto' }} />
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: 'var(--text-main)', marginBottom: '8px' }}>Aguardando Telemetria</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-dim)', maxWidth: '300px', lineHeight: 1.5 }}>
                Inicie uma sessão ou conecte o dispositivo via USB para visualizar os gráficos em tempo real.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
