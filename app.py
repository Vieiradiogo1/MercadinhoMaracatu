import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Importando as telas
from main import PDVWindow
from cadastro import GerenciamentoProdutosWindow

# Importando controllers
from controllers.produto_controller import ProdutoController
from controllers.venda_controller import VendaController

class MenuPrincipal(QWidget):
    """Menu principal do sistema"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do menu principal"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Mercadinho - Sistema de Gestão")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Botões
        self.criar_botao("Ponto de Venda (PDV)", self.abrir_pdv, layout)
        self.criar_botao("Gerenciar Produtos", self.abrir_gerenciamento_produtos, layout)
        self.criar_botao("Relatórios de Vendas", self.abrir_relatorios, layout)
        self.criar_botao("Configurações", self.abrir_configuracoes, layout)
        self.criar_botao("Sair", self.sair, layout)
    
    def criar_botao(self, texto, funcao, layout):
        """Cria um botão padronizado"""
        botao = QPushButton(texto)
        botao.setFont(QFont("Arial", 14))
        botao.setMinimumSize(300, 60)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5d8c;
            }
        """)
        botao.clicked.connect(funcao)
        layout.addWidget(botao)
        return botao
    
    def abrir_pdv(self):
        """Abre a tela de PDV"""
        self.parent().abrir_tela_pdv()
    
    def abrir_gerenciamento_produtos(self):
        """Abre a tela de gerenciamento de produtos"""
        self.parent().abrir_tela_gerenciamento_produtos()
    
    def abrir_relatorios(self):
        """Abre a tela de relatórios (não implementada ainda)"""
        print("Tela de relatórios não implementada")
    
    def abrir_configuracoes(self):
        """Abre a tela de configurações (não implementada ainda)"""
        print("Tela de configurações não implementada")
    
    def sair(self):
        """Fecha o aplicativo"""
        self.parent().close()

class MainWindow(QMainWindow):
    """Janela principal que contém todas as telas em um QStackedWidget"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mercadinho - Sistema Integrado")
        self.setGeometry(50, 50, 1200, 700)
        
        # Inicializar controllers
        self.produto_controller = ProdutoController()
        self.venda_controller = VendaController()
        
        # Configurar o widget principal
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Adicionar telas
        self.menu_principal = MenuPrincipal(self)
        self.stacked_widget.addWidget(self.menu_principal)
        
        # PDV e Gerenciamento serão adicionados quando necessário
        self.pdv_window = None
        self.gerenciamento_window = None
    
    def abrir_tela_pdv(self):
        """Abre a tela de PDV"""
        if not self.pdv_window:
            self.pdv_window = PDVWindow()
            self.pdv_window.setup_controllers(self.produto_controller, self.venda_controller)
            self.stacked_widget.addWidget(self.pdv_window)
        
        # Abre a tela de PDV
        self.stacked_widget.setCurrentWidget(self.pdv_window)
    
    def abrir_tela_gerenciamento_produtos(self):
        """Abre a tela de gerenciamento de produtos"""
        if not self.gerenciamento_window:
            self.gerenciamento_window = GerenciamentoProdutosWindow()
            self.gerenciamento_window.setup_controller(self.produto_controller)
            self.stacked_widget.addWidget(self.gerenciamento_window)
        
        # Abre a tela de gerenciamento
        self.stacked_widget.setCurrentWidget(self.gerenciamento_window)
    
    def voltar_menu_principal(self):
        """Volta para o menu principal"""
        self.stacked_widget.setCurrentWidget(self.menu_principal)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())