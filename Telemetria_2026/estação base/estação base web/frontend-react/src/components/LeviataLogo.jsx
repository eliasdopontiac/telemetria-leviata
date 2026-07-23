import React from 'react';

export default function LeviataLogo({ height = 36 }) {
  return (
    <svg height={height} viewBox="0 0 160 68" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ display: 'block' }}>
      {/* Texto "equipe•" no topo */}
      <text x="2" y="20" fontFamily="'Inter', system-ui, sans-serif" fontWeight="600" fontSize="16" fill="#0052ff" letterSpacing="-0.5px">
        equipe
      </text>
      <circle cx="64" cy="15" r="3.5" fill="#0052ff" />

      {/* Texto "leviata" sem o til padrão */}
      <text x="0" y="62" fontFamily="'Inter', system-ui, sans-serif" fontWeight="800" fontSize="44" fill="#0052ff" letterSpacing="-1.5px">
        leviata
      </text>

      {/* Til em onda estilizada (~) posicionado exatamente sobre a letra 'a' final */}
      <path d="M124 26 C128 21, 134 21, 138 26 C142 31, 148 31, 152 26" stroke="#0052ff" strokeWidth="4.5" strokeLinecap="round" fill="none" />
    </svg>
  );
}
