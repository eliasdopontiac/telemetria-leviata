import React, { useState, useEffect, useRef } from 'react';
import { X, Cpu, ArrowsClockwise, CheckCircle, WarningCircle, TerminalWindow } from '@phosphor-icons/react';
import { fetchPortasSeriais, conectarSerial, desconectarSerial } from '../services/api';
import { socket } from '../services/socket';

export default function SerialModal({ isOpen, onClose, serialStatus }) {
  const [portas, setPortas] = useState([]);
  const [selectedPort, setSelectedPort] = useState('');
  const [baudRate, setBaudRate] = useState('115200');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [logs, setLogs] = useState([]);
  const logEndRef = useRef(null);

  const load = async () => { 
    setLoading(true); 
    setError(''); 
    try { 
      const r = await fetchPortasSeriais(); 
      setPortas(r.portas || []); 
      if (r.portas?.length && !selectedPort) setSelectedPort(r.portas[0].path); 
    } catch (e) { 
      setError(e.message); 
    } finally { 
      setLoading(false); 
    } 
  };

  useEffect(() => { 
    if (isOpen) load(); 
  }, [isOpen]);

  useEffect(() => {
    const handleLog = (logItem) => {
      setLogs((prev) => [...prev.slice(-30), logItem]);
    };
    socket.on('serial_log', handleLog);
    return () => {
      socket.off('serial_log', handleLog);
    };
  }, []);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  if (!isOpen) return null;

  const connect = async () => { 
    if (!selectedPort) { 
      setError('Selecione uma porta.'); 
      return; 
    } 
    setLoading(true); 
    setError(''); 
    try { 
      await conectarSerial(selectedPort, baudRate); 
      onClose(); 
    } catch (e) { 
      setError(e.message); 
    } finally { 
      setLoading(false); 
    } 
  };

  const disconnect = async () => { 
    setLoading(true); 
    try { 
      await desconectarSerial(); 
      onClose(); 
    } catch (e) { 
      setError(e.message); 
    } finally { 
      setLoading(false); 
    } 
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: 500 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 12, marginBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Cpu size={18} weight="duotone" color="#ffb703" />
            <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-main)' }}>Porta Serial (LoRa USB)</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)' }}><X size={18} weight="bold" /></button>
        </div>

        <div style={{ marginBottom: 12, padding: 10, borderRadius: 10, background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
          <span style={{ color: 'var(--text-dim)' }}>Status: <strong style={{ color: serialStatus?.status === 'connected' ? '#00e676' : '#ff1744' }}>{serialStatus?.status === 'connected' ? `Conectado em ${serialStatus.port}` : 'Desconectado'}</strong></span>
          {serialStatus?.status === 'connected' && <button className="btn btn-danger-fill" style={{ fontSize: 10, padding: '3px 8px' }} onClick={disconnect} disabled={loading}>Desconectar</button>}
        </div>

        {error && <div style={{ marginBottom: 10, padding: 8, borderRadius: 8, background: 'rgba(255,23,68,0.08)', border: '1px solid rgba(255,23,68,0.3)', color: '#fca5a5', fontSize: 11, display: 'flex', gap: 6, alignItems: 'center' }}><WarningCircle size={14} weight="fill" style={{ flexShrink: 0 }} />{error}</div>}

        <div style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)' }}>Porta COM / USB:</label>
            <button className="btn" style={{ fontSize: 10, padding: '2px 6px' }} onClick={load} disabled={loading}><ArrowsClockwise size={11} weight="bold" style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />Atualizar</button>
          </div>
          <select value={selectedPort} onChange={e => setSelectedPort(e.target.value)} style={{ width: '100%', background: '#070a11', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-main)', borderRadius: 8, padding: 8, fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            {portas.length === 0 ? <option value="">Nenhuma porta encontrada</option> : portas.map(p => <option key={p.path} value={p.path}>{p.path} - {p.friendlyName || p.manufacturer}</option>)}
          </select>
        </div>

        <div style={{ marginBottom: 12 }}>
          <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Baud Rate:</label>
          <select value={baudRate} onChange={e => setBaudRate(e.target.value)} style={{ width: '100%', background: '#070a11', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-main)', borderRadius: 8, padding: 8, fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            <option value="115200">115200 (Padrão Heltec LoRa)</option><option value="9600">9600</option><option value="57600">57600</option>
          </select>
        </div>

        {/* Monitor Serial em Tempo Real */}
        <div style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 5 }}>
              <TerminalWindow size={13} weight="bold" color="#38bdf8" />
              Monitor Serial (Últimas Leituras):
            </span>
            {logs.length > 0 && (
              <button 
                type="button" 
                onClick={() => setLogs([])} 
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', fontSize: 10, cursor: 'pointer' }}
              >
                Limpar
              </button>
            )}
          </div>
          <div style={{
            background: '#040711',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 8,
            padding: '8px 10px',
            height: 90,
            overflowY: 'auto',
            fontFamily: 'var(--font-mono)',
            fontSize: 10,
            color: '#94a3b8'
          }}>
            {logs.length === 0 ? (
              <span style={{ color: '#475569', fontStyle: 'italic' }}>
                {serialStatus?.status === 'connected' ? 'Porta aberta. Aguardando pacotes do rádio...' : 'Conecte a porta serial para ver os dados brutos.'}
              </span>
            ) : (
              logs.map((l, idx) => (
                <div key={idx} style={{ 
                  color: l.type === 'warning' ? '#f59e0b' : (l.type === 'info' ? '#38bdf8' : '#cbd5e1'),
                  wordBreak: 'break-all',
                  marginBottom: 2
                }}>
                  {typeof l === 'string' ? l : l.text}
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <button className="btn" onClick={onClose}>Cancelar</button>
          <button className="btn btn-accent" onClick={connect} disabled={loading || !portas.length}><CheckCircle size={14} weight="duotone" />Conectar</button>
        </div>
      </div>
    </div>
  );
}
