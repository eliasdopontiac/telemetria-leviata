// exportService.js - Exportação de Relatórios Pós-Corrida em PDF e Planilhas Excel (.xlsx)
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';
import ExcelJS from 'exceljs';

// Inicializa as fontes virtuais do pdfMake se disponíveis
if (pdfFonts && pdfFonts.pdfMake && pdfFonts.pdfMake.vfs) {
  pdfMake.vfs = pdfFonts.pdfMake.vfs;
} else if (pdfFonts && pdfFonts.vfs) {
  pdfMake.vfs = pdfFonts.vfs;
}

/**
 * Calcula resumo estatístico a partir do histórico de telemetria
 */
export function calcularEstatisticasSessao(history = []) {
  if (!history || history.length === 0) {
    return {
      totalPontos: 0,
      velMax: 0,
      velMedia: 0,
      potSolarMax: 0,
      potSolarMedia: 0,
      iMotorMax: 0,
      tMotorMax: 0,
      tCtrlMax: 0,
      socMin: 100,
      socMax: 100,
      vBatMin: 0,
      vBatMax: 0
    };
  }

  let somaVel = 0;
  let somaPotSolar = 0;
  let velMax = 0;
  let potSolarMax = 0;
  let iMotorMax = 0;
  let tMotorMax = 0;
  let tCtrlMax = 0;
  let socMin = 100;
  let socMax = 0;
  let vBatMin = 999;
  let vBatMax = 0;

  history.forEach(item => {
    const s = item.solar || {};
    const p = item.prop || {};
    const b = item.bateria || {};
    const n = item.nav || {};

    const vel = Number(n.vel ?? item.vel ?? 0) * 0.539957;
    const pot = Number(s.pot ?? item.pot_solar ?? 0);
    const iMot = Number(p.i_motor ?? item.i_motor ?? 0);
    const tMot = Number(p.t_motor ?? item.t_motor ?? 0);
    const tCt = Number(p.t_ctrl ?? item.t_ctrl ?? 0);
    const soc = Number(b.soc ?? item.soc ?? 0);
    const vBat = Number(b.tensao_bat ?? item.v_bat ?? 0);

    somaVel += vel;
    somaPotSolar += pot;
    if (vel > velMax) velMax = vel;
    if (pot > potSolarMax) potSolarMax = pot;
    if (iMot > iMotorMax) iMotorMax = iMot;
    if (tMot > tMotorMax) tMotorMax = tMot;
    if (tCt > tCtrlMax) tCtrlMax = tCt;
    if (soc > 0 && soc < socMin) socMin = soc;
    if (soc > socMax) socMax = soc;
    if (vBat > 0 && vBat < vBatMin) vBatMin = vBat;
    if (vBat > vBatMax) vBatMax = vBat;
  });

  const count = history.length;
  return {
    totalPontos: count,
    velMax: velMax.toFixed(1),
    velMedia: (somaVel / count).toFixed(1),
    potSolarMax: potSolarMax.toFixed(0),
    potSolarMedia: (somaPotSolar / count).toFixed(0),
    iMotorMax: iMotorMax.toFixed(1),
    tMotorMax: tMotorMax.toFixed(1),
    tCtrlMax: tCtrlMax.toFixed(1),
    socMin: socMin === 100 && socMax === 0 ? '--' : socMin.toFixed(1),
    socMax: socMax === 0 ? '--' : socMax.toFixed(1),
    vBatMin: vBatMin === 999 ? '--' : vBatMin.toFixed(2),
    vBatMax: vBatMax === 0 ? '--' : vBatMax.toFixed(2)
  };
}

/**
 * Gera e dispara o download do relatório oficial em PDF da Sessão
 */
