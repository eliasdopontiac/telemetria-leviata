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
async function processarEDistribuir(payload, fonte = 'serial', opts = {}) {
  if (!sessaoAtiva) {
    sessaoAtiva = await dbModule.getSessaoAtivaOuUltima();
  }
  if (!sessaoAtiva) return null;

  try {
    const registroSalvo = await dbModule.salvarTelemetria(sessaoAtiva.id, payload, fonte, opts);
    if (registroSalvo) {
      io.emit('telemetria_data', registroSalvo);
    }
    return registroSalvo;
  } catch (err) {
    console.error(`[Telemetria] Erro ao processar payload (${fonte}):`, err.message);
    return null;
  }
}

// Tratamento inteligente e resiliente de dados vindos da Porta Serial
function tratarDadoSerial(rawLine) {
  if (!rawLine) return;
  const line = String(rawLine).replace(/\0/g, '').trim();
  if (!line) return;

  // 1. Verificar se a linha contém JSON delimitado por '{' e '}'
  const startIdx = line.indexOf('{');
  const endIdx = line.lastIndexOf('}');

  if (startIdx !== -1 && endIdx > startIdx) {
    const jsonStr = line.substring(startIdx, endIdx + 1);
    const prefix = line.substring(0, startIdx).trim();

    // Se havia mensagem antes do JSON (ex: "IN_BYTES: AA 00 12 ...")
    if (prefix) {
      console.log(`[Serial LoRa Info]: ${prefix}`);
      io.emit('serial_log', { text: prefix, type: 'info', ts: new Date().toISOString() });
    }

    try {
      const parsed = JSON.parse(jsonStr);

      // Alertas específicos gerados pelo firmware (ex: {"erro_local":"Falha LoRa"})
      if (parsed.erro_local) {
        console.warn(`[Serial ESP32 Alerta]: ${parsed.erro_local}`);
        io.emit('serial_log', { text: `Alerta ESP32: ${parsed.erro_local}`, type: 'warning', ts: new Date().toISOString() });
        return;
      }

      // Processa e grava telemetria normalmente
      processarEDistribuir(parsed, 'serial');
      return;
    } catch (err) {
      console.warn(`[Serial] JSON encontrado com sintaxe incompleta: ${err.message} | Trecho: ${jsonStr}`);
    }
  }

  // 2. Formato CSV de telemetria legado (valores separados por vírgula)
  const parts = line.split(',');
  if (parts.length >= 6 && !isNaN(parseFloat(parts[0])) && !isNaN(parseFloat(parts[1]))) {
    try {
      const parsedCsv = {
        v_bat: parseFloat(parts[0]) || 0,
        i_liq: parseFloat(parts[1]) || 0,
        soc: parseFloat(parts[2]) || 0,
        v_solar: parseFloat(parts[3]) || 0,
        i_solar: parseFloat(parts[4]) || 0,
        pot_solar: parseFloat(parts[5]) || 0,
        rpm: parseInt(parts[6], 10) || 0,
        i_motor: parseFloat(parts[7]) || 0,
        t_motor: parseFloat(parts[8]) || 0,
        t_ctrl: parseFloat(parts[9]) || 0,
        vel: parseFloat(parts[10]) || 0,
        lat: parseFloat(parts[11]) || -22.41548354710283,
        lon: parseFloat(parts[12]) || -41.81782266355955,
        gps_satelites: parseInt(parts[13], 10) || 0,
        sinal_lora: parseInt(parts[14], 10) || 0
      };
      processarEDistribuir(parsedCsv, 'serial');
      return;
    } catch (err) {
      // Ignora erro de parsing CSV e segue para log normal
    }
  }

  // 3. Linha de texto comum / Log de Boot / Debug do Microcontrolador (ESP32)
  // Ex: "IN_BYTES: AA 00 ...", "STRUCT_SIZE=63", "LoRa OK", etc.
  console.log(`[Serial RX]: ${line}`);
  io.emit('serial_log', { text: line, type: 'debug', ts: new Date().toISOString() });
}

// Handler de dados vindo da Porta Serial
serialManager.onData((dataString) => {
  tratarDadoSerial(dataString);
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

// Deletar sessão (com proteção opcional de trava de segurança)
app.delete('/api/sessoes/:id', async (req, res) => {
  try {
    const { id } = req.params;
    if (process.env.TRAVAR_SESSOES === 'true') {
      return res.status(403).json({ error: 'Operação bloqueada: As sessões estão travadas para segurança da prova.' });
    }
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

// Endpoint de Ingestão de Telemetria Remota (Lote com Deduplicação)
app.post('/api/ingest', async (req, res) => {
  try {
    const { pacotes } = req.body;
    if (!pacotes || !Array.isArray(pacotes) || pacotes.length === 0) {
      return res.status(400).json({ error: 'Nenhum pacote enviado.' });
    }

    const recebidos = [];
    for (const item of pacotes) {
      const payload = item.payload || item;
      const uid = item.uid || payload.uid;
      const tsIso = item.timestamp_iso || payload.timestamp_iso;

      const salvo = await processarEDistribuir(payload, 'online_sync', {
        uid,
        timestamp_iso: tsIso,
        enviado: 1
      });

      if (salvo && salvo.uid) {
        recebidos.push(salvo.uid);
      } else if (uid) {
        recebidos.push(uid);
      }
    }

    res.json({ success: true, count: recebidos.length, recebidos });
  } catch (err) {
    console.error('[API Ingest] Erro ao processar lote:', err);
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

// Configuração Online (Computador B / Relé)
const configOnlinePath = path.join(__dirname, 'config_online.json');

app.get('/api/config-online', (req, res) => {
  try {
    if (fs.existsSync(configOnlinePath)) {
      const cfg = JSON.parse(fs.readFileSync(configOnlinePath, 'utf8'));
      return res.json(cfg);
    }
    res.json({ url_servidor_online: '', email_notificacao: {} });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/config-online', (req, res) => {
  try {
    const { url_servidor_online, email_notificacao } = req.body;
    let cfg = {};
    if (fs.existsSync(configOnlinePath)) {
      try { cfg = JSON.parse(fs.readFileSync(configOnlinePath, 'utf8')); } catch (_) {}
    }
    if (url_servidor_online !== undefined) cfg.url_servidor_online = url_servidor_online.trim();
    if (email_notificacao) cfg.email_notificacao = { ...cfg.email_notificacao, ...email_notificacao };

    fs.writeFileSync(configOnlinePath, JSON.stringify(cfg, null, 2), 'utf8');
    
    // Atualiza instância de uplink se ativa
    if (global.uplinkManager) {
      global.uplinkManager.carregarConfig();
    }

    res.json({ success: true, config: cfg });
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

  // Inicializa Uplink caso modo online esteja habilitado
  if (process.env.MODO_ONLINE === 'true' || process.env.HABILITAR_UPLINK === 'true') {
    try {
      const UplinkManager = require('./uplink');
      global.uplinkManager = new UplinkManager(io);
      global.uplinkManager.iniciar();
      console.log(' 📡 UPLINK ONLINE ATIVADO (Sincronização de Fila com Servidor Central)');
    } catch (err) {
      console.error(' [Uplink] Erro ao iniciar gerenciador:', err.message);
    }
  }

  // Abrir o navegador automaticamente no Windows
  if (process.platform === 'win32' && process.env.SEM_NAVEGADOR !== 'true') {
    const { exec } = require('child_process');
    exec(`start http://localhost:${PORT}`);
  }
});
