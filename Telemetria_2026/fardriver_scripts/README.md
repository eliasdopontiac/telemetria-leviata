# 🖥️ Fardriver Scripts — Prototipagem e Análise

Esta pasta contém **scripts experimentais** criados durante o processo de pesquisa e desenvolvimento do protocolo de comunicação com o controlador de motor **Fardriver (ND72450)**.

> ⚠️ Estes são protótipos e rascunhos de engenharia. A versão **estável e com interface gráfica** está em `../Fardriver_pro/`.

---

## 📄 Arquivos

| Arquivo | Descrição |
|---|---|
| `Fardriver.py` | Script inicial de leitura serial do Fardriver |
| `Fardriver_PyQtGrafs.py` | Protótipo com gráficos PyQt5 em tempo real |
| `Fardriver_matplotlib.py` | Protótipo com gráficos Matplotlib |
| `fardriver_UI_teste.py` | Testes de layout da interface gráfica |
| `fardriver_app.py` | Versão consolidada de testes antes do `Fardriver_pro` |
| `fardriver_streamlit.py` | Experimento com Streamlit como alternativa de UI |

---

## 🚫 Não use em produção

Estes scripts foram utilizados para:
- Engenharia reversa do protocolo Fardriver
- Testes de bibliotecas de gráficos
- Prova de conceitos de interface

Para o sistema de diagnóstico oficial, vá para [`../Fardriver_pro/`](../Fardriver_pro/README.md).
