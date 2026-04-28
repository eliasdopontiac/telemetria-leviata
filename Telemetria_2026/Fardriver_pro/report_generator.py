import os
import webbrowser
from datetime import datetime

# Mapeamento de erros da Fardriver (conforme manual oficial)
ERROS_FARDRIVER = {
    0: "NENHUM ERRO (SISTEMA OK)",
    1: "FALHA SENSOR HALL DO MOTOR",
    2: "FALHA NO ACELERADOR",
    3: "ALARME DE PROTEÇÃO ANORMAL",
    4: "REINÍCIO POR PROTEÇÃO DE CORRENTE",
    5: "FALHA DE TENSÃO (SUB/SOBRETENSÃO)",
    6: "RESERVADO",
    7: "TEMPERATURA DO MOTOR ANORMAL",
    8: "TEMPERATURA DA CONTROLADORA ANORMAL",
    9: "EXCESSO DE CORRENTE DE FASE",
    10: "FALHA PONTO ZERO CORRENTE DE FASE",
    11: "CURTO-CIRCUITO NA FASE DO MOTOR",
    12: "FALHA PONTO ZERO CORRENTE DE LINHA",
    13: "FALHA MOSFET (PONTE SUPERIOR)",
    14: "FALHA MOSFET (PONTE INFERIOR)",
    15: "PROTEÇÃO PICO DE CORRENTE DE LINHA",
}

# Número máximo de pontos enviados aos gráficos do relatório.
# Acima desse limite os dados são decimados para evitar HTML gigante.
MAX_CHART_POINTS = 3000


