class Simulator {
  constructor() {
    this.timer = null;
    this.isRunning = false;
    this.onDataCallbacks = [];
    
    // Estado interno para variação contínua realista
    this.soc = 85.0;
    this.lat = -3.1190;
    this.lon = -60.0210;
    this.proa = 180.0;
    this.pktCount = 1;
  }

  onData(callback) {
    this.onDataCallbacks.push(callback);
  }

  gerarPacote() {
    const agora = new Date();
    const gpsHora = agora.toTimeString().split(' ')[0];

    const rpm = Math.floor(1200 + Math.random() * 300);
    const vel = parseFloat((rpm * 0.015).toFixed(2));
    
    // Atualização simples de latitude e longitude no trajeto
    this.lat += (Math.random() - 0.49) * 0.0001;
    this.lon += (Math.random() - 0.49) * 0.0001;
    this.proa = parseFloat((170 + Math.random() * 20).toFixed(1));
    this.soc = Math.max(10, parseFloat((this.soc - 0.01).toFixed(2)));

    const potSolar = parseFloat((260 + Math.random() * 90).toFixed(1));
    const vSolar = parseFloat((46.5 + (Math.random() - 0.5)).toFixed(2));
    const iSolar = parseFloat((potSolar / vSolar).toFixed(2));

    const iMotor = parseFloat((15 + Math.random() * 12).toFixed(2));
    const vBat = parseFloat((51.2 - (Math.random() * 0.4)).toFixed(2));
    const iLiq = parseFloat((iSolar - iMotor).toFixed(2));

    const fardriverFalha = Math.random() > 0.95 ? [1, 5, 8][Math.floor(Math.random() * 3)] : 0;

    const pacote = {
      solar: {
        tensao: vSolar,
        corrente: iSolar,
        pot: potSolar
      },
      bateria: {
        soc: this.soc,
        tensao_bat: vBat,
        corrente_liq: iLiq
      },
      prop: {
        rpm: rpm,
        i_motor: iMotor,
        t_motor: parseFloat((45 + Math.random() * 10).toFixed(1)),
        t_ctrl: parseFloat((35 + Math.random() * 8).toFixed(1)),
        fardriver_falha: fardriverFalha
      },
      nav: {
        vel: vel,
        lat: parseFloat(this.lat.toFixed(6)),
        lon: parseFloat(this.lon.toFixed(6)),
        gps_satelites: Math.floor(9 + Math.random() * 4),
        gps_hora: gpsHora,
        proa: this.proa,
        hdop: parseFloat((0.8 + Math.random() * 0.5).toFixed(2))
      },
      sinal: {
        lora_pacotes: this.pktCount++,
        lora: Math.floor(-90 + Math.random() * 20),
        lte: Math.floor(15 + Math.random() * 15)
      },
      v_sist: parseFloat((4.0 + (Math.random() - 0.5) * 0.2).toFixed(2))
    };

    return pacote;
  }

  start(intervalMs = 1000) {
    if (this.isRunning) return;
    this.isRunning = true;

    this.timer = setInterval(() => {
      const pkg = this.gerarPacote();
      this.onDataCallbacks.forEach(cb => cb(pkg));
    }, intervalMs);

    console.log('Simulador de telemetria INICIADO.');
  }

  stop() {
    if (!this.isRunning) return;
    clearInterval(this.timer);
    this.timer = null;
    this.isRunning = false;
    console.log('Simulador de telemetria PARADO.');
  }
}

module.exports = new Simulator();
