import sys
import os
from PyQt5.QtWidgets import QApplication

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interfaces.test_menu import MercadinhoApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MercadinhoApp()
    window.show()
    sys.exit(app.exec_())