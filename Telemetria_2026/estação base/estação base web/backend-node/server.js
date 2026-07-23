const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');

const dbModule = require('./database');
const serialManager = require('./serialManager');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST', 'DELETE']
  }
});

const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Estado em memória da sessão ativa
let sessaoAtiva = null;

// Inicializa a sessão ativa a partir do banco
(async () => {
  try {
    sessaoAtiva = await dbModule.getSessaoAtivaOuUltima();
    console.log(`[DB] Sessão ativa inicializada: ID ${sessaoAtiva?.id} - ${sessaoAtiva?.nome}`);
  } catch (err) {
    console.error('[DB] Erro ao carregar sessão inicial:', err);
  }
})();

// Processa e distribui dados de telemetria recebidos
async function processarEDistribuir(payload, fonte = 'serial') {
  if (!sessaoAtiva) {
    sessaoAtiva = await dbModule.getSessaoAtivaOuUltima();
  }
  if (!sessaoAtiva) return;

  try {
    const registroSalvo = await dbModule.salvarTelemetria(sessaoAtiva.id, payload, fonte);
    io.emit('telemetria_data', registroSalvo);
  } catch (err) {
    console.error(`[Telemetria] Erro ao processar payload (${fonte}):`, err.message);
  }
}

// Handler de dados vindo da Porta Serial
serialManager.onData((dataString) => {
  processarEDistribuir(dataString, 'serial');
});

// Handler de status da Porta Serial
serialManager.onStatusChange((statusObj) => {
  io.emit('serial_status', statusObj);
});

// --- ROTAS DA API REST ---

