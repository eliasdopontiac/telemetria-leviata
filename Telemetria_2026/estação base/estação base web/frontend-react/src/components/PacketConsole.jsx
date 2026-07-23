import React, { useState } from 'react';
import { Terminal, CellSignalFull, CopySimple, Check, Broadcast, Cpu, ShieldWarning } from '@phosphor-icons/react';

export default function PacketConsole({ history = [], currentTelemetry, serialStatus }) {
  const [copied, setCopied] = useState(false);

  const sig = currentTelemetry?.sinal || {};
  const lora = sig.lora ?? currentTelemetry?.sinal_lora ?? 0;
  const lte = sig.lte ?? currentTelemetry?.sinal_lte ?? 0;
  const pkts = sig.lora_pacotes ?? currentTelemetry?.pkt_seq ?? 0;
  const vSist = currentTelemetry?.v_sist ?? 0;

  const rawJson = currentTelemetry 
    ? JSON.stringify(currentTelemetry, null, 2) 
    : '// Aguardando pacotes de telemetria...';

  const handleCopy = () => {
    navigator.clipboard.writeText(rawJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Tabela de falhas do Fardriver para diagnóstico rápido
  const fardriverErrors = {
    0: '0 - Funcionamento Normal (Sem erros)',
    1: '1 - Sobretensão na Bateria',
    2: '2 - Subtensão na Bateria (Corte por baixa carga)',
    3: '3 - Sobrecorrente no Motor',
    4: '4 - Sobreatemperatura no Motor (> 85°C)',
    5: '5 - Sobreatemperatura no Controlador (> 85°C)',
    6: '6 - Falha no Sensor Hall de Posição',
    7: '7 - Falha no Sinal do Acelerador (Throttle Fault)',
    8: '8 - Perda de Comunicação CAN/Serial'
  };

  const currentFault = currentTelemetry?.prop?.fardriver_falha ?? currentTelemetry?.falha_ctrl ?? 0;

  return (
    <div className="space-y-6">
      
      {/* Cards de Métricas do Link de Rádio LoRa */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        
        <div className="glass-card p-4 flex items-center gap-3">
          <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Broadcast size={20} weight="duotone" className="animate-pulse" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Sinal LoRa RSSI</span>
            <div className="text-xl font-extrabold font-mono text-cyan-400">{lora} dBm</div>
          </div>
        </div>

        <div className="glass-card p-4 flex items-center gap-3">
          <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <CellSignalFull size={20} weight="duotone" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Sinal Celular LTE</span>
            <div className="text-xl font-extrabold font-mono text-amber-400">{lte} dBm</div>
          </div>
        </div>

        <div className="glass-card p-4 flex items-center gap-3">
          <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <Terminal size={20} weight="duotone" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Pacotes LoRa</span>
            <div className="text-xl font-extrabold font-mono text-emerald-400">{pkts}</div>
          </div>
        </div>

        <div className="glass-card p-4 flex items-center gap-3">
          <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/30">
            <Cpu size={20} weight="duotone" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Tensão Sistema Interno</span>
            <div className="text-xl font-extrabold font-mono text-purple-400">{vSist.toFixed(2)} V</div>
          </div>
        </div>

      </div>

      {/* Grid: Terminal Inspector JSON + Diagnóstico Fardriver */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Terminal JSON Inspector */}
        <div className="lg:col-span-2 glass-card p-5 flex flex-col font-mono text-xs">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Terminal size={16} weight="duotone" className="text-cyan-400" />
              <span className="font-bold text-slate-200 uppercase tracking-wider">
                Inspetor de Pacotes Brutos (JSON Stream)
              </span>
            </div>
            <button
              onClick={handleCopy}
              className="btn-secondary text-[11px] py-1 px-2.5 flex items-center gap-1.5"
            >
              {copied ? <Check size={14} weight="bold" className="text-emerald-400" /> : <CopySimple size={14} weight="duotone" />}
              <span>{copied ? 'Copiado!' : 'Copiar JSON'}</span>
            </button>
          </div>

          <pre className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-cyan-300 overflow-x-auto max-h-[360px] leading-relaxed shadow-inner">
            {rawJson}
          </pre>
        </div>

        {/* Diagnóstico do Controlador Fardriver */}
        <div className="glass-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldWarning size={20} weight="duotone" className="text-amber-400" />
              <h3 className="font-bold text-sm text-slate-200 uppercase tracking-wider">
                Status Fardriver
              </h3>
            </div>

            <div className={`p-4 rounded-xl border mb-4 text-xs font-mono font-bold ${
              currentFault === 0
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-rose-500/20 border-rose-500/50 text-rose-300 animate-pulse'
            }`}>
              {fardriverErrors[currentFault] || `Falha Desconhecida (${currentFault})`}
            </div>

            <span className="text-[11px] text-slate-400 block mb-2 font-semibold uppercase">
              Tabela de Códigos Fardriver:
            </span>
            
            <ul className="text-[11px] space-y-1.5 text-slate-400 font-mono max-h-[220px] overflow-y-auto pr-1">
              {Object.entries(fardriverErrors).map(([code, label]) => (
                <li 
                  key={code} 
                  className={`p-1.5 rounded-lg border ${
                    parseInt(code, 10) === currentFault 
                      ? 'bg-rose-500/20 border-rose-500/50 text-rose-200 font-bold' 
                      : 'border-transparent hover:bg-slate-900'
                  }`}
                >
                  {label}
                </li>
              ))}
            </ul>
          </div>
        </div>

      </div>

    </div>
  );
}
