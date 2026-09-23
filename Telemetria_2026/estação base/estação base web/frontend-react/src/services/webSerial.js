// webSerial.js - Gerenciador Web Serial API para conexão direta Browser <-> ESP32 (Modo Standalone / Backup)

class WebSerialManager {
  constructor() {
    this.port = null;
    this.reader = null;
    this.readableStreamClosed = null;
    this.isConnected = false;
    this.dataCallbacks = [];
    this.statusCallbacks = [];
    this.buffer = '';
  }

  // Verifica se o navegador suporta Web Serial API
  isSupported() {
    return typeof navigator !== 'undefined' && 'serial' in navigator;
  }

  onData(callback) {
    this.dataCallbacks.push(callback);
    return () => {
      this.dataCallbacks = this.dataCallbacks.filter(cb => cb !== callback);
    };
  }

  onStatusChange(callback) {
    this.statusCallbacks.push(callback);
    return () => {
      this.statusCallbacks = this.statusCallbacks.filter(cb => cb !== callback);
    };
  }

  emitStatus(status, details = {}) {
    this.statusCallbacks.forEach(cb => {
      try {
        cb({ isConnected: this.isConnected, status, ...details });
      } catch (e) {
        console.error('[WebSerial] Erro no callback de status:', e);
      }
    });
  }

  // Solicita permissão ao usuário e conecta à porta
  async connect(baudRate = 115200) {
    if (!this.isSupported()) {
      throw new Error('Web Serial API não é suportada neste navegador. Use o Google Chrome, Edge ou Opera.');
    }

    try {
      // Abre o diálogo nativo do navegador para o usuário selecionar o dispositivo USB/ESP32
      this.port = await navigator.serial.requestPort();
      await this.port.open({ baudRate: parseInt(baudRate, 10) });

      this.isConnected = true;
      const portInfo = this.port.getInfo ? this.port.getInfo() : {};
      this.emitStatus('connected', { portInfo, baudRate });

      this.startReading();
      return true;
    } catch (err) {
      this.isConnected = false;
      this.port = null;
      this.emitStatus('error', { error: err.message });
      throw err;
    }
  }

  async startReading() {
    if (!this.port || !this.port.readable) return;

    try {
      const textDecoder = new TextDecoderStream();
      this.readableStreamClosed = this.port.readable.pipeTo(textDecoder.writable);
      this.reader = textDecoder.readable.getReader();

      while (this.isConnected) {
        const { value, done } = await this.reader.read();
        if (done) {
          break;
        }
        if (value) {
          this.handleIncomingChunk(value);
        }
      }
    } catch (err) {
      console.warn('[WebSerial] Erro na leitura do stream serial:', err);
    } finally {
      if (this.isConnected) {
        this.disconnect();
      }
    }
  }

  handleIncomingChunk(chunk) {
    this.buffer += chunk;
    const lines = this.buffer.split(/\r?\n/);
    // Guarda a última linha incompleta no buffer
    this.buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.length > 0) {
        this.parseLine(trimmed);
      }
    }
  }

  parseLine(line) {
    try {
      // Tenta decodificar formato JSON
      if (line.startsWith('{') && line.endsWith('}')) {
        const parsed = JSON.parse(line);
        this.notifyData(parsed, line);
        return;
      }

      // Tenta decodificar formato CSV/Separado por vírgula compatível com firmware ESP32
      const parts = line.split(',');
      if (parts.length >= 6) {
        const record = this.parseCsvProtocol(parts);
        this.notifyData(record, line);
      }
    } catch (e) {
      console.warn('[WebSerial] Linha serial ignorada ou não-JSON:', line);
    }
  }

  parseCsvProtocol(p) {
    // Parser fallback para telemetria em formato CSV comum de ESP32/LoRa
    const vBat = parseFloat(p[0]) || 0;
    const iLiq = parseFloat(p[1]) || 0;
    const soc = parseFloat(p[2]) || 0;
    const vSolar = parseFloat(p[3]) || 0;
    const iSolar = parseFloat(p[4]) || 0;
    const potSolar = parseFloat(p[5]) || (vSolar * iSolar);
    const rpm = parseInt(p[6], 10) || 0;
    const iMotor = parseFloat(p[7]) || 0;
    const tMotor = parseFloat(p[8]) || 0;
    const tCtrl = parseFloat(p[9]) || 0;
    const vel = parseFloat(p[10]) || 0;
    const lat = parseFloat(p[11]) || -3.119;
    const lon = parseFloat(p[12]) || -60.021;
    const sats = parseInt(p[13], 10) || 0;
    const lora = parseInt(p[14], 10) || 0;

    return {
      timestamp_iso: new Date().toISOString(),
      fonte: 'webserial',
      v_solar: vSolar,
      i_solar: iSolar,
      pot_solar: potSolar,
      soc: soc,
      v_bat: vBat,
      i_liq: iLiq,
      rpm: rpm,
      i_motor: iMotor,
      t_motor: tMotor,
      t_ctrl: tCtrl,
      vel: vel,
      lat: lat,
      lon: lon,
      gps_satelites: sats,
      sinal_lora: lora,
      solar: { tensao: vSolar, corrente: iSolar, pot: potSolar },
      bateria: { soc: soc, tensao_bat: vBat, corrente_liq: iLiq },
      prop: { rpm, i_motor: iMotor, t_motor: tMotor, t_ctrl: tCtrl, fardriver_falha: 0 },
      nav: { vel, proa: 0, lat, lon, gps_satelites: sats, gps_hora: new Date().toLocaleTimeString('pt-BR') },
      sinal: { lora, lte: 0, lora_pacotes: 0 },
      status_data: 'valid'
    };
  }

  notifyData(record, rawString) {
    this.dataCallbacks.forEach(cb => {
      try {
        cb(record, rawString);
      } catch (e) {
        console.error('[WebSerial] Erro ao processar telemetria em callback:', e);
      }
    });
  }

  async disconnect() {
    this.isConnected = false;
    try {
      if (this.reader) {
        await this.reader.cancel();
        this.reader = null;
      }
      if (this.readableStreamClosed) {
        await this.readableStreamClosed.catch(() => {});
        this.readableStreamClosed = null;
      }
      if (this.port) {
        await this.port.close();
        this.port = null;
      }
    } catch (err) {
      console.warn('[WebSerial] Erro ao fechar porta serial:', err);
    } finally {
      this.emitStatus('disconnected');
    }
  }
}

export const webSerial = new WebSerialManager();
export default webSerial;
