import React from 'react';
import { Gauge, LineChart, Map, Terminal } from 'lucide-react';

export default function NavigationTabs({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'cockpit', label: 'Cockpit Ao Vivo', icon: Gauge },
    { id: 'charts', label: 'Análise de Desempenho', icon: LineChart },
    { id: 'map', label: 'Mapa & Raia', icon: Map },
    { id: 'diagnostics', label: 'Diagnósticos & Pacotes', icon: Terminal }
  ];

  return (
    <div className="flex items-center justify-center mb-6">
      <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md shadow-lg">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold tracking-wide transition-all flex items-center gap-2 ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 shadow-lg shadow-cyan-500/25'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
