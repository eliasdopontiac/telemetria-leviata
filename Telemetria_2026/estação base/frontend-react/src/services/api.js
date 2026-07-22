const getBaseUrl = () => {
  const host = window.location.hostname || 'localhost';
  return `http://${host}:3001`;
};

export const API_BASE = getBaseUrl();

export const fetchSessoes = async () => {
  const res = await fetch(`${API_BASE}/api/sessoes`);
  if (!res.ok) throw new Error('Erro ao buscar sessões');
  return res.json();
};

export const fetchSessaoAtiva = async () => {
  const res = await fetch(`${API_BASE}/api/sessoes/ativa`);
  if (!res.ok) throw new Error('Erro ao buscar sessão ativa');
  return res.json();
};

export const criarSessao = async (nome) => {
  const res = await fetch(`${API_BASE}/api/sessoes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome })
  });
  if (!res.ok) throw new Error('Erro ao criar sessão');
  return res.json();
};

export const setSessaoAtiva = async (id) => {
  const res = await fetch(`${API_BASE}/api/sessoes/ativa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  });
  if (!res.ok) throw new Error('Erro ao alterar sessão ativa');
  return res.json();
};

export const deletarSessao = async (id) => {
  const res = await fetch(`${API_BASE}/api/sessoes/${id}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Erro ao deletar sessão');
  return res.json();
};

export const fetchHistoricoSessao = async (sessaoId, limit = 500) => {
  const res = await fetch(`${API_BASE}/api/sessoes/${sessaoId}/telemetria?limit=${limit}`);
  if (!res.ok) throw new Error('Erro ao buscar histórico');
  return res.json();
};

export const getDownloadCsvUrl = (sessaoId) => {
  return `${API_BASE}/api/exportar-csv?sessao_id=${sessaoId}`;
};

export const fetchPortasSeriais = async () => {
  const res = await fetch(`${API_BASE}/api/portas-seriais`);
  if (!res.ok) throw new Error('Erro ao listar portas seriais');
  return res.json();
};

export const conectarSerial = async (portPath, baudRate = 115200) => {
  const res = await fetch(`${API_BASE}/api/conectar-serial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ portPath, baudRate })
  });
  if (!res.ok) throw new Error('Erro ao conectar porta serial');
  return res.json();
};

export const desconectarSerial = async () => {
  const res = await fetch(`${API_BASE}/api/desconectar-serial`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Erro ao desconectar porta serial');
  return res.json();
};

export const toggleSimulador = async (start = true) => {
  const endpoint = start ? '/api/simulador/start' : '/api/simulador/stop';
  const res = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
  if (!res.ok) throw new Error('Erro ao alternar simulador');
  return res.json();
};
