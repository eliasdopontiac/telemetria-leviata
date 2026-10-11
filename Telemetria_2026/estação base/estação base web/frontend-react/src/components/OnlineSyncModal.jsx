import React, { useState, useEffect } from 'react';
import { CloudArrowUp, CheckCircle, WarningCircle, ArrowClockwise, X } from '@phosphor-icons/react';

export default function OnlineSyncModal({ isOpen, onClose }) {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState(null);
  const [salvando, setSalvando] = useState(false);
  const [msg, setMsg] = useState('');

  const carregarConfig = async () => {
    try {
      const res = await fetch('/api/config-online');
      if (res.ok) {
        const data = await res.json();
        setUrl(data.url_servidor_online || '');
      }
    } catch (_) {}
  };

  useEffect(() => {
    if (isOpen) {
      carregarConfig();
      setMsg('');
    }
  }, [isOpen]);

  const handleSalvar = async (e) => {
    e.preventDefault();
    setSalvando(true);
    setMsg('');
    try {
      const res = await fetch('/api/config-online', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url_servidor_online: url.trim() })
      });
      if (res.ok) {
        setMsg('URL atualizada com sucesso! A fila sincronizará automaticamente.');
      } else {
        setMsg('Erro ao salvar configuração.');
      }
    } catch (err) {
      setMsg('Falha de conexão com backend local.');
    } finally {
      setSalvando(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: 460 }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CloudArrowUp size={20} color="#00e5ff" weight="duotone" />
            <span style={{ fontWeight: 700, fontSize: 14 }}>Sincronização Online (Uplink)</span>
          </div>
          <button className="btn-icon" onClick={onClose}><X size={16} /></button>
        </div>

        <form onSubmit={handleSalvar} style={{ padding: '16px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
          <p style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.4 }}>
            Cole aqui a URL pública gerada no <strong>Computador A</strong> (ex: link do Cloudflare recebido por e-mail). 
            Os pacotes serão enviados em tempo real e qualquer fila pendente será sincronizada.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
              URL DO SERVIDOR ONLINE:
            </label>
            <input
              type="text"
              placeholder="https://exemplo.trycloudflare.com"
              value={url}
              onChange={e => setUrl(e.target.value)}
              className="input-text"
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 8,
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid rgba(255,255,255,0.15)',
                color: '#fff',
                fontFamily: 'var(--font-mono)',
                fontSize: 12
              }}
            />
          </div>

          {msg && (
            <div style={{
              fontSize: 11,
              fontFamily: 'var(--font-mono)',
              padding: '8px 10px',
              borderRadius: 6,
              background: msg.includes('sucesso') ? 'rgba(0,230,118,0.15)' : 'rgba(255,23,68,0.15)',
              color: msg.includes('sucesso') ? '#00e676' : '#ff5252',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}>
              {msg.includes('sucesso') ? <CheckCircle size={14} /> : <WarningCircle size={14} />}
              <span>{msg}</span>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 10 }}>
            <button type="button" className="btn" onClick={onClose}>Fechar</button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={salvando}
              style={{ background: 'var(--accent-cyan)', color: '#000', fontWeight: 700 }}
            >
              {salvando ? 'Salvando...' : 'Aplicar URL'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