// Obter sessões
app.get('/api/sessoes', async (req, res) => {
  try {
    const sessoes = await dbModule.getSessoes();
    res.json(sessoes);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Obter sessão ativa
app.get('/api/sessoes/ativa', async (req, res) => {
  try {
    if (!sessaoAtiva) {
      sessaoAtiva = await dbModule.getSessaoAtivaOuUltima();
    }
    res.json(sessaoAtiva || null);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Criar nova sessão
app.post('/api/sessoes', async (req, res) => {
  try {
    const { nome } = req.body;
    if (!nome || !nome.trim()) {
      return res.status(400).json({ error: 'Nome da sessão é obrigatório.' });
    }
    const novaSessao = await dbModule.criarSessao(nome.trim());
    sessaoAtiva = novaSessao;
    io.emit('sessao_alterada', sessaoAtiva);
    res.json(novaSessao);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Definir sessão ativa existente
app.post('/api/sessoes/ativa', async (req, res) => {
  try {
    const { id } = req.body;
    const sessoes = await dbModule.getSessoes();
    const sel = sessoes.find(s => s.id === parseInt(id, 10));
    if (!sel) {
      return res.status(404).json({ error: 'Sessão não encontrada.' });
    }
    sessaoAtiva = sel;
    io.emit('sessao_alterada', sessaoAtiva);
    res.json(sessaoAtiva);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Deletar sessão
app.delete('/api/sessoes/:id', async (req, res) => {
  try {
    const { id } = req.params;
    await dbModule.deletarSessao(id);
    if (sessaoAtiva && sessaoAtiva.id === parseInt(id, 10)) {
      sessaoAtiva = await dbModule.getSessaoAtivaOuUltima();
      io.emit('sessao_alterada', sessaoAtiva);
    }
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Obter dados de telemetria da sessão
app.get('/api/sessoes/:id/telemetria', async (req, res) => {
  try {
    const { id } = req.params;
    const limit = req.query.limit ? parseInt(req.query.limit, 10) : 1000;
    const registros = await dbModule.getTelemetriaPorSessao(id, limit);
    res.json(registros);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Exportar CSV de uma sessão
app.get('/api/exportar-csv', async (req, res) => {
  try {
    const sessaoId = req.query.sessao_id || (sessaoAtiva ? sessaoAtiva.id : null);
    if (!sessaoId) {
      return res.status(400).json({ error: 'ID da sessão não fornecido.' });
    }

    const registros = await dbModule.getTelemetriaPorSessao(sessaoId, 100000);
    
    // Cabeçalhos compatíveis com backend original
    const headers = [
      'timestamp_iso', 'fonte', 'gps_hora', 'v_solar', 'i_solar', 'pot_solar',
      'soc', 'v_bat', 'i_liq', 'rpm', 'i_motor', 't_motor', 't_ctrl',
      'vel', 'lat', 'lon', 'sats', 'proa', 'hdop', 'lat_int', 'lon_int',
      'v_sist', 'falha_ctrl', 'pkt_seq', 'sig_lora', 'sig_lte', 'status_data'
    ];

    let csvContent = headers.join(',') + '\n';

    registros.forEach(row => {
      const line = [
        row.timestamp_iso || '',
        row.fonte || 'serial',
        row.gps_hora || '',
        row.v_solar || 0,
        row.i_solar || 0,
        row.pot_solar || 0,
        row.soc || 0,
        row.v_bat || 0,
        row.i_liq || 0,
        row.rpm || 0,
        row.i_motor || 0,
        row.t_motor || 0,
        row.t_ctrl || 0,
        row.vel || 0,
        row.lat || 0,
        row.lon || 0,
        row.gps_satelites || 0,
        row.proa || 0,
        row.hdop || 0,
        0, // lat_int
        0, // lon_int
        row.v_sist || 0,
        row.falha_ctrl || 0,
        row.pkt_seq || 0,
        row.sinal_lora || 0,
        row.sinal_lte || 0,
        row.status_data || 'valid'
      ].join(',');

      csvContent += line + '\n';
    });

    const filename = `telemetria_sessao_${sessaoId}.csv`;
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.send(csvContent);

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Portas Seriais
app.get('/api/portas-seriais', async (req, res) => {
  try {
    const portas = await serialManager.listPorts();
    res.json({
      portas,
      conectada: serialManager.isConnected,
      portaAtual: serialManager.currentPortPath
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/conectar-serial', async (req, res) => {
  try {
    const { portPath, baudRate } = req.body;
    if (!portPath) {
      return res.status(400).json({ error: 'Caminho da porta serial é obrigatório.' });
    }
    await serialManager.connect(portPath, baudRate || 115200);
    res.json({ success: true, portPath });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/desconectar-serial', async (req, res) => {
  try {
    await serialManager.disconnect();
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Servir a aplicação Frontend React estática (build de produção)
const frontendDistPath = path.join(__dirname, '../frontend-react/dist');
const fs = require('fs');

if (fs.existsSync(frontendDistPath)) {
  app.use(express.static(frontendDistPath));
  app.use((req, res, next) => {
    if (req.method === 'GET' && !req.path.startsWith('/api')) {
      return res.sendFile(path.join(frontendDistPath, 'index.html'));
    }
    next();
  });
  console.log(`[Static Web] Frontend servido a partir de: ${frontendDistPath}`);
}

// Real-time WebSocket handlers
io.on('connection', (socket) => {
  console.log(`[Socket.IO] Cliente conectado: ${socket.id}`);
  
  socket.emit('sessao_ativa', sessaoAtiva);
  socket.emit('serial_status', {
    status: serialManager.isConnected ? 'connected' : 'disconnected',
    port: serialManager.currentPortPath
  });

  socket.on('disconnect', () => {
    console.log(`[Socket.IO] Cliente desconectado: ${socket.id}`);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`=================================================`);
  console.log(` 🚀 SERVIDOR TELEMETRIA LEVIATÃ RODANDO`);
  console.log(` 🌐 PAINEL WEB DE PISTA: http://localhost:${PORT}`);
  console.log(` ⚡ WebSocket: ws://localhost:${PORT}`);
  console.log(`=================================================`);

  // Abrir o navegador automaticamente no Windows
  if (process.platform === 'win32') {
    const { exec } = require('child_process');
    exec(`start http://localhost:${PORT}`);
  }
});
