import React, { useState, useEffect, useCallback } from 'react';
import { socket } from './services/socket';
import { fetchSessaoAtiva, fetchHistoricoSessao } from './services/api';
import audioAlerts from './services/audioAlerts';

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
    } catch (err) {
      console.warn('Backend offline ou inacessível:', err.message);
    }
  };

  // Handler para receber dados diretos da Web Serial API (modo backup)
  const handleWebSerialData = useCallback((data) => {
    if (!data) return;
    setCurrentTelemetry(data);
    setHistory(prev => [...prev.slice(-499), data]);
  }, []);

  useEffect(() => {
    carregarDados();

    const handleConnect = () => {
      setIsConnected(true);
      audioAlerts.playInfo();
    };

    const handleDisconnect = () => {
      setIsConnected(false);
      audioAlerts.playSignalLost();
    };

    const handleSessaoAtiva = (s) => setSessaoAtiva(s);

    const handleSessaoAlterada = (s) => {
      setSessaoAtiva(s);
      setHistory([]);
      if (s) carregarDados();
    };

    const handleSerialStatus = (s) => setSerialStatus(s);

    const handleTelemetriaData = (r) => {
      setCurrentTelemetry(r);
      setHistory(p => [...p.slice(-499), r]);
    };

    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('sessao_ativa', handleSessaoAtiva);
    socket.on('sessao_alterada', handleSessaoAlterada);
    socket.on('serial_status', handleSerialStatus);
    socket.on('telemetria_data', handleTelemetriaData);

    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('sessao_ativa', handleSessaoAtiva);
      socket.off('sessao_alterada', handleSessaoAlterada);
      socket.off('serial_status', handleSerialStatus);
      socket.off('telemetria_data', handleTelemetriaData);
    };
  }, []);

  const t = currentTelemetry || DEFAULT_TELEMETRY;
  const n = t.nav || {};
  const lastUpdated = n.gps_hora && n.gps_hora !== '--:--:--'
    ? n.gps_hora
    : (t.timestamp_iso ? new Date(t.timestamp_iso).toLocaleTimeString('pt-BR') : null);

  return (
    <Router>
      <div className="app-shell">
        <Header
          isConnected={isConnected}
          sessaoAtiva={sessaoAtiva}
          serialStatus={serialStatus}
          lastUpdated={lastUpdated}
          history={history}
          onOpenSessionModal={() => setIsSessionModalOpen(true)}
          onOpenSerialModal={() => setIsSerialModalOpen(true)}
          onWebSerialData={handleWebSerialData}
        />

        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage currentTelemetry={currentTelemetry} history={history} />} />
            <Route path="/analytics" element={<AnalyticsPage history={history} />} />
          </Routes>
        </div>

        {isSerialModalOpen && (
          <SerialModal
            isOpen={isSerialModalOpen}
            onClose={() => setIsSerialModalOpen(false)}
            serialStatus={serialStatus}
          />
        )}

        {isSessionModalOpen && (
          <SessionModal
            isOpen={isSessionModalOpen}
            onClose={() => setIsSessionModalOpen(false)}
            sessaoAtiva={sessaoAtiva}
            onSessaoChanged={(s) => {
              setSessaoAtiva(s);
              setIsSessionModalOpen(false);
            }}
          />
        )}
      </div>
    </Router>
  );
}
