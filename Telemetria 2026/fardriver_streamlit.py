import streamlit as st
import serial.tools.list_ports
import time
import pandas as pd

# ==========================================
# CONFIGURAÇÕES DE PÁGINA STREAMLIT
# ==========================================
st.set_page_config(page_title="Fardriver Pro", page_icon="⚡", layout="wide")

# ==========================================
# GESTÃO DE ESTADO (MEMÓRIA DO STREAMLIT)
# ==========================================
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
if 'telemetria' not in st.session_state:
    st.session_state.telemetria = {"rpm": 0, "volt": 48.0, "curr": 0.0, "temp_motor": 25, "temp_mosfet": 30}
if 'historico' not in st.session_state:
    # DataFrame vazio para os gráficos
    st.session_state.historico = pd.DataFrame(columns=["Tempo", "RPM", "Corrente", "Tensão"])

# ==========================================
# BARRA LATERAL (CONEXÃO E CONFIGURAÇÃO)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=50)
    st.title("Ligação USB")
    
    portas = [port.device for port in serial.tools.list_ports.comports()]
    if not portas:
        portas = ["Nenhuma porta encontrada"]
        
    porta_selecionada = st.selectbox("Selecione a Porta COM:", portas)
    
    if st.button("Ligar / Desligar"):
        if porta_selecionada != "Nenhuma porta encontrada":
            st.session_state.conectado = not st.session_state.conectado
            
    if st.session_state.conectado:
        st.success(f"Ligado na {porta_selecionada}")
    else:
        st.error("Desligado")

    st.markdown("---")
    st.subheader("Configurações Rápidas")
    limite_linha = st.slider("Corrente de Bateria (A)", 0, 100, 80)
    limite_fase = st.slider("Corrente de Fase (A)", 0, 450, 250)
    
    if st.button("Gravar na Controladora"):
        if st.session_state.conectado:
            st.success("Comando enviado com sucesso!")
        else:
            st.warning("Ligue a controladora primeiro.")

# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================
st.title("⚡ Painel de Telemetria Fardriver")
st.markdown("Monitorização em tempo real da ND72450 (Chumbo-Ácido Edition)")

# ==========================================
# ATUALIZAÇÃO DE TEMPO REAL (Modelo Streamlit)
# ==========================================
if st.session_state.conectado:
    # Apenas para parar o loop se o utilizador clicar em algo
    if st.button("Parar Telemetria"):
        st.session_state.conectado = False
        st.rerun()

    # 1. Aqui faríamos a leitura da Serial (Simulação de dados oscilantes)
    import random
    t = st.session_state.telemetria
    t["rpm"] = max(0, min(6000, t["rpm"] + random.randint(-50, 50)))
    t["volt"] = max(42.0, min(58.0, t["volt"] + random.uniform(-0.5, 0.5)))
    t["curr"] = max(0.0, min(100.0, t["curr"] + random.uniform(-2.0, 2.0)))
    
    # 2. Atualizar o histórico para o gráfico
    novo_dado = pd.DataFrame([{
        "Tempo": time.strftime("%H:%M:%S"), 
        "RPM": t["rpm"], 
        "Corrente": t["curr"], 
        "Tensão": t["volt"]
    }])
    st.session_state.historico = pd.concat([st.session_state.historico, novo_dado]).tail(50) # Mantém os últimos 50 pontos

    # 3. Desenhar as Métricas no Ecrã (Cartões)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Velocidade (RPM)", f"{t['rpm']} rpm", delta=random.randint(-10, 10))
    col2.metric("Tensão Bateria", f"{t['volt']:.1f} V", delta=f"{random.uniform(-0.1, 0.1):.1f} V")
    col3.metric("Corrente Linha", f"{t['curr']:.1f} A", delta_color="inverse")
    col4.metric("Temp Motor", f"{t['temp_motor']} °C")

    # 4. Desenhar os Gráficos
    st.subheader("Gráficos de Desempenho")
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.line_chart(st.session_state.historico.set_index("Tempo")[["Corrente", "Tensão"]], height=250)
    with col_graf2:
        st.line_chart(st.session_state.historico.set_index("Tempo")[["RPM"]], color="#00FF00", height=250)

    # 5. O SEGREDO DO STREAMLIT: Pausa curta e recarrega a página automaticamente
    time.sleep(0.5)
    st.rerun()

else:
    st.info("A aguardar ligação à porta USB...")