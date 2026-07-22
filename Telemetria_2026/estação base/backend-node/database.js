const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, 'telemetria.db');
const db = new sqlite3.Database(dbPath);

// Inicializa o esquema de tabelas
db.serialize(() => {
  // Tabela de Sessões
  db.run(`
    CREATE TABLE IF NOT EXISTS sessoes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nome TEXT NOT NULL,
      criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Tabela de Registros de Telemetria
  db.run(`
    CREATE TABLE IF NOT EXISTS registros_telemetria (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sessao_id INTEGER,
      timestamp_iso TEXT,
      fonte TEXT,
      v_solar REAL,
      i_solar REAL,
      pot_solar REAL,
      soc REAL,
      v_bat REAL,
      i_liq REAL,
      rpm REAL,
      i_motor REAL,
      t_motor REAL,
      t_ctrl REAL,
      falha_ctrl INTEGER,
      vel REAL,
      lat REAL,
      lon REAL,
      proa REAL,
      gps_satelites INTEGER,
      gps_hora TEXT,
      hdop REAL,
      sinal_lora REAL,
      sinal_lte REAL,
      pkt_seq INTEGER,
      v_sist REAL,
      status_data TEXT,
      FOREIGN KEY (sessao_id) REFERENCES sessoes(id) ON DELETE CASCADE
    )
  `);

  // Se não existir nenhuma sessão, cria a sessão Padrão
  db.get("SELECT COUNT(*) as count FROM sessoes", (err, row) => {
    if (!err && row.count === 0) {
      const dataHora = new Date().toLocaleString('pt-BR');
      db.run("INSERT INTO sessoes (nome) VALUES (?)", [`Sessão Inicial - ${dataHora}`]);
    }
  });
});

/**
 * Retorna todas as sessões
 */
function getSessoes() {
  return new Promise((resolve, reject) => {
    db.all("SELECT * FROM sessoes ORDER BY id DESC", [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

/**
 * Cria uma nova sessão
 */
function criarSessao(nome) {
  return new Promise((resolve, reject) => {
    db.run("INSERT INTO sessoes (nome) VALUES (?)", [nome], function (err) {
      if (err) reject(err);
      else resolve({ id: this.lastID, nome, criado_em: new Date().toISOString() });
    });
  });
}

/**
 * Exclui uma sessão e seus registros
 */
function deletarSessao(id) {
  return new Promise((resolve, reject) => {
    db.run("DELETE FROM sessoes WHERE id = ?", [id], (err) => {
      if (err) reject(err);
      else resolve(true);
    });
  });
}

/**
 * Obtém a sessão ativa mais recente
 */
function getSessaoAtivaOuUltima() {
  return new Promise((resolve, reject) => {
    db.get("SELECT * FROM sessoes ORDER BY id DESC LIMIT 1", [], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

/**
 * Insere um pacote de telemetria no banco
 */
function salvarTelemetria(sessaoId, rawPayload, fonte = 'serial') {
  return new Promise((resolve, reject) => {
    const tsIso = new Date().toISOString();
    let data = {};
    try {
      if (typeof rawPayload === 'string') {
        data = JSON.parse(rawPayload);
      } else {
        data = rawPayload;
      }
    } catch (e) {
      return reject(new Error('Payload JSON inválido'));
    }

    const s = data.solar || {};
    const b = data.bateria || {};
    const p = data.prop || {};
    const n = data.nav || {};
    const sig = data.sinal || {};

    const vSolar = parseFloat(s.tensao) || 0;
    const iSolar = parseFloat(s.corrente) || 0;
    const potSolar = parseFloat(s.pot) || 0;

    let vBat = parseFloat(b.tensao_bat) || 0;
    let statusData = 'valid';
    if (vBat <= 0 && vSolar > 0) {
      vBat = vSolar;
      statusData = 'solar_fallback';
    }

    const soc = parseFloat(b.soc) || 0;
    const iLiq = parseFloat(b.corrente_liq) || 0;

    const rpm = parseFloat(p.rpm) || 0;
    const iMotor = parseFloat(p.i_motor) || 0;
    const tMotor = parseFloat(p.t_motor) || 0;
    const tCtrl = parseFloat(p.t_ctrl) || 0;
    const falhaCtrl = parseInt(p.fardriver_falha, 10) || 0;

    const vel = parseFloat(n.vel) || 0;
    const lat = parseFloat(n.lat) || 0;
    const lon = parseFloat(n.lon) || 0;
    const proa = parseFloat(n.proa) || 0;
    const gpsSatelites = parseInt(n.gps_satelites, 10) || 0;
    const gpsHora = n.gps_hora || '--:--:--';
    const hdop = parseFloat(n.hdop) || 0;

    const sinalLora = parseFloat(sig.lora) || 0;
    const sinalLte = parseFloat(sig.lte) || 0;
    const pktSeq = parseInt(sig.lora_pacotes, 10) || 0;
    const vSist = parseFloat(data.v_sist) || 0;

    const query = `
      INSERT INTO registros_telemetria (
        sessao_id, timestamp_iso, fonte, v_solar, i_solar, pot_solar,
        soc, v_bat, i_liq, rpm, i_motor, t_motor, t_ctrl, falha_ctrl,
        vel, lat, lon, proa, gps_satelites, gps_hora, hdop,
        sinal_lora, sinal_lte, pkt_seq, v_sist, status_data
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    const params = [
      sessaoId, tsIso, fonte, vSolar, iSolar, potSolar,
      soc, vBat, iLiq, rpm, iMotor, tMotor, tCtrl, falhaCtrl,
      vel, lat, lon, proa, gpsSatelites, gpsHora, hdop,
      sinalLora, sinalLte, pktSeq, vSist, statusData
    ];

    db.run(query, params, function (err) {
      if (err) {
        reject(err);
      } else {
        const registro = {
          id: this.lastID,
          sessao_id: sessaoId,
          timestamp_iso: tsIso,
          fonte,
          solar: { tensao: vSolar, corrente: iSolar, pot: potSolar },
          bateria: { soc, tensao_bat: vBat, corrente_liq: iLiq },
          prop: { rpm, i_motor: iMotor, t_motor: tMotor, t_ctrl: tCtrl, fardriver_falha: falhaCtrl },
          nav: { vel, lat, lon, proa, gps_satelites: gpsSatelites, gps_hora: gpsHora, hdop },
          sinal: { lora: sinalLora, lte: sinalLte, lora_pacotes: pktSeq },
          v_sist: vSist,
          status_data: statusData
        };
        resolve(registro);
      }
    });
  });
}

/**
 * Busca histórico de telemetria por ID de sessão
 */
function getTelemetriaPorSessao(sessaoId, limit = 1000) {
  return new Promise((resolve, reject) => {
    const query = `
      SELECT * FROM registros_telemetria 
      WHERE sessao_id = ? 
      ORDER BY id ASC 
      LIMIT ?
    `;
    db.all(query, [sessaoId, limit], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

module.exports = {
  db,
  getSessoes,
  criarSessao,
  deletarSessao,
  getSessaoAtivaOuUltima,
  salvarTelemetria,
  getTelemetriaPorSessao
};
