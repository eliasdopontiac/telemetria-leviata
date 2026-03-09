import sys
from PyQt5.QtWidgets import QApplication

# Importa a Interface Gráfica que criamos
from ui_dashboard import FardriverApp

def main():
    """
    Ponto de entrada principal da aplicação Fardriver Pro.
    Este é o arquivo que deve ser executado no terminal.
    """
    print("A inicializar o Fardriver Pro - Bancada de Testes...")
    
    # Inicializa o motor do PyQt5
    app = QApplication(sys.argv)
    
    # Cria a janela principal
    janela = FardriverApp()
    janela.show()
    
    # Arranca o loop principal da aplicação e mantém a janela aberta
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()