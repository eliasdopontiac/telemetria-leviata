import React, { useState } from 'react';
import { LockKey, ShieldCheck, X, WarningCircle } from '@phosphor-icons/react';
import { useAuth } from '../context/AuthContext';

export default function LoginModal() {
  const { isLoginModalOpen, setIsLoginModalOpen, loginTech } = useAuth();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  if (!isLoginModalOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    const res = loginTech(password);
    if (!res.success) {
      setError(res.error);
    } else {
      setPassword('');
    }
  };

  return (
    <div className="modal-overlay" onClick={() => setIsLoginModalOpen(false)}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: 380 }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ShieldCheck size={20} color="#00e5ff" weight="duotone" />
            <span style={{ fontWeight: 700, fontSize: 14 }}>Acesso Equipe Técnica</span>
          </div>
          <button className="btn-icon" onClick={() => setIsLoginModalOpen(false)}><X size={16} /></button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '16px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
          <p style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.4 }}>
            Insira a senha de operador para liberar os controles de hardware, porta serial, cronômetro e sessões.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
              SENHA DE EQUIPE:
            </label>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <input
                type="password"
                placeholder="Senha de acesso..."
                value={password}
                autoFocus
                onChange={e => setPassword(e.target.value)}
                style={{
                  width: '100%',
                  padding: '9px 12px 9px 34px',
                  borderRadius: 8,
                  background: 'rgba(0,0,0,0.3)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  color: '#fff',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 13
                }}
              />
              <LockKey size={16} color="var(--text-dim)" style={{ position: 'absolute', left: 10 }} />
            </div>
          </div>

          {error && (
            <div style={{
              fontSize: 11,
              fontFamily: 'var(--font-mono)',
              padding: '8px 10px',
              borderRadius: 6,
              background: 'rgba(255,23,68,0.15)',
              color: '#ff5252',
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}>
              <WarningCircle size={14} />
              <span>{error}</span>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
            <button type="button" className="btn" onClick={() => setIsLoginModalOpen(false)}>Cancelar</button>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ background: 'var(--accent-cyan)', color: '#000', fontWeight: 700 }}
            >
              Desbloquear
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