export async function exportarRelatorioPDF(sessao, history = []) {
  const stats = calcularEstatisticasSessao(history);
  const dataHoje = new Date().toLocaleString('pt-BR');
  const nomeSessao = sessao?.nome || 'Sessão de Telemetria';
  const sessaoId = sessao?.id || 'Avulsa';

  // Amostra de até 20 registros mais recentes para a tabela resumida
  const ultimosRegistros = history.slice(-25).reverse();

  const docDefinition = {
    pageSize: 'A4',
    pageOrientation: 'portrait',
    pageMargins: [35, 40, 35, 40],
    defaultStyle: {
      fontSize: 9,
      color: '#1e293b'
    },
    styles: {
      headerTitle: {
        fontSize: 16,
        bold: true,
        color: '#0284c7'
      },
      subHeader: {
        fontSize: 10,
        color: '#64748b',
        margin: [0, 2, 0, 10]
      },
      sectionTitle: {
        fontSize: 12,
        bold: true,
        color: '#0f172a',
        margin: [0, 12, 0, 6]
      },
      tableHeader: {
        bold: true,
        fontSize: 8,
        color: '#ffffff',
        fillColor: '#0284c7',
        alignment: 'center'
      },
      tableCell: {
        fontSize: 8,
        alignment: 'center'
      },
      kpiBox: {
        fontSize: 10,
        bold: true,
        alignment: 'center'
      }
    },
    content: [
      // Cabeçalho Principal
      {
        columns: [
          {
            width: '*',
            stack: [
              { text: 'LEVIATÃ - BARCO SOLAR UFSC / TELEMETRIA', style: 'headerTitle' },
              { text: `Relatório Oficial da Sessão: ${nomeSessao} (ID: ${sessaoId})`, style: 'subHeader' },
              { text: `Gerado em: ${dataHoje} | Total de Pacotes: ${stats.totalPontos}`, fontSize: 8, color: '#94a3b8' }
            ]
          }
        ]
      },
      { canvas: [{ type: 'line', x1: 0, y1: 5, x2: 525, y2: 5, lineWidth: 1.5, lineColor: '#0284c7' }] },
      
      // Resumo de KPIs / Estatísticas
      { text: '1. RESUMO EXECUTIVO DA PROVA / SESSÃO', style: 'sectionTitle' },
      {
        table: {
          widths: ['*', '*', '*', '*'],
          body: [
            [
              { text: 'Velocidade Máxima\n' + stats.velMax + ' nós', style: 'kpiBox', fillColor: '#f0f9ff' },
              { text: 'Velocidade Média\n' + stats.velMedia + ' nós', style: 'kpiBox', fillColor: '#f0f9ff' },
              { text: 'Potência Solar Máx\n' + stats.potSolarMax + ' W', style: 'kpiBox', fillColor: '#fefce8' },
              { text: 'Potência Solar Média\n' + stats.potSolarMedia + ' W', style: 'kpiBox', fillColor: '#fefce8' }
            ],
            [
              { text: 'Corrente Máx Motor\n' + stats.iMotorMax + ' A', style: 'kpiBox', fillColor: '#fef2f2' },
              { text: 'Temp Máx Motor\n' + stats.tMotorMax + ' °C', style: 'kpiBox', fillColor: '#fef2f2' },
              { text: 'Temp Máx Ctrl\n' + stats.tCtrlMax + ' °C', style: 'kpiBox', fillColor: '#fef2f2' },
              { text: 'SOC Mínimo\n' + stats.socMin + ' %', style: 'kpiBox', fillColor: '#f0fdf4' }
            ]
          ]
        },
        layout: {
          hLineWidth: () => 0.5,
          vLineWidth: () => 0.5,
          hLineColor: () => '#cbd5e1',
          vLineColor: () => '#cbd5e1'
        }
      },

      // Tabela de Amostras de Telemetria
      { text: '2. ÚLTIMOS REGISTROS DE TELEMETRIA (AMOSTRAGEM)', style: 'sectionTitle' },
      {
        table: {
          headerRows: 1,
          widths: [45, 35, 35, 40, 40, 35, 35, 45, 45, '*'],
          body: [
            [
              { text: 'Hora', style: 'tableHeader' },
              { text: 'Vel (nós)', style: 'tableHeader' },
              { text: 'RPM', style: 'tableHeader' },
              { text: 'V.Bat (V)', style: 'tableHeader' },
              { text: 'I.Liq (A)', style: 'tableHeader' },
              { text: 'SOC (%)', style: 'tableHeader' },
              { text: 'P.Sol (W)', style: 'tableHeader' },
              { text: 'T.Mot (°C)', style: 'tableHeader' },
              { text: 'T.Ctrl (°C)', style: 'tableHeader' },
              { text: 'Fonte', style: 'tableHeader' }
            ],
            ...ultimosRegistros.map(r => {
              const s = r.solar || {};
              const p = r.prop || {};
              const b = r.bateria || {};
              const n = r.nav || {};
              const hora = n.gps_hora && n.gps_hora !== '--:--:--'
                ? n.gps_hora
                : (r.timestamp_iso ? new Date(r.timestamp_iso).toLocaleTimeString('pt-BR') : '--');

              return [
                { text: hora, style: 'tableCell' },
                { text: ((n.vel ?? r.vel ?? 0) * 0.539957).toFixed(1), style: 'tableCell' },
                { text: (p.rpm ?? r.rpm ?? 0), style: 'tableCell' },
                { text: (b.tensao_bat ?? r.v_bat ?? 0).toFixed(1), style: 'tableCell' },
                { text: (b.corrente_liq ?? r.i_liq ?? 0).toFixed(1), style: 'tableCell' },
                { text: (b.soc ?? r.soc ?? 0).toFixed(0) + '%', style: 'tableCell' },
                { text: (s.pot ?? r.pot_solar ?? 0).toFixed(0), style: 'tableCell' },
                { text: (p.t_motor ?? r.t_motor ?? 0).toFixed(1), style: 'tableCell' },
                { text: (p.t_ctrl ?? r.t_ctrl ?? 0).toFixed(1), style: 'tableCell' },
                { text: r.fonte || 'serial', style: 'tableCell' }
              ];
            })
          ]
        },
        layout: {
          fillColor: (rowIndex) => (rowIndex % 2 === 0 ? '#f8fafc' : null),
          hLineWidth: () => 0.5,
          vLineWidth: () => 0.5,
          hLineColor: () => '#e2e8f0',
          vLineColor: () => '#e2e8f0'
        }
      },

      // Rodapé
      {
        margin: [0, 20, 0, 0],
        text: 'Leviatã Solar Racing Team - UFSC | Sistema de Telemetria e Aquisição de Dados 2026',
        style: { alignment: 'center', fontSize: 8, color: '#94a3b8', italic: true }
      }
    ]
  };

  const filename = `Relatorio_Telemetria_${nomeSessao.replace(/[^a-zA-Z0-9_-]/g, '_')}_ID${sessaoId}.pdf`;
  pdfMake.createPdf(docDefinition).download(filename);
}

/**
 * Gera e dispara o download da planilha Excel (.xlsx) completa com formatação profissional
 */
export async function exportarPlanilhaExcel(sessao, history = []) {
  const stats = calcularEstatisticasSessao(history);
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'Telemetria Leviatã';
  workbook.created = new Date();

  // === ABA 1: RESUMO EXECUTIVO ===
  const wsResumo = workbook.addWorksheet('Resumo da Prova');

  wsResumo.columns = [
    { header: 'Métrica / Parâmetro', key: 'param', width: 32 },
    { header: 'Valor Registrado', key: 'valor', width: 22 },
    { header: 'Unidade', key: 'unidade', width: 14 }
  ];

  // Estilo do cabeçalho
  wsResumo.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
  wsResumo.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0284C7' } };

  const linhasResumo = [
    { param: 'Nome da Sessão', valor: sessao?.nome || 'Telemetria Geral', unidade: '-' },
    { param: 'Identificador (ID)', valor: sessao?.id || 'Avulsa', unidade: '#' },
    { param: 'Total de Pacotes Processados', valor: stats.totalPontos, unidade: 'amostras' },
    { param: 'Velocidade Máxima', valor: stats.velMax, unidade: 'nós' },
    { param: 'Velocidade Média', valor: stats.velMedia, unidade: 'nós' },
    { param: 'Potência Solar de Pico', valor: stats.potSolarMax, unidade: 'W' },
    { param: 'Potência Solar Média', valor: stats.potSolarMedia, unidade: 'W' },
    { param: 'Corrente Máxima do Motor', valor: stats.iMotorMax, unidade: 'A' },
    { param: 'Temperatura Máxima do Motor', valor: stats.tMotorMax, unidade: '°C' },
    { param: 'Temperatura Máxima do Controlador', valor: stats.tCtrlMax, unidade: '°C' },
    { param: 'Estado de Carga Mínimo (SoC)', valor: stats.socMin, unidade: '%' },
    { param: 'Tensão Mínima de Bateria', valor: stats.vBatMin, unidade: 'V' }
  ];

  linhasResumo.forEach(item => wsResumo.addRow(item));

  // === ABA 2: DADOS DE TELEMETRIA COMPLETOS ===
  const wsDados = workbook.addWorksheet('Dados Completos');

  wsDados.columns = [
    { header: 'Data/Hora ISO', key: 'timestamp_iso', width: 24 },
    { header: 'Hora GPS', key: 'gps_hora', width: 12 },
    { header: 'Fonte', key: 'fonte', width: 12 },
    { header: 'Velocidade (nós)', key: 'vel', width: 16 },
    { header: 'RPM', key: 'rpm', width: 10 },
    { header: 'Tensao Solar (V)', key: 'v_solar', width: 16 },
    { header: 'Corrente Solar (A)', key: 'i_solar', width: 18 },
    { header: 'Potencia Solar (W)', key: 'pot_solar', width: 18 },
    { header: 'Tensao Bateria (V)', key: 'v_bat', width: 18 },
    { header: 'Corrente Liquida (A)', key: 'i_liq', width: 18 },
    { header: 'SoC Bateria (%)', key: 'soc', width: 16 },
    { header: 'Corrente Motor (A)', key: 'i_motor', width: 18 },
    { header: 'Temp Motor (°C)', key: 't_motor', width: 16 },
    { header: 'Temp Ctrl (°C)', key: 't_ctrl', width: 16 },
    { header: 'Latitude', key: 'lat', width: 14 },
    { header: 'Longitude', key: 'lon', width: 14 },
    { header: 'Satelites', key: 'sats', width: 12 },
    { header: 'Sinal LoRa (dBm)', key: 'lora', width: 16 }
  ];

  wsDados.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } };
  wsDados.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF0F172A' } };

  history.forEach(r => {
    const s = r.solar || {};
    const p = r.prop || {};
    const b = r.bateria || {};
    const n = r.nav || {};
    const sig = r.sinal || {};

    wsDados.addRow({
      timestamp_iso: r.timestamp_iso || '',
      gps_hora: n.gps_hora || r.gps_hora || '',
      fonte: r.fonte || 'serial',
      vel: (n.vel ?? r.vel ?? 0) * 0.539957,
      rpm: p.rpm ?? r.rpm ?? 0,
      v_solar: s.tensao ?? r.v_solar ?? 0,
      i_solar: s.corrente ?? r.i_solar ?? 0,
      pot_solar: s.pot ?? r.pot_solar ?? 0,
      v_bat: b.tensao_bat ?? r.v_bat ?? 0,
      i_liq: b.corrente_liq ?? r.i_liq ?? 0,
      soc: b.soc ?? r.soc ?? 0,
      i_motor: p.i_motor ?? r.i_motor ?? 0,
      t_motor: p.t_motor ?? r.t_motor ?? 0,
      t_ctrl: p.t_ctrl ?? r.t_ctrl ?? 0,
      lat: n.lat ?? r.lat ?? 0,
      lon: n.lon ?? r.lon ?? 0,
      sats: n.gps_satelites ?? r.gps_satelites ?? 0,
      lora: sig.lora ?? r.sinal_lora ?? 0
    });
  });

  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Telemetria_Leviata_${(sessao?.nome || 'Sessao').replace(/[^a-zA-Z0-9_-]/g, '_')}.xlsx`;
  a.click();
  window.URL.revokeObjectURL(url);
}
