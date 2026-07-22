import React from 'react';
import { NavLink } from 'react-router-dom';
import { Radio, Play, Square, FolderKanban, Cpu, Wifi, WifiOff, Download, Activity, LayoutDashboard } from 'lucide-react';
import { getDownloadCsvUrl } from '../services/api';

export default function Header({
  isConnected, sessaoAtiva, serialStatus, simuladorRunning, lastUpdated,
  onOpenSessionModal, onOpenSerialModal, onToggleSimulador
}) {
  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="header-brand-icon"><Radio style={{ width: 16, height: 16, color: '#070a11' }} /></div>
        <div>
          <h1>LEVIATÃ 2026</h1>
          <p>TELEMETRIA PISTA</p>
        </div>
      </div>

      <div className="header-controls">
        <div style={{ display: 'flex', gap: '4px', backgroundColor: 'var(--bg-dark)', padding: '2px', borderRadius: '8px', border: '1px solid var(--border-glass)', marginRight: '8px' }}>
          <NavLink to="/" className={({ isActive }) => `btn ${isActive ? 'btn-active' : ''}`} style={{ padding: '6px 12px' }}>
            <LayoutDashboard style={{ width: 14, height: 14 }} /> Visão Geral
          </NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `btn ${isActive ? 'btn-active' : ''}`} style={{ padding: '6px 12px' }}>
            <Activity style={{ width: 14, height: 14 }} /> Gráficos
          </NavLink>
        </div>

        <button className="btn" onClick={onOpenSessionModal} title="Gerenciar Sessões">
          <FolderKanban style={{ width: 14, height: 14, color: '#00f2fe' }} />
          <span style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {sessaoAtiva?.nome || 'Nenhuma Sessão'}
          </span>
        </button>

        {sessaoAtiva && (
          <a className="btn" href={getDownloadCsvUrl(sessaoAtiva.id)} download title="Baixar CSV">
            <Download style={{ width: 14, height: 14, color: '#ffb703' }} />CSV
          </a>
        )}

        <button className="btn" onClick={onOpenSerialModal} title="Porta Serial USB"
          style={serialStatus?.status === 'connected' ? { borderColor: 'rgba(0,230,118,0.4)' } : {}}>
          <Cpu style={{ width: 14, height: 14, color: '#ffb703' }} />
          <span>{serialStatus?.status === 'connected' ? `LoRa (${serialStatus.port})` : 'Serial Off'}</span>
          <span className={`led ${serialStatus?.status === 'connected' ? 'led-green' : 'led-red'}`} />
        </button>

        <button
          className={`btn ${simuladorRunning ? 'btn-sim-active' : ''}`}
          onClick={onToggleSimulador}
        >
          {simuladorRunning
            ? <><Square style={{ width: 12, height: 12, fill: '#fbbf24', color: '#fbbf24' }} />Simulador ON</>
            : <><Play style={{ width: 12, height: 12, fill: '#00e676', color: '#00e676' }} />Simular</>
          }
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {lastUpdated && (
          <span style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', borderRight: '1px solid rgba(255,255,255,0.08)', paddingRight: 10 }}>
            {lastUpdated}
          </span>
        )}
        <div className="header-status">
          {isConnected
            ? <><Wifi style={{ width: 14, height: 14, color: '#00e676' }} /><span style={{ color: '#00e676', fontWeight: 700 }}>ONLINE</span><span className="led led-green" /></>
            : <><WifiOff style={{ width: 14, height: 14, color: '#ff1744' }} /><span style={{ color: '#ff1744', fontWeight: 700 }}>OFFLINE</span><span className="led led-red" /></>
          }
        </div>
      </div>
    </header>
  );
}
