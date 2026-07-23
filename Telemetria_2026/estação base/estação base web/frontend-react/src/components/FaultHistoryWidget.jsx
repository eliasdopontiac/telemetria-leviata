import React from 'react';
import { WarningCircle, CheckCircle, ShieldWarning } from '@phosphor-icons/react';

const fardriverErrorMap = {
  0: { label: 'Operação Normal', desc: 'Sem erros detectados', color: '#00e676', isCrit: false },
  1: { label: 'Sobretensão Bateria', desc: 'Tensão acima do limite seguro', color: '#ff1744', isCrit: true },
  2: { label: 'Subtensão Bateria', desc: 'Corte por descarga excessiva', color: '#ff9100', isCrit: true },
  3: { label: 'Sobrecorrente Motor', desc: 'Pico de corrente no motor', color: '#ff1744', isCrit: true },
  4: { label: 'Temp. Motor Elevada', desc: 'Superaquecimento (>85°C)', color: '#ff1744', isCrit: true },
  5: { label: 'Temp. Controlador Elevada', desc: 'Superaquecimento (>85°C)', color: '#ff9100', isCrit: true },
  6: { label: 'Falha Sensor Hall', desc: 'Erro na posição do rotor', color: '#ff9100', isCrit: true },
  7: { label: 'Falha Acelerador', desc: 'Sinal de Throttle inválido', color: '#ff1744', isCrit: true },
  8: { label: 'Perda Sinal CAN/Serial', desc: 'Sem comunicação com a base', color: '#ff9100', isCrit: true }
};

export default function FaultHistoryWidget({ history = [], currentTelemetry }) {
  const currentFault = currentTelemetry?.prop?.fardriver_falha ?? currentTelemetry?.falha_ctrl ?? 0;

  // Extrai todas as alterações de falhas no histórico
  const faultEvents = [];
  let lastRecordedFault = null;

  const reversed = [...history].reverse();
  reversed.forEach(item => {
    const code = item.prop?.fardriver_falha ?? item.falha_ctrl ?? 0;
    if (code !== lastRecordedFault) {
      lastRecordedFault = code;
      const hora = item.nav?.gps_hora && item.nav.gps_hora !== '--:--:--'
        ? item.nav.gps_hora
        : (item.timestamp_iso ? new Date(item.timestamp_iso).toLocaleTimeString('pt-BR') : 'Agora');
      
      faultEvents.push({
        id: item.id || Math.random(),
        code,
        hora,
        info: fardriverErrorMap[code] || { label: `Código ${code}`, desc: 'Erro desconhecido', color: '#ff9100', isCrit: true }
      });
    }
  });

  // Mostra até 4 eventos mais recentes
  const recentEvents = faultEvents.slice(0, 4);

  const currentInfo = fardriverErrorMap[currentFault] || { label: `Falha ${currentFault}`, desc: 'Código desconhecido', color: '#ff9100', isCrit: true };

  return (
    <div className="card" style={{ marginTop: '8px', flex: 1 }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <ShieldWarning size={15} weight="duotone" color={currentFault === 0 ? '#00e676' : '#ff1744'} />
          <span className="card-title">Histórico de Falhas (Fardriver)</span>
        </div>
        <span className="card-badge" style={{
          background: currentFault === 0 ? 'rgba(0,230,118,0.1)' : 'rgba(255,23,68,0.15)',
          color: currentFault === 0 ? '#00e676' : '#ff1744',
          borderColor: currentFault === 0 ? 'rgba(0,230,118,0.3)' : 'rgba(255,23,68,0.4)'
        }}>
          {currentFault === 0 ? 'NORMAL' : `FALHA (${currentFault})`}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 4 }}>
        {recentEvents.length === 0 ? (
          <div style={{ fontSize: 11, color: 'var(--text-dim)', textAlign: 'center', padding: '12px 0' }}>
            <CheckCircle size={18} weight="duotone" color="#00e676" style={{ margin: '0 auto 4px', display: 'block' }} />
            Nenhuma falha registrada na sessão.
          </div>
        ) : (
          recentEvents.map(evt => (
            <div key={evt.id} style={{
              display: 'flex',
              alignItems: 'center',
              justify: 'space-between',
              padding: '6px 8px',
              borderRadius: 8,
              background: evt.code === 0 ? 'rgba(255,255,255,0.02)' : 'rgba(255,23,68,0.08)',
              border: `1px solid ${evt.code === 0 ? 'rgba(255,255,255,0.05)' : 'rgba(255,23,68,0.25)'}`,
              fontSize: 11
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {evt.code === 0 ? (
                  <CheckCircle size={14} weight="fill" color="#00e676" />
                ) : (
                  <WarningCircle size={14} weight="fill" color={evt.info.color} />
                )}
                <div>
                  <strong style={{ color: evt.code === 0 ? '#f1f5f9' : evt.info.color, display: 'block', fontSize: 11 }}>
                    {evt.info.label}
                  </strong>
                  <span style={{ fontSize: 9, color: 'var(--text-dim)' }}>{evt.info.desc}</span>
                </div>
              </div>
              <span style={{ fontSize: 9, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                {evt.hora}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
