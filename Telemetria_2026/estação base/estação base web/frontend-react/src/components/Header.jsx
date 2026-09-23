import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  FolderSimple, Cpu, WifiHigh, WifiSlash, DownloadSimple,
  ChartLineUp, SquaresFour, SpeakerHigh, SpeakerSlash,
  FilePdf, FileXls, CaretDown
} from '@phosphor-icons/react';
import Lottie from './LottieWrapper';
import LeviataLogo from './LeviataLogo';
import { radarPulseLottie } from '../assets/lottieAnimations';
import { getDownloadCsvUrl } from '../services/api';
import WebSerialWidget from './WebSerialWidget';
import audioAlerts from '../services/audioAlerts';
import { exportarRelatorioPDF, exportarPlanilhaExcel } from '../services/exportService';

export default function Header({
  isConnected, sessaoAtiva, serialStatus, lastUpdated, history,
  onOpenSessionModal, onOpenSerialModal, onWebSerialData
}) {
  const [isMuted, setIsMuted] = useState(audioAlerts.isMuted());
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const toggleSound = () => {
    const muted = audioAlerts.toggleMute();
    setIsMuted(muted);
  };

  const handleExportPDF = async () => {
    try {
      setIsExporting(true);
      setIsExportOpen(false);
      audioAlerts.playInfo();
      await exportarRelatorioPDF(sessaoAtiva, history || []);
    } catch (e) {
      console.error('Erro ao gerar PDF:', e);
      alert('Erro ao gerar relatório PDF: ' + e.message);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      setIsExporting(true);
      setIsExportOpen(false);
      audioAlerts.playInfo();
      await exportarPlanilhaExcel(sessaoAtiva, history || []);
    } catch (e) {
      console.error('Erro ao gerar Excel:', e);
      alert('Erro ao exportar planilha Excel: ' + e.message);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <header className="app-header">
      <div className="header-brand" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <LeviataLogo height={38} />
        <div style={{ borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: 10 }}>
          <p style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', letterSpacing: 1.5, fontWeight: 700 }}>TELEMETRIA 2026</p>
        </div>
      </div>

      <div className="header-controls">
        {/* Navegação entre Páginas */}
        <div style={{ display: 'flex', gap: '4px', backgroundColor: 'var(--bg-dark)', padding: '2px', borderRadius: '8px', border: '1px solid var(--border-glass)', marginRight: '8px' }}>
          <NavLink to="/" className={({ isActive }) => `btn ${isActive ? 'btn-active' : ''}`} style={{ padding: '6px 12px' }}>
            <SquaresFour size={14} weight="duotone" /> Visão Geral
          </NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `btn ${isActive ? 'btn-active' : ''}`} style={{ padding: '6px 12px' }}>
            <ChartLineUp size={14} weight="duotone" /> Gráficos
          </NavLink>
        </div>

        {/* Gerenciamento de Sessão */}
        <button className="btn" onClick={onOpenSessionModal} title="Gerenciar Sessões">
          <FolderSimple size={14} weight="duotone" className="text-slate-400" />
          <span style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {sessaoAtiva?.nome || 'Nenhuma Sessão'}
          </span>
        </button>

        {/* Menu Dropdown de Exportação (PDF / Excel / CSV) */}
        <div className="relative inline-block text-left">
          <button
            className={`btn transition-all ${isExportOpen ? 'btn-active' : ''}`}
            onClick={() => setIsExportOpen(!isExportOpen)}
            title="Exportar Dados da Sessão"
          >
            <DownloadSimple size={14} weight="duotone" className="text-slate-400" />
            <span>Exportar</span>
            <CaretDown size={10} className="text-slate-500" />
          </button>

          {isExportOpen && (
            <div className="export-dropdown absolute right-0 mt-1.5 w-48 rounded-xl bg-slate-900/95 border border-cyan-500/30 shadow-2xl backdrop-blur-md z-50 py-1.5 font-mono text-xs">
              <button
                onClick={handleExportPDF}
                disabled={isExporting}
                className="w-full text-left px-3 py-2 flex items-center gap-2 text-slate-200 hover:bg-cyan-500/15 hover:text-cyan-300 transition-colors"
              >
                <FilePdf size={16} weight="duotone" className="text-red-400" />
                <span>Relatório PDF</span>
              </button>
              <button
                onClick={handleExportExcel}
                disabled={isExporting}
                className="w-full text-left px-3 py-2 flex items-center gap-2 text-slate-200 hover:bg-cyan-500/15 hover:text-cyan-300 transition-colors"
              >
                <FileXls size={16} weight="duotone" className="text-emerald-400" />
                <span>Planilha Excel (.xlsx)</span>
              </button>
              {sessaoAtiva && (
                <a
                  href={getDownloadCsvUrl(sessaoAtiva.id)}
                  download
                  onClick={() => setIsExportOpen(false)}
                  className="w-full text-left px-3 py-2 flex items-center gap-2 text-slate-200 hover:bg-cyan-500/15 hover:text-cyan-300 transition-colors block"
                >
                  <DownloadSimple size={16} weight="duotone" className="text-amber-400" />
                  <span>Arquivo CSV Bruto</span>
                </a>
              )}
            </div>
          )}
        </div>

        {/* Status Serial Backend */}
        <button
          className="btn"
          onClick={onOpenSerialModal}
          title="Porta Serial USB via Backend"
          style={serialStatus?.status === 'connected' ? { borderColor: 'rgba(0,230,118,0.4)' } : {}}
        >
          <Cpu size={14} weight="duotone" className={serialStatus?.status === 'connected' ? "text-emerald-400" : "text-slate-400"} />
          <span>{serialStatus?.status === 'connected' ? `LoRa (${serialStatus.port})` : 'Serial Server'}</span>
          <span className={`led ${serialStatus?.status === 'connected' ? 'led-green' : 'led-red'}`} />
        </button>

        {/* Widget Web Serial Direto (Browser <-> ESP32) */}
        <WebSerialWidget onDataReceived={onWebSerialData} />

        {/* Botão de Som / Alertas Sonoros */}
        <button
          className={`btn transition-colors ${isMuted ? 'text-slate-500 border-slate-700/50' : 'text-cyan-300 border-cyan-500/30 bg-cyan-500/10'}`}
          onClick={toggleSound}
          title={isMuted ? 'Sons desativados (clique para ativar)' : 'Sons de alerta ativos (clique para silenciar)'}
        >
          {isMuted ? <SpeakerSlash size={14} weight="bold" /> : <SpeakerHigh size={14} weight="bold" />}
          <span>{isMuted ? 'Mudo' : 'Som On'}</span>
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
            : (
              <>
                <WifiSlash size={14} weight="duotone" color="#ff1744" />
                <span style={{ color: '#ff1744', fontWeight: 700 }}>OFFLINE</span>
                <span className="led led-red" />
              </>
            )
          }
        </div>
      </div>
    </header>
  );
}
