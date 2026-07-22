import React, { useState, useEffect } from 'react';
import { socket } from './services/socket';
import { fetchSessaoAtiva, fetchHistoricoSessao, toggleSimulador } from './services/api';

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Header from './components/Header';
import SerialModal from './components/SerialModal';
import SessionModal from './components/SessionModal';

import DashboardPage from './pages/DashboardPage';
import AnalyticsPage from './pages/AnalyticsPage';



const DEFAULT_TELEMETRY = {
  solar: { tensao: 0, corrente: 0, pot: 0 },
  bateria: { soc: 0, tensao_bat: 0, corrente_liq: 0 },
  prop: { rpm: 0, i_motor: 0, t_motor: 0, t_ctrl: 0, fardriver_falha: 0 },
  nav: { vel: 0, proa: 0, lat: -3.119, lon: -60.021, gps_satelites: 0, gps_hora: '--:--:--' },
  sinal: { lora: 0, lte: 0, lora_pacotes: 0 },
  v_sist: 0, status_data: 'valid'
};

export default function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [sessaoAtiva, setSessaoAtiva] = useState(null);
  const [serialStatus, setSerialStatus] = useState({ status: 'disconnected', port: null });
  const [simuladorRunning, setSimuladorRunning] = useState(false);
  const [currentTelemetry, setCurrentTelemetry] = useState(DEFAULT_TELEMETRY);
  const [history, setHistory] = useState([]);
  const [isSerialModalOpen, setIsSerialModalOpen] = useState(false);
  const [isSessionModalOpen, setIsSessionModalOpen] = useState(false);

  const carregarDados = async () => {
    try {
      const ativa = await fetchSessaoAtiva();
      setSessaoAtiva(ativa);
      if (ativa) {
        const h = await fetchHistoricoSessao(ativa.id, 500);
        setHistory(h || []);
        if (h?.length > 0) setCurrentTelemetry(h[h.length - 1]);
      }
    } catch (err) { console.error('Backend offline:', err.message); }
  };

  useEffect(() => {
    carregarDados();
    socket.on('connect', () => setIsConnected(true));
    socket.on('disconnect', () => setIsConnected(false));
    socket.on('sessao_ativa', s => setSessaoAtiva(s));
    socket.on('sessao_alterada', s => { setSessaoAtiva(s); setHistory([]); if (s) carregarDados(); });
    socket.on('serial_status', s => setSerialStatus(s));
    socket.on('simulador_status', s => setSimuladorRunning(s.isRunning));
    socket.on('telemetria_data', r => { setCurrentTelemetry(r); setHistory(p => [...p.slice(-499), r]); });
    return () => { socket.off('connect'); socket.off('disconnect'); socket.off('sessao_ativa'); socket.off('sessao_alterada'); socket.off('serial_status'); socket.off('simulador_status'); socket.off('telemetria_data'); };
  }, []);

  const t = currentTelemetry || DEFAULT_TELEMETRY;

  const n = t.nav || {};
  const lastUpdated = n.gps_hora && n.gps_hora !== '--:--:--' ? n.gps_hora : (t.timestamp_iso ? new Date(t.timestamp_iso).toLocaleTimeString('pt-BR') : null);

  return (
    <Router>
      <div className="app-shell">
        <Header
          isConnected={isConnected} sessaoAtiva={sessaoAtiva} serialStatus={serialStatus}
          simuladorRunning={simuladorRunning} lastUpdated={lastUpdated}
          onOpenSessionModal={() => setIsSessionModalOpen(true)}
          onOpenSerialModal={() => setIsSerialModalOpen(true)}
          onToggleSimulador={async () => { try { await toggleSimulador(!simuladorRunning); } catch (e) { console.error(e); } }}
        />

        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage currentTelemetry={currentTelemetry} history={history} />} />
            <Route path="/analytics" element={<AnalyticsPage history={history} />} />
          </Routes>
        </div>

        {isSerialModalOpen && <SerialModal isOpen={isSerialModalOpen} onClose={() => setIsSerialModalOpen(false)} serialStatus={serialStatus} />}
        {isSessionModalOpen && <SessionModal isOpen={isSessionModalOpen} onClose={() => setIsSessionModalOpen(false)} sessaoAtiva={sessaoAtiva} onSessaoChanged={s => { setSessaoAtiva(s); setIsSessionModalOpen(false); }} />}
      </div>
    </Router>
  );
}
