// WebSerialWidget.jsx - Conexão Direta Browser <-> ESP32 via Web Serial API
import React, { useState, useEffect } from 'react';
import { Usb, Plugs, PlugsConnected, WarningCircle } from '@phosphor-icons/react';
import webSerial from '../services/webSerial';
import audioAlerts from '../services/audioAlerts';

export default function WebSerialWidget({ onDataReceived }) {
  const isSupported = webSerial.isSupported();
  const [isConnected, setIsConnected] = useState(webSerial.isConnected);
  const [baudRate, setBaudRate] = useState(115200);
  const [isOpen, setIsOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [rxCount, setRxCount] = useState(0);

  useEffect(() => {
    const unsubStatus = webSerial.onStatusChange(statusObj => {
      setIsConnected(statusObj.isConnected);
      if (statusObj.isConnected) {
        setErrorMsg('');
        audioAlerts.playInfo();
      }
    });

    const unsubData = webSerial.onData((data, raw) => {
      setRxCount(prev => prev + 1);
      if (onDataReceived) {
        onDataReceived(data);
      }
    });

    return () => {
      unsubStatus();
      unsubData();
    };
  }, [onDataReceived]);

  const handleConnect = async () => {
    try {
      setErrorMsg('');
      await webSerial.connect(baudRate);
      setIsOpen(false);
    } catch (err) {
      if (err.name !== 'NotFoundError') { // Ignora se usuário apenas cancelou o diálogo do browser
        setErrorMsg(err.message || 'Erro ao conectar na porta serial.');
      }
    }
  };

  const handleDisconnect = async () => {
    await webSerial.disconnect();
    audioAlerts.playSignalLost();
  };

  if (!isSupported) {
    return null; // Oculta se o navegador não der suporte
  }

  return (
    <>
      {/* Botão de Status no Header / Toolbar */}
      <button
        onClick={() => setIsOpen(true)}
        className={`btn text-xs font-mono transition-all duration-200 flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${
          isConnected
            ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.2)]'
            : 'bg-slate-800/60 border-slate-700/60 text-slate-300 hover:border-slate-500'
        }`}
        title={isConnected ? 'Conectado via USB Web Serial' : 'Conectar ESP32 direto via Web Serial'}
      >
        <Usb size={14} className={isConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-400'} />
        <span>{isConnected ? `WebSerial (${rxCount} pkts)` : 'USB Direto'}</span>
        <span className={`led ${isConnected ? 'led-green' : 'led-red'}`} />
      </button>

      {/* Modal de Configuração Web Serial */}
      {isOpen && (
        <div className="modal-overlay">
          <div className="modal-content max-w-md bg-slate-900/95 border border-cyan-500/30 rounded-2xl p-6 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
              <div className="flex items-center gap-2.5 text-cyan-400">
                <Usb size={22} weight="bold" />
                <h3 className="font-bold text-sm tracking-wide uppercase text-white">Web Serial API (Backup Direto)</h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white text-lg font-mono leading-none"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              Permite que este navegador leia os pacotes de telemetria diretamente da porta USB do receptor ESP32/LoRa, funcionando mesmo se o backend Node.js estiver offline.
            </p>

            {errorMsg && (
              <div className="flex items-center gap-2 p-3 bg-red-500/15 border border-red-500/40 rounded-xl text-red-300 text-xs mb-4">
                <WarningCircle size={18} className="flex-shrink-0 text-red-400" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Baud Rate (Velocidade)
                </label>
                <select
                  value={baudRate}
                  onChange={e => setBaudRate(e.target.value)}
                  disabled={isConnected}
                  className="w-full bg-slate-800 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400 font-mono"
                >
                  <option value={115200}>115200 (Padrão ESP32 Leviatã)</option>
                  <option value={57600}>57600</option>
                  <option value={38400}>38400</option>
                  <option value={19200}>19200</option>
                  <option value={9600}>9600</option>
                </select>
              </div>

              <div className="pt-2 flex gap-3">
                {isConnected ? (
                  <button
                    onClick={handleDisconnect}
                    className="flex-1 btn btn-danger-fill py-2.5 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg"
                  >
                    <Plugs size={16} weight="bold" />
                    Desconectar USB
                  </button>
                ) : (
                  <button
                    onClick={handleConnect}
                    className="flex-1 btn btn-accent py-2.5 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20"
                  >
                    <PlugsConnected size={16} weight="bold" />
                    Selecionar Porta USB & Conectar
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="btn px-4 py-2.5 rounded-xl text-slate-300 border-white/10 hover:bg-white/10"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
