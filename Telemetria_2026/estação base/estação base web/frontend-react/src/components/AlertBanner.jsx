import React from 'react';
import { ShieldWarning, Fire, BatteryLow, Sun } from '@phosphor-icons/react';
import Lottie from './LottieWrapper';
import { warningPulseLottie } from '../assets/lottieAnimations';

export default function AlertBanner({ telemetryData }) {
  if (!telemetryData) return null;
  const prop = telemetryData.prop || {};
  const bat = telemetryData.bateria || {};
  const statusData = telemetryData.status_data || '';
  const alerts = [];

  if (prop.fardriver_falha > 0) alerts.push({ id: 'f', type: 'critical', icon: ShieldWarning, title: `FALHA FARDRIVER (CÓD: ${prop.fardriver_falha})`, desc: 'Desligue o acelerador e verifique o motor.' });
  if (prop.t_motor > 60) alerts.push({ id: 'tm', type: 'warning', icon: Fire, title: `MOTOR QUENTE (${prop.t_motor.toFixed(1)} °C)`, desc: 'Monitore a corrente e o arrefecimento.' });
  if (prop.t_ctrl > 60) alerts.push({ id: 'tc', type: 'warning', icon: Fire, title: `CONTROLADOR QUENTE (${prop.t_ctrl.toFixed(1)} °C)`, desc: 'Verifique a ventilação.' });
  if (bat.soc > 0 && bat.soc < 25) alerts.push({ id: 'soc', type: 'warning', icon: BatteryLow, title: `BATERIA CRÍTICA (${bat.soc.toFixed(1)}%)`, desc: 'Economize energia.' });
  if (statusData.includes('solar_fallback')) alerts.push({ id: 'sf', type: 'info', icon: Sun, title: 'FALLBACK SOLAR ATIVO', desc: 'Usando tensão solar como referência.' });

  if (alerts.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, padding: '0 10px', flexShrink: 0 }}>
      {alerts.map(a => {
        const Icon = a.icon;
        const isCrit = a.type === 'critical';
        return (
          <div key={a.id} className={`alert-banner ${isCrit ? 'alert-critical' : 'alert-warning'}`}>
            <div className="alert-icon" style={{ background: isCrit ? '#ff1744' : '#ff9100', position: 'relative' }}>
              {isCrit && (
                <div style={{ position: 'absolute', inset: -8, pointerEvents: 'none' }}>
                  <Lottie animationData={warningPulseLottie} loop={true} style={{ width: '100%', height: '100%' }} />
                </div>
              )}
              <Icon size={16} weight="fill" color="#fff" style={{ position: 'relative', zIndex: 1 }} />
            </div>
            <div className="alert-text">
              <h4>{a.title}</h4>
              <p>{a.desc}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