class ReportGenerator:
    """
    Classe dedicada à geração de relatórios offline (HTML/PDF).
    Isola a lógica visual do relatório da lógica da interface gráfica.
    """

    @staticmethod
    def _decimate(data: list, max_pts: int = MAX_CHART_POINTS) -> list:
        """
        Reduz uma lista longa a no máximo *max_pts* pontos, preservando
        os extremos (primeiro e último elemento).
        """
        n = len(data)
        if n <= max_pts:
            return data
        step = n / max_pts
        indices = set([0, n - 1])
        indices.update(int(i * step) for i in range(1, max_pts - 1))
        return [data[i] for i in sorted(indices)]

    @staticmethod
    def generate_html_report(
        telemetry: dict,
        lista_rpm: list,
        lista_curr: list,
        lista_volt: list,
        eixo_x: list,
        save_path: str,
        lista_temp_motor: list = None,
        lista_temp_mosfet: list = None,
    ) -> str:
        """
        Gera um relatório HTML interativo e o salva em *save_path*.

        Parâmetros
        ----------
        telemetry       : dicionário com o último estado da telemetria.
        lista_rpm/curr/volt : histórico completo de cada grandeza.
        eixo_x          : eixo de tempo (índices ou segundos) — será decimado.
        save_path       : caminho completo do arquivo a salvar (escolhido pelo user).
        lista_temp_*    : históricos de temperatura (opcionais).
        """
        # ── Segurança: garantir listas de temperatura ─────────────────────────
        lista_temp_motor = lista_temp_motor or [telemetry.get("temp_motor", 0)]
        lista_temp_mosfet = lista_temp_mosfet or [telemetry.get("temp_mosfet", 0)]

        # ── Decimação ─────────────────────────────────────────────────────────
        rpm_dec = ReportGenerator._decimate(lista_rpm)
        curr_dec = ReportGenerator._decimate(lista_curr)
        volt_dec = ReportGenerator._decimate(lista_volt)
        eixo_dec = ReportGenerator._decimate(eixo_x)

        # ── Métricas de resumo ────────────────────────────────────────────────
        agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        avg_t_motor = sum(lista_temp_motor) / len(lista_temp_motor)
        max_t_motor = max(lista_temp_motor)
        avg_t_mosfet = sum(lista_temp_mosfet) / len(lista_temp_mosfet)
        max_t_mosfet = max(lista_temp_mosfet)
        total_pontos = len(lista_rpm)

        # ── Status de erro ────────────────────────────────────────────────────
        ultimo_erro = telemetry.get("error", 0)
        descricao_erro = ERROS_FARDRIVER.get(
            ultimo_erro, f"CÓDIGO DESCONHECIDO ({ultimo_erro})"
        )
        tem_erro = ultimo_erro != 0
        status_cor = "#dc3545" if tem_erro else "#198754"
        status_texto = (
            f"⚠️ FALHA DETECTADA — {descricao_erro}"
            if tem_erro
            else "✅ OK (Sem falhas críticas)"
        )

        # ── Duração estimada da sessão ────────────────────────────────────────
        segundos_totais = total_pontos // 10  # 10 Hz
        minutos = segundos_totais // 60
        segundos = segundos_totais % 60
        duracao_str = f"{minutos}m {segundos}s"

        # ── HTML ──────────────────────────────────────────────────────────────
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Fardriver — Leviatã</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            color: #212529;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1050px;
            margin: auto;
            background: #ffffff;
            padding: 36px 40px;
            border-radius: 10px;
            box-shadow: 0 4px 18px rgba(0,0,0,.12);
        }}

        /* ─── Cabeçalho ─────────────────────────────────────────────────── */
        .header-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #0d6efd;
            padding-bottom: 14px;
            margin-bottom: 8px;
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .logo-img {{ height: 52px; object-fit: contain; }}
        h1 {{ color: #0d6efd; font-size: 22px; }}
        .header-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #6c757d;
            font-size: 0.88em;
            margin: 10px 0 28px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        /* ─── Badge de status ───────────────────────────────────────────── */
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.88em;
            color: #fff;
            background-color: {status_cor};
        }}

        /* ─── Grids de métricas ─────────────────────────────────────────── */
        h3 {{
            font-size: 15px;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: .05em;
            margin-bottom: 12px;
            border-left: 4px solid #0d6efd;
            padding-left: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 34px;
        }}
        .metric-box {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 16px 14px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-title {{
            font-size: 0.78em;
            color: #6c757d;
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .metric-value {{
            font-size: 1.75em;
            font-weight: 700;
            color: #212529;
        }}

        /* ─── Gráficos ──────────────────────────────────────────────────── */
        .section-title {{
            font-size: 15px;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: .05em;
            margin-bottom: 16px;
            border-left: 4px solid #0d6efd;
            padding-left: 10px;
        }}
        .charts-wrapper {{ display: flex; flex-direction: column; gap: 28px; margin-top: 4px; }}
        .chart-container {{ width: 100%; height: 260px; }}

        /* ─── Rodapé ────────────────────────────────────────────────────── */
        .footer {{
            margin-top: 36px;
            padding-top: 14px;
            border-top: 1px solid #dee2e6;
            font-size: 0.82em;
            color: #adb5bd;
            text-align: center;
        }}

        /* ─── Botão imprimir ────────────────────────────────────────────── */
        .btn-print {{
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 9px 18px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9em;
            transition: background .2s;
        }}
        .btn-print:hover {{ background-color: #0b5ed7; }}

        @media print {{
            .btn-print {{ display: none; }}
            body {{ padding: 0; background: white; }}
            .container {{ box-shadow: none; max-width: 100%; }}
            .chart-container {{ height: 230px; }}
        }}
        @media (max-width: 700px) {{
            .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
<div class="container">

    <!-- ── Cabeçalho ───────────────────────────────────────────────────── -->
    <div class="header-container">
        <div class="header-left">
            <img src="logo.png" alt="Leviatã" class="logo-img"
                 onerror="this.style.display='none'">
            <h1>Relatório de Teste Físico — Leviatã / Fardriver</h1>
        </div>
        <button class="btn-print" onclick="window.print()">🖨️ Salvar PDF</button>
    </div>

    <div class="header-info">
        <span><strong>Exportado em:</strong> {agora}</span>
        <span><strong>Duração da sessão:</strong> {duracao_str}
              &nbsp;({total_pontos} amostras)</span>
        <span class="status-badge">{status_texto}</span>
    </div>

    <!-- ── Resumo de Potência ───────────────────────────────────────────── -->
    <h3>Análise Geral de Potência</h3>
    <div class="metrics-grid">
        <div class="metric-box">
            <div class="metric-title">RPM Máximo</div>
            <div class="metric-value">{max(lista_rpm)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Pico de Corrente</div>
            <div class="metric-value">{max(lista_curr):.1f} A</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Tensão Mínima</div>
            <div class="metric-value">{min(lista_volt):.1f} V</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Tensão Final</div>
            <div class="metric-value">{telemetry.get("volt", 0):.1f} V</div>
        </div>
    </div>

    <!-- ── Análise Térmica ──────────────────────────────────────────────── -->
    <h3>Análise Térmica</h3>
    <div class="metrics-grid">
        <div class="metric-box">
            <div class="metric-title">Temp. Motor (Média)</div>
            <div class="metric-value">{avg_t_motor:.1f} °C</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Temp. Motor (Máx.)</div>
            <div class="metric-value">{max_t_motor} °C</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Temp. Ctrl (Média)</div>
            <div class="metric-value">{avg_t_mosfet:.1f} °C</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Temp. Ctrl (Máx.)</div>
            <div class="metric-value">{max_t_mosfet} °C</div>
        </div>
    </div>

    <!-- ── Gráficos ─────────────────────────────────────────────────────── -->
    <h3 class="section-title">Gráficos de Comportamento (Decimados para {len(rpm_dec)} pts)</h3>
    <div class="charts-wrapper">
        <div class="chart-container"><canvas id="graficoRPM"></canvas></div>
        <div class="chart-container"><canvas id="graficoCorrente"></canvas></div>
        <div class="chart-container"><canvas id="graficoTensao"></canvas></div>
    </div>

    <!-- ── Rodapé ───────────────────────────────────────────────────────── -->
    <div class="footer">
        Gerado por <strong>Fardriver Pro</strong> — Equipe Leviatã (UEA) &nbsp;|&nbsp; {agora}
    </div>

</div>

<script>
    const labelsX = {eixo_dec};

    const commonOptions = {{
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: {{ mode: 'index', intersect: false }},
        plugins: {{
            legend: {{ position: 'top' }},
            tooltip: {{ mode: 'index' }}
        }}
    }};

    // 1. RPM
    new Chart(document.getElementById('graficoRPM').getContext('2d'), {{
        type: 'line',
        data: {{
            labels: labelsX,
            datasets: [{{
                label: 'Rotação (RPM)',
                data: {rpm_dec},
                borderColor: '#198754',
                backgroundColor: 'rgba(25,135,84,.08)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.2
            }}]
        }},
        options: {{
            ...commonOptions,
            scales: {{
                x: {{ display: false }},
                y: {{ title: {{ display: true, text: 'RPM' }} }}
            }}
        }}
    }});

    // 2. Corrente
    new Chart(document.getElementById('graficoCorrente').getContext('2d'), {{
        type: 'line',
        data: {{
            labels: labelsX,
            datasets: [{{
                label: 'Corrente (A)',
                data: {curr_dec},
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220,53,69,.08)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.2
            }}]
        }},
        options: {{
            ...commonOptions,
            scales: {{
                x: {{ display: false }},
                y: {{ title: {{ display: true, text: 'Amperes (A)' }} }}
            }}
        }}
    }});

    // 3. Tensão
    new Chart(document.getElementById('graficoTensao').getContext('2d'), {{
        type: 'line',
        data: {{
            labels: labelsX,
            datasets: [{{
                label: 'Tensão Bateria (V)',
                data: {volt_dec},
                borderColor: '#0dcaf0',
                backgroundColor: 'rgba(13,202,240,.08)',
                borderWidth: 2,
                fill: true,
                pointRadius: 0,
                tension: 0.2
            }}]
        }},
        options: {{
            ...commonOptions,
            scales: {{
                x: {{ display: false }},
                y: {{ title: {{ display: true, text: 'Volts (V)' }} }}
            }}
        }}
    }});
</script>
</body>
</html>"""

        # ── Salva no caminho escolhido pelo usuário ───────────────────────────
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Abre automaticamente no navegador padrão
        webbrowser.open(f"file:///{os.path.abspath(save_path)}")

        return save_path
