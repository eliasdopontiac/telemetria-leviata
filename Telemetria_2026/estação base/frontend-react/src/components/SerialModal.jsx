import React, { useState, useEffect } from 'react';
import { X, Cpu, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { fetchPortasSeriais, conectarSerial, desconectarSerial } from '../services/api';

export default function SerialModal({ isOpen, onClose, serialStatus }) {
  const [portas, setPortas] = useState([]);
  const [selectedPort, setSelectedPort] = useState('');
  const [baudRate, setBaudRate] = useState('115200');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => { setLoading(true); setError(''); try { const r = await fetchPortasSeriais(); setPortas(r.portas || []); if (r.portas?.length && !selectedPort) setSelectedPort(r.portas[0].path); } catch (e) { setError(e.message); } finally { setLoading(false); } };
  useEffect(() => { if (isOpen) load(); }, [isOpen]);
  if (!isOpen) return null;

  const connect = async () => { if (!selectedPort) { setError('Selecione uma porta.'); return; } setLoading(true); setError(''); try { await conectarSerial(selectedPort, baudRate); onClose(); } catch (e) { setError(e.message); } finally { setLoading(false); } };
  const disconnect = async () => { setLoading(true); try { await desconectarSerial(); onClose(); } catch (e) { setError(e.message); } finally { setLoading(false); } };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 12, marginBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Cpu style={{ width: 18, height: 18, color: '#ffb703' }} />
            <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-main)' }}>Porta Serial (LoRa USB)</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)' }}><X style={{ width: 18, height: 18 }} /></button>
        </div>

        <div style={{ marginBottom: 12, padding: 10, borderRadius: 10, background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 11 }}>
          <span style={{ color: 'var(--text-dim)' }}>Status: <strong style={{ color: serialStatus?.status === 'connected' ? '#00e676' : '#ff1744' }}>{serialStatus?.status === 'connected' ? `Conectado em ${serialStatus.port}` : 'Desconectado'}</strong></span>
          {serialStatus?.status === 'connected' && <button className="btn btn-danger-fill" style={{ fontSize: 10, padding: '3px 8px' }} onClick={disconnect} disabled={loading}>Desconectar</button>}
        </div>

        {error && <div style={{ marginBottom: 10, padding: 8, borderRadius: 8, background: 'rgba(255,23,68,0.08)', border: '1px solid rgba(255,23,68,0.3)', color: '#fca5a5', fontSize: 11, display: 'flex', gap: 6, alignItems: 'center' }}><AlertCircle style={{ width: 14, height: 14, flexShrink: 0 }} />{error}</div>}

        <div style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)' }}>Porta COM / USB:</label>
            <button className="btn" style={{ fontSize: 10, padding: '2px 6px' }} onClick={load} disabled={loading}><RefreshCw style={{ width: 11, height: 11, animation: loading ? 'spin 1s linear infinite' : 'none' }} />Atualizar</button>
          </div>
          <select value={selectedPort} onChange={e => setSelectedPort(e.target.value)} style={{ width: '100%', background: '#070a11', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-main)', borderRadius: 8, padding: 8, fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            {portas.length === 0 ? <option value="">Nenhuma porta encontrada</option> : portas.map(p => <option key={p.path} value={p.path}>{p.path} - {p.friendlyName || p.manufacturer}</option>)}
          </select>
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Baud Rate:</label>
          <select value={baudRate} onChange={e => setBaudRate(e.target.value)} style={{ width: '100%', background: '#070a11', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-main)', borderRadius: 8, padding: 8, fontSize: 12, fontFamily: 'var(--font-mono)' }}>
            <option value="115200">115200 (Padrão Heltec LoRa)</option><option value="9600">9600</option><option value="57600">57600</option>
          </select>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <button className="btn" onClick={onClose}>Cancelar</button>
          <button className="btn btn-accent" onClick={connect} disabled={loading || !portas.length}><CheckCircle2 style={{ width: 14, height: 14 }} />Conectar</button>
        </div>
      </div>
    </div>
  );
}
