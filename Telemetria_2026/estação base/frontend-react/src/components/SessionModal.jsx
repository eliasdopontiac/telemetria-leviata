import React, { useState, useEffect } from 'react';
import { X, FolderKanban, Plus, Download, Trash2, CheckCircle2 } from 'lucide-react';
import { fetchSessoes, criarSessao, setSessaoAtiva, deletarSessao, getDownloadCsvUrl } from '../services/api';

export default function SessionModal({ isOpen, onClose, sessaoAtiva, onSessaoChanged }) {
  const [sessoes, setSessoes] = useState([]);
  const [novoNome, setNovoNome] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async () => { setLoading(true); try { setSessoes(await fetchSessoes() || []); } catch (e) { setError(e.message); } finally { setLoading(false); } };
  useEffect(() => { if (isOpen) load(); }, [isOpen]);
  if (!isOpen) return null;

  const criar = async (e) => { e.preventDefault(); if (!novoNome.trim()) return; setLoading(true); try { const n = await criarSessao(novoNome.trim()); setNovoNome(''); await load(); onSessaoChanged(n); } catch (er) { setError(er.message); } finally { setLoading(false); } };
  const selecionar = async (id) => { setLoading(true); try { onSessaoChanged(await setSessaoAtiva(id)); } catch (e) { setError(e.message); } finally { setLoading(false); } };
  const deletar = async (id, nome) => { if (!window.confirm(`Excluir "${nome}"?`)) return; setLoading(true); try { await deletarSessao(id); await load(); } catch (e) { setError(e.message); } finally { setLoading(false); } };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: 560 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 12, marginBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}><FolderKanban style={{ width: 18, height: 18, color: '#00f2fe' }} /><h3 style={{ fontSize: 15, fontWeight: 700 }}>Sessões de Telemetria</h3></div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)' }}><X style={{ width: 18, height: 18 }} /></button>
        </div>

        <form onSubmit={criar} style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
          <input type="text" placeholder="Nome da nova sessão..." value={novoNome} onChange={e => setNovoNome(e.target.value)} style={{ flex: 1, background: '#070a11', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-main)', borderRadius: 8, padding: '6px 10px', fontSize: 12 }} />
          <button type="submit" className="btn btn-accent" disabled={loading || !novoNome.trim()} style={{ fontSize: 11 }}><Plus style={{ width: 14, height: 14 }} />Criar</button>
        </form>

        {error && <div style={{ marginBottom: 10, padding: 8, borderRadius: 8, background: 'rgba(255,23,68,0.08)', border: '1px solid rgba(255,23,68,0.3)', color: '#fca5a5', fontSize: 11 }}>{error}</div>}

        <div style={{ maxHeight: 280, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
          {sessoes.length === 0 ? <p style={{ fontSize: 11, color: 'var(--text-dim)', textAlign: 'center', padding: 16 }}>Nenhuma sessão.</p> : sessoes.map(s => {
            const isAtiva = sessaoAtiva?.id === s.id;
            return (
              <div key={s.id} style={{ padding: 10, borderRadius: 10, border: `1px solid ${isAtiva ? 'rgba(0,242,254,0.4)' : 'rgba(255,255,255,0.06)'}`, background: isAtiva ? 'rgba(0,242,254,0.06)' : 'rgba(15,23,42,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <strong style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.nome}</strong>
                    {isAtiva && <span style={{ fontSize: 9, fontWeight: 800, padding: '1px 6px', borderRadius: 6, background: 'rgba(0,242,254,0.15)', color: '#00f2fe', border: '1px solid rgba(0,242,254,0.3)' }}>ATIVA</span>}
                  </div>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{new Date(s.criado_em).toLocaleString('pt-BR')}</span>
                </div>
                <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                  {!isAtiva && <button className="btn" style={{ fontSize: 10, padding: '3px 8px' }} onClick={() => selecionar(s.id)} disabled={loading}><CheckCircle2 style={{ width: 12, height: 12, color: '#00f2fe' }} />Ativar</button>}
                  <a className="btn" style={{ fontSize: 10, padding: '3px 8px' }} href={getDownloadCsvUrl(s.id)} download><Download style={{ width: 12, height: 12, color: '#ffb703' }} />CSV</a>
                  <button onClick={() => deletar(s.id, s.nome)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', padding: 4, borderRadius: 6 }}><Trash2 style={{ width: 14, height: 14 }} /></button>
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 14, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          <button className="btn" onClick={onClose}>Fechar</button>
        </div>
      </div>
    </div>
  );
}
