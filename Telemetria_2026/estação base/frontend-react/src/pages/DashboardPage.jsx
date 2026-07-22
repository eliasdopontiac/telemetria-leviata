import React from 'react';
import CircularGauge from '../components/CircularGauge';
import BatteryWidget from '../components/BatteryWidget';
import LapTimer from '../components/LapTimer';
import AlertBanner from '../components/AlertBanner';
import BoatMap from '../components/BoatMap';
import MetricCard from '../components/MetricCard';
import EnergyChartWidget from '../components/EnergyChartWidget';
import { Zap, Gauge, Navigation, Flame, Thermometer, Signal } from 'lucide-react';

export default function DashboardPage({ currentTelemetry, history }) {
  const t = currentTelemetry || {};
  const s = t.solar || {};
  const p = t.prop || {};
  const n = t.nav || {};
  
  const potSolar = s.pot ?? t.pot_solar ?? 0;
  const rpm = p.rpm ?? t.rpm ?? 0;
  const iMotor = p.i_motor ?? t.i_motor ?? 0;
  const tMotor = p.t_motor ?? t.t_motor ?? 0;
  const tCtrl = p.t_ctrl ?? t.t_ctrl ?? 0;
  const vel = n.vel ?? t.vel ?? 0;
  
  const sig = t.sinal || {};
  const lora = sig.lora ?? t.sinal_lora ?? 0;
  const pkts = sig.lora_pacotes ?? t.pkt_seq ?? 0;

  return (
    <>
      <AlertBanner telemetryData={t} />

      <div className="dashboard-grid">
        {/* COLUNA ESQUERDA: Manômetros + Bateria */}
        <div className="dashboard-col">
          <div className="gauge-row">
            <CircularGauge title="Velocidade" value={vel} unit="km/h" min={0} max={30} warningThreshold={22} dangerThreshold={26} color="#00f2fe" icon={Navigation} />
            <CircularGauge title="RPM" value={rpm} unit="RPM" min={0} max={2500} warningThreshold={1800} dangerThreshold={2200} color="#38bdf8" icon={Gauge} />
            <CircularGauge title="Solar" value={potSolar} unit="W" min={0} max={500} color="#ffb703" icon={Zap} />
          </div>
          <BatteryWidget telemetryData={t} />
          <EnergyChartWidget history={history} />
        </div>

        {/* COLUNA CENTRAL: Mapa + Cronômetro */}
        <div className="dashboard-col">
          <div style={{ flex: 1, minHeight: '300px' }}>
            <BoatMap telemetryData={t} />
          </div>
          <LapTimer history={history} currentTelemetry={t} />
        </div>

        {/* COLUNA DIREITA: Métricas Críticas (Temperaturas, Corrente) */}
        <div className="dashboard-col" style={{ gap: '16px', display: 'flex', flexDirection: 'column' }}>
          <MetricCard
            title="Temp. Motor" value={tMotor.toFixed(1)} unit="°C"
            icon={Flame} colorScheme="danger" warning={65} danger={85}
            progress={tMotor} progressMax={100}
            subtext="Limite: 65°C"
          />
          <MetricCard
            title="Temp. Ctrl" value={tCtrl.toFixed(1)} unit="°C"
            icon={Thermometer} colorScheme="primary" warning={55} danger={75}
            progress={tCtrl} progressMax={100}
            subtext="Caixa Eletrônica"
          />
          <MetricCard
            title="Corrente Motor" value={iMotor.toFixed(1)} unit="A"
            icon={Zap} colorScheme="solar"
            subtext="Consumo"
          />
          <MetricCard
            title="Sinal LoRa" value={lora ? `${lora}` : '--'} unit="dBm"
            icon={Signal} colorScheme="primary"
            progress={Math.max(0, 100 + (lora > 0 ? -lora : lora))} progressMax={100}
            subtext={`Pkts: ${pkts}`}
          />
        </div>
      </div>
    </>
  );
}
