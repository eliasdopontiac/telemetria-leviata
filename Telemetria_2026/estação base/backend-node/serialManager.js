const { SerialPort, ReadlineParser } = require('serialport');

class SerialManager {
  constructor() {
    this.port = null;
    this.parser = null;
    this.currentPortPath = null;
    this.isConnected = false;
    this.onDataCallbacks = [];
    this.onStatusCallbacks = [];
  }

  async listPorts() {
    try {
      const ports = await SerialPort.list();
      return ports.map(p => ({
        path: p.path,
        manufacturer: p.manufacturer || 'Desconhecido',
        serialNumber: p.serialNumber || '',
        pnpId: p.pnpId || '',
        friendlyName: p.friendlyName || p.path
      }));
    } catch (err) {
      console.error('Erro ao listar portas seriais:', err);
      return [];
    }
  }

  onData(callback) {
    this.onDataCallbacks.push(callback);
  }

  onStatusChange(callback) {
    this.onStatusCallbacks.push(callback);
  }

  notifyStatus(status, details = {}) {
    this.onStatusCallbacks.forEach(cb => cb({ status, details, port: this.currentPortPath }));
  }

  async connect(portPath, baudRate = 115200) {
    if (this.isConnected) {
      await this.disconnect();
    }

    return new Promise((resolve, reject) => {
      try {
        this.port = new SerialPort({
          path: portPath,
          baudRate: parseInt(baudRate, 10),
          autoOpen: false
        });

        this.parser = this.port.pipe(new ReadlineParser({ delimiter: '\n' }));

        this.port.open((err) => {
          if (err) {
            console.error(`Erro ao abrir porta ${portPath}:`, err.message);
            this.isConnected = false;
            this.notifyStatus('error', { message: err.message });
            return reject(err);
          }

          this.isConnected = true;
          this.currentPortPath = portPath;
          console.log(`Porta Serial conectada com sucesso: ${portPath} @ ${baudRate} bps`);
          this.notifyStatus('connected', { portPath, baudRate });

          resolve(true);
        });

        this.parser.on('data', (line) => {
          const trimmed = line.trim();
          if (!trimmed) return;
          this.onDataCallbacks.forEach(cb => cb(trimmed));
        });

        this.port.on('close', () => {
          console.log(`Porta serial fechada: ${this.currentPortPath}`);
          this.isConnected = false;
          this.notifyStatus('disconnected');
        });

        this.port.on('error', (err) => {
          console.error(`Erro na conexão serial (${this.currentPortPath}):`, err.message);
          this.notifyStatus('error', { message: err.message });
        });

      } catch (err) {
        reject(err);
      }
    });
  }

  async disconnect() {
    if (!this.port) return Promise.resolve(true);

    return new Promise((resolve) => {
      if (this.port.isOpen) {
        this.port.close(() => {
          this.isConnected = false;
          this.port = null;
          this.parser = null;
          this.currentPortPath = null;
          resolve(true);
        });
      } else {
        this.isConnected = false;
        this.port = null;
        this.parser = null;
        this.currentPortPath = null;
        resolve(true);
      }
    });
  }
}

module.exports = new SerialManager();
