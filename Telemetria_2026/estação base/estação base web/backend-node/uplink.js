const fs = require('fs');
const path = require('path');
const dbModule = require('./database');

class UplinkManager {
  constructor(io = null) {
    this.io = io;
    this.configPath = path.join(__dirname, 'config_online.json');
    this.urlServidor = '';
    this.intervaloMs = 1000;
    this.timer = null;
    this.enviando = false;
    this.status = {
      conectado: false,
      pendentes: 0,
      ultimoEnvio: null,
      erro: null,
      url: ''
    };
    this.carregarConfig();
  }

  carregarConfig() {
    try {
      if (fs.existsSync(this.configPath)) {
        const raw = fs.readFileSync(this.configPath, 'utf8');
        const cfg = JSON.parse(raw);
        this.urlServidor = (cfg.url_servidor_online || '').trim();
      } else {
        this.urlServidor = '';
      }
      this.status.url = this.urlServidor;
      this.notificarStatus();
    } catch (err) {
      console.error('[Uplink] Erro ao ler config_online.json:', err.message);
    }
  }

  notificarStatus() {
    if (this.io) {
      this.io.emit('uplink_status', this.status);
    }
  }

  iniciar() {
    if (this.timer) return;
    this.timer = setInterval(() => this.processarFila(), this.intervaloMs);
    console.log('[Uplink] Fila de sincronização iniciada.');
  }

  parar() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  async processarFila() {
    if (this.enviando) return;
    this.carregarConfig();

    try {
      const pendentes = await dbModule.getPacotesPendentes(50);
      this.status.pendentes = pendentes.length;

      if (!this.urlServidor) {
        this.status.conectado = false;
        this.status.erro = 'Aguardando definição da URL do servidor online';
        this.notificarStatus();
        return;
      }

      if (pendentes.length === 0) {
        this.status.conectado = true;
        this.status.erro = null;
        this.notificarStatus();
        return;
      }

      this.enviando = true;

      // Monta lote de pacotes para o ingest
      const lote = pendentes.map(row => ({
        uid: row.uid || `${row.id}-${row.timestamp_iso}`,
        timestamp_iso: row.timestamp_iso,
        payload: {
          solar: { tensao: row.v_solar, corrente: row.i_solar, pot: row.pot_solar },
          bateria: { soc: row.soc, tensao_bat: row.v_bat, corrente_liq: row.i_liq },
          prop: { rpm: row.rpm, i_motor: row.i_motor, t_motor: row.t_motor, t_ctrl: row.t_ctrl, fardriver_falha: row.falha_ctrl },
          nav: { vel: row.vel, lat: row.lat, lon: row.lon, proa: row.proa, gps_satelites: row.gps_satelites, gps_hora: row.gps_hora, hdop: row.hdop },
          sinal: { lora: row.sinal_lora, lte: row.sinal_lte, lora_pacotes: row.pkt_seq },
          v_sist: row.v_sist,
          status_data: row.status_data
        }
      }));

      // Faz envio via HTTP POST /api/ingest
      const targetUrl = this.urlServidor.replace(/\/+$/, '') + '/api/ingest';
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);

      const resp = await fetch(targetUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pacotes: lote }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!resp.ok) {
        throw new Error(`Servidor respondeu com status ${resp.status}`);
      }

      const data = await resp.json();
      const uidsConfirmados = data.recebidos || lote.map(p => p.uid);

      await dbModule.marcarPacotesEnviados(uidsConfirmados);

      this.status.conectado = true;
      this.status.ultimoEnvio = new Date().toISOString();
      this.status.erro = null;
      this.status.pendentes = Math.max(0, this.status.pendentes - uidsConfirmados.length);
      this.notificarStatus();

    } catch (err) {
      this.status.conectado = false;
      this.status.erro = err.message || 'Falha de comunicação com servidor online';
      this.notificarStatus();
    } finally {
      this.enviando = false;
    }
  }
}

module.exports = UplinkManager;
