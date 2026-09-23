// audioAlerts.js - Gerenciador de Áudio e Alertas Sonoros da Estação Base Leviatã
// Suporta sons sintetizados via Web Audio API + Howler.js, sem dependência de internet ou arquivos externos.

class AudioAlertManager {
  constructor() {
    this.muted = false;
    this.audioCtx = null;
    this.lastAlertTimes = {
      critical: 0,
      warning: 0,
      info: 0,
      beep: 0
    };
    this.cooldownMs = 4000; // Intervalo mínimo entre alertas repetidos do mesmo tipo
  }

  getAudioContext() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
    return this.audioCtx;
  }

  isMuted() {
    return this.muted;
  }

  setMuted(mute) {
    this.muted = !!mute;
    return this.muted;
  }

  toggleMute() {
    this.muted = !this.muted;
    if (!this.muted) {
      this.playBeep(880, 0.1, 'sine');
    }
    return this.muted;
  }

  // Toca um tom sintetizado de frequência e duração customizadas
  playTone(frequency, durationSec, type = 'sine', gainVal = 0.25, timeOffset = 0) {
    if (this.muted) return;
    try {
      const ctx = this.getAudioContext();
      if (!ctx) return;

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(frequency, ctx.currentTime + timeOffset);

      gain.gain.setValueAtTime(0.001, ctx.currentTime + timeOffset);
      gain.gain.exponentialRampToValueAtTime(gainVal, ctx.currentTime + timeOffset + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + timeOffset + durationSec);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(ctx.currentTime + timeOffset);
      osc.stop(ctx.currentTime + timeOffset + durationSec + 0.05);
    } catch (e) {
      console.warn('[AudioAlerts] Erro ao reproduzir tom:', e);
    }
  }

  // Bip simples para cliques / ações
  playBeep(freq = 600, duration = 0.08, type = 'sine') {
    if (this.muted) return;
    this.playTone(freq, duration, type, 0.15);
  }

  // Alerta de Nível Crítico (Sirene dupla de alta urgência: 950Hz -> 600Hz x2)
  playCritical(force = false) {
    if (this.muted) return;
    const now = Date.now();
    if (!force && now - this.lastAlertTimes.critical < this.cooldownMs) {
      return;
    }
    this.lastAlertTimes.critical = now;

    // Dois pulsos agressivos de perigo
    this.playTone(980, 0.18, 'sawtooth', 0.25, 0.0);
    this.playTone(650, 0.18, 'sawtooth', 0.25, 0.2);
    this.playTone(980, 0.18, 'sawtooth', 0.25, 0.45);
    this.playTone(650, 0.25, 'sawtooth', 0.25, 0.65);
  }

  // Alerta de Nível Aviso (Tom duplo de atenção suave: 520Hz -> 780Hz)
  playWarning(force = false) {
    if (this.muted) return;
    const now = Date.now();
    if (!force && now - this.lastAlertTimes.warning < this.cooldownMs) {
      return;
    }
    this.lastAlertTimes.warning = now;

    this.playTone(520, 0.15, 'triangle', 0.2, 0.0);
    this.playTone(780, 0.22, 'triangle', 0.2, 0.18);
  }

  // Alerta de Conexão ou Notificação Informativa
  playInfo() {
    if (this.muted) return;
    this.playTone(440, 0.1, 'sine', 0.12, 0.0);
    this.playTone(880, 0.15, 'sine', 0.12, 0.12);
  }

  // Perda de sinal / desconexão (tom descendente)
  playSignalLost() {
    if (this.muted) return;
    this.playTone(600, 0.15, 'sine', 0.15, 0.0);
    this.playTone(350, 0.3, 'sine', 0.15, 0.16);
  }
}

export const audioAlerts = new AudioAlertManager();
export default audioAlerts;
