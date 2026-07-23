import React from 'react';
import { NavLink } from 'react-router-dom';
import { FolderSimple, Cpu, WifiHigh, WifiSlash, DownloadSimple, ChartLineUp, SquaresFour } from '@phosphor-icons/react';
import Lottie from './LottieWrapper';
import LeviataLogo from './LeviataLogo';
import { radarPulseLottie } from '../assets/lottieAnimations';
import { getDownloadCsvUrl } from '../services/api';

export default function Header({
  isConnected, sessaoAtiva, serialStatus, lastUpdated,
  onOpenSessionModal, onOpenSerialModal
}) {
  return (
    <header className="app-header">
      <div className="header-brand" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <LeviataLogo height={38} />
        <div style={{ borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: 10 }}>
          <p style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', letterSpacing: 1.5, fontWeight: 700 }}>TELEMETRIA 2026</p>
        </div>
      </div>

      <div className="header-controls">
        <div style={{ display: 'flex', gap: '4px', backgroundColor: 'var(--bg-dark)', padding: '2px', borderRadius: '8px', border: '1px solid var(--border-glass)', marginRight: '8px' }}>
          <NavLink to="/" className={({ isActive }) => `btn ${isActive ? 'btn-active' : ''}`} style={{ padding: '6px 12px' }}>
            <SquaresFour size={14} weight="duotone" /> Visão Geral
          </NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `btn ${isActive ? 'btn-active' : ''}`} style={{ padding: '6px 12px' }}>
            <ChartLineUp size={14} weight="duotone" /> Gráficos
          </NavLink>
        </div>

        <button className="btn" onClick={onOpenSessionModal} title="Gerenciar Sessões">
          <FolderSimple size={14} weight="duotone" color="#00f2fe" />
          <span style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {sessaoAtiva?.nome || 'Nenhuma Sessão'}
          </span>
        </button>

        {sessaoAtiva && (
          <a className="btn" href={getDownloadCsvUrl(sessaoAtiva.id)} download title="Baixar CSV">
            <DownloadSimple size={14} weight="duotone" color="#ffb703" />CSV
          </a>
        )}

        <button className="btn" onClick={onOpenSerialModal} title="Porta Serial USB"
          style={serialStatus?.status === 'connected' ? { borderColor: 'rgba(0,230,118,0.4)' } : {}}>
          <Cpu size={14} weight="duotone" color="#ffb703" />
          <span>{serialStatus?.status === 'connected' ? `LoRa (${serialStatus.port})` : 'Serial Off'}</span>
          <span className={`led ${serialStatus?.status === 'connected' ? 'led-green' : 'led-red'}`} />
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
            ? (
              <>
                <WifiHigh size={14} weight="duotone" color="#00e676" />
                <span style={{ color: '#00e676', fontWeight: 700 }}>ONLINE</span>
                <div style={{ width: 16, height: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Lottie animationData={radarPulseLottie} loop={true} style={{ width: 22, height: 22 }} />
                </div>
              </>
            )
            : <><WifiSlash size={14} weight="duotone" color="#ff1744" /><span style={{ color: '#ff1744', fontWeight: 700 }}>OFFLINE</span><span className="led led-red" /></>
          }
        </div>
      </div>
    </header>
  );
}
