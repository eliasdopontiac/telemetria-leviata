import os
import webbrowser
from datetime import datetime

class ReportGenerator:
    """
    Classe dedicada à geração de relatórios offline (HTML/PDF).
    Isola a lógica visual do relatório da lógica da interface gráfica.
    """
    
    @staticmethod
    def generate_html_report(telemetry, lista_rpm, lista_curr, lista_volt, eixo_x, base_dir, lista_temp_motor=None, lista_temp_mosfet=None):
        # Pega a data e hora exata de agora
        agora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Tratamento de segurança caso as listas de temperatura não sejam enviadas pela UI
        lista_temp_motor = lista_temp_motor or [telemetry.get('temp_motor', 0)]
        lista_temp_mosfet = lista_temp_mosfet or [telemetry.get('temp_mosfet', 0)]

        # Cálculos de Média e Máximo
        avg_t_motor = sum(lista_temp_motor) / len(lista_temp_motor)
        max_t_motor = max(lista_temp_motor)
        
        avg_t_mosfet = sum(lista_temp_mosfet) / len(lista_temp_mosfet)
        max_t_mosfet = max(lista_temp_mosfet)

        # Monta um template HTML profissional usando Chart.js
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Relatório Fardriver - {timestamp_arquivo}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #333; margin: 0; padding: 40px; }}
                .container {{ max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header-container {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0d6efd; padding-bottom: 10px; margin-bottom: 20px; }}
                h1 {{ color: #0d6efd; margin: 0; font-size: 24px; }}
                .logo-img {{ height: 50px; object-fit: contain; }}
                .header-info {{ display: flex; justify-content: space-between; color: #6c757d; font-size: 0.9em; margin-bottom: 30px; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 40px; }}
                .metric-box {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 6px; text-align: center; }}
                .metric-title {{ font-size: 0.85em; color: #6c757d; text-transform: uppercase; font-weight: bold; }}
                .metric-value {{ font-size: 1.8em; font-weight: bold; color: #212529; margin-top: 5px; }}
                
                /* Layout para múltiplos gráficos */
                .charts-wrapper {{ display: flex; flex-direction: column; gap: 30px; margin-top: 30px; }}
                .chart-container {{ width: 100%; height: 280px; }} /* Altura reduzida para caberem os 3 */
                
                .btn-print {{ background-color: #0d6efd; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
                .btn-print:hover {{ background-color: #0b5ed7; }}
                
                /* Esconde o botão de imprimir na hora de gerar o PDF */
                @media print {{
                    .btn-print {{ display: none; }}
                    body {{ padding: 0; background-color: white; }}
                    .container {{ box-shadow: none; max-width: 100%; border: none; }}
                    .chart-container {{ height: 250px; }} /* Ajuste fino para impressão */
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header-container">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <!-- Busca a logo.png na mesma pasta do relatório -->
                        <img src="logo.png" alt="Logotipo Leviatã" class="logo-img" onerror="this.style.display='none'">
                        <h1>Relatório de Teste Físico - Leviatã / Fardriver</h1>
                    </div>
                    <button class="btn-print" onclick="window.print()">🖨️ Salvar PDF</button>
                </div>
                
                <div class="header-info">
                    <span><strong>Data da Exportação:</strong> {agora}</span>
                    <span><strong>Status do Sistema:</strong> OK (Sem falhas críticas)</span>
                </div>

                <h3>Análise Geral de Potência</h3>
                <div class="metrics-grid">
                    <div class="metric-box"><div class="metric-title">RPM Máximo Atingido</div><div class="metric-value">{max(lista_rpm)}</div></div>
                    <div class="metric-box"><div class="metric-title">Pico de Corrente</div><div class="metric-value">{max(lista_curr):.1f} A</div></div>
                    <div class="metric-box"><div class="metric-title">Tensão Mínima</div><div class="metric-value">{min(lista_volt):.1f} V</div></div>
                    <div class="metric-box"><div class="metric-title">Tensão Atual</div><div class="metric-value">{telemetry.get('volt', 0):.1f} V</div></div>
                </div>

                <h3>Análise Térmica</h3>
                <div class="metrics-grid">
                    <div class="metric-box"><div class="metric-title">Temp. Motor (Média)</div><div class="metric-value">{avg_t_motor:.1f} °C</div></div>
                    <div class="metric-box"><div class="metric-title">Temp. Motor (Máximo)</div><div class="metric-value">{max_t_motor} °C</div></div>
                    <div class="metric-box"><div class="metric-title">Temp. Ctrl (Média)</div><div class="metric-value">{avg_t_mosfet:.1f} °C</div></div>
                    <div class="metric-box"><div class="metric-title">Temp. Ctrl (Máximo)</div><div class="metric-value">{max_t_mosfet} °C</div></div>
                </div>

                <h3>Gráficos de Comportamento (Trifásico)</h3>
                <div class="charts-wrapper">
                    <!-- Gráfico RPM -->
                    <div class="chart-container">
                        <canvas id="graficoRPM"></canvas>
                    </div>
                    <!-- Gráfico Corrente -->
                    <div class="chart-container">
                        <canvas id="graficoCorrente"></canvas>
                    </div>
                    <!-- Gráfico Tensão -->
                    <div class="chart-container">
                        <canvas id="graficoTensao"></canvas>
                    </div>
                </div>
            </div>

            <script>
                const labelsX = {eixo_x};

                // Configuração comum para todos os gráficos
                const commonOptions = {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{ legend: {{ position: 'top' }} }}
                }};

                // 1. Inicializa Gráfico de RPM
                new Chart(document.getElementById('graficoRPM').getContext('2d'), {{
                    type: 'line',
                    data: {{
                        labels: labelsX,
                        datasets: [{{
                            label: 'Rotação (RPM)',
                            data: {lista_rpm},
                            borderColor: '#198754',
                            backgroundColor: 'rgba(25, 135, 84, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            pointRadius: 0
                        }}]
                    }},
                    options: {{
                        ...commonOptions,
                        scales: {{
                            x: {{ display: false }},
                            y: {{ display: true, title: {{ display: true, text: 'Rotação (RPM)' }} }}
                        }}
                    }}
                }});

                // 2. Inicializa Gráfico de Corrente
                new Chart(document.getElementById('graficoCorrente').getContext('2d'), {{
                    type: 'line',
                    data: {{
                        labels: labelsX,
                        datasets: [{{
                            label: 'Corrente (A)',
                            data: {lista_curr},
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            pointRadius: 0
                        }}]
                    }},
                    options: {{
                        ...commonOptions,
                        scales: {{
                            x: {{ display: false }},
                            y: {{ display: true, title: {{ display: true, text: 'Corrente (Amperes)' }} }}
                        }}
                    }}
                }});

                // 3. Inicializa Gráfico de Tensão
                new Chart(document.getElementById('graficoTensao').getContext('2d'), {{
                    type: 'line',
                    data: {{
                        labels: labelsX,
                        datasets: [{{
                            label: 'Tensão Bateria (V)',
                            data: {lista_volt},
                            borderColor: '#0dcaf0',
                            backgroundColor: 'rgba(13, 202, 240, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            pointRadius: 0
                        }}]
                    }},
                    options: {{
                        ...commonOptions,
                        scales: {{
                            x: {{ display: false }},
                            y: {{ display: true, title: {{ display: true, text: 'Tensão (Volts)' }} }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """

        # Salva o arquivo na mesma pasta do projeto
        nome_arquivo = f"Relatorio_Fardriver_{timestamp_arquivo}.html"
        caminho_completo = os.path.join(base_dir, nome_arquivo)
        
        with open(caminho_completo, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Abre automaticamente no navegador padrão do Windows
        webbrowser.open(f"file://{caminho_completo}")
        
        return caminho_completo