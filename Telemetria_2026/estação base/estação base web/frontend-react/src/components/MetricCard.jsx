import React from 'react';

const colorSchemes = {
  primary:  { icon: 'rgba(0,242,254,0.1)', iconBorder: 'rgba(0,242,254,0.3)', iconText: '#00f2fe', value: '#00f2fe', bar: '#00f2fe' },
  solar:    { icon: 'rgba(255,183,3,0.1)',  iconBorder: 'rgba(255,183,3,0.3)',  iconText: '#ffb703', value: '#ffb703', bar: '#ffb703' },
  battery:  { icon: 'rgba(0,230,118,0.1)',  iconBorder: 'rgba(0,230,118,0.3)',  iconText: '#00e676', value: '#00e676', bar: '#00e676' },
  danger:   { icon: 'rgba(255,23,68,0.1)',  iconBorder: 'rgba(255,23,68,0.3)',  iconText: '#ff1744', value: '#ff1744', bar: '#ff1744' },
  warning:  { icon: 'rgba(255,145,0,0.1)',  iconBorder: 'rgba(255,145,0,0.3)',  iconText: '#ff9100', value: '#ff9100', bar: '#ff9100' },
};

export default function MetricCard({ title, value, unit, subtitle, icon: Icon, colorScheme = 'primary', progress, statusLed }) {
  const theme = colorSchemes[colorScheme] || colorSchemes.primary;

  return (
    <div className="metric-card">
      <div className="metric-top">
        <span className="metric-label">{title}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {statusLed && <span className={`led led-${statusLed}`} />}
          {Icon && (
            <div style={{ padding: 5, borderRadius: 8, border: `1px solid ${theme.iconBorder}`, background: theme.icon }}>
              <Icon size={14} weight="duotone" color={theme.iconText} />
            </div>
          )}
        </div>
      </div>

      <div className="metric-value-row">
        <span className="metric-value" style={{ color: theme.value, textShadow: `0 0 10px ${theme.value}40` }}>
          {value !== undefined && value !== null ? value : '--'}
        </span>
        {unit && <span className="metric-unit">{unit}</span>}
      </div>

      {subtitle && <div className="metric-subtitle">{subtitle}</div>}

      {typeof progress === 'number' && (
        <div className="metric-bar">
          <div className="metric-bar-fill" style={{ width: `${Math.min(100, Math.max(0, progress))}%`, background: theme.bar }} />
        </div>
      )}
    </div>
  );
}
