import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

# Importando o controller
from MercadinhoMaracatu.controllers.produto_controller import ProdutoController
from MercadinhoMaracatu.controllers.venda_controller import VendaController


class NovoProdutoDialog(QDialog):
    """Dialog para adicionar ou editar produtos"""
    def __init__(self, produto=None, parent=None):
        super().__init__(parent)
        self.produto = produto  # Se for None, é um novo produto
        self.setup_ui()
        
        if produto:
            self.setWindowTitle("Editar Produto")
            self.nome_input.setText(produto["nome"])
            self.preco_input.setValue(produto["preco"])
            self.estoque_input.setValue(produto["estoque"])
            self.codigo_input.setText(produto["codigo"])
            self.categoria_input.setText(produto["categoria"])
        else:
            self.setWindowTitle("Novo Produto")
    
    def setup_ui(self):
        """Configura a interface do diálogo"""
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # Nome
        self.nome_input = QLineEdit()
        form_layout.addRow("Nome:", self.nome_input)
        
        # Preço
        self.preco_input = QDoubleSpinBox()
        self.preco_input.setRange(0, 9999.99)
        self.preco_input.setDecimals(2)
        self.preco_input.setSingleStep(0.5)
        self.preco_input.setPrefix("R$ ")
        form_layout.addRow("Preço:", self.preco_input)
        
        # Estoque
        self.estoque_input = QSpinBox()
        self.estoque_input.setRange(0, 9999)
        form_layout.addRow("Estoque:", self.estoque_input)
        
        # Código
        self.codigo_input = QLineEdit()
        form_layout.addRow("Código:", self.codigo_input)
        
        # Categoria
        self.categoria_input = QLineEdit()
        form_layout.addRow("Categoria:", self.categoria_input)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancelar_btn)
        
        salvar_btn = QPushButton("Salvar")
        salvar_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        salvar_btn.clicked.connect(self.aceitar)
        button_layout.addWidget(salvar_btn)
        
        layout.addLayout(button_layout)
    
    def aceitar(self):
        """Valida e aceita o formulário"""
        if not self.nome_input.text():
            QMessageBox.warning(self, "Erro", "O nome do produto é obrigatório.")
            return
        
        if self.preco_input.value() <= 0:
            QMessageBox.warning(self, "Erro", "O preço deve ser maior que zero.")
            return
        
        if not self.codigo_input.text():
            # Gerar código automaticamente baseado no nome
            codigo = f"{self.nome_input.text()[:3].upper()}-{self.estoque_input.value()}"
            self.codigo_input.setText(codigo)
        
        self.accept()
    
    def get_produto(self):
        """Retorna os dados do produto"""
        return {
            "nome": self.nome_input.text(),
            "preco": self.preco_input.value(),
            "estoque": self.estoque_input.value(),
            "codigo": self.codigo_input.text(),
            "categoria": self.categoria_input.text()
        }

class GerenciamentoProdutosWindow(QMainWindow):
    """Janela de gerenciamento de produtos"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciamento de Produtos")
        self.setGeometry(100, 100, 900, 600)
        
        # Inicializa o controller
        self.produto_controller = ProdutoController()
        
        self.setup_ui()
        self.carregar_produtos()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Gerenciamento de Produtos")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Barra de pesquisa
        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText("Pesquisar produto...")
        self.pesquisa_input.setMinimumWidth(250)
        self.pesquisa_input.textChanged.connect(self.filtrar_produtos)
        header_layout.addWidget(self.pesquisa_input)
        
        # Botão de novo produto
        novo_btn = QPushButton("Novo Produto")
        novo_btn.setStyleSheet("""QPushButton { background-color: #4CAF50; color: white; padding: 5px 15px; border: none; border-radius: 3px; } QPushButton:hover { background-color: #45a049; }""")
        novo_btn.clicked.connect(self.abrir_novo_produto)
        header_layout.addWidget(novo_btn)
        
        layout.addLayout(header_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)  # Código, Nome, Preço, Estoque, Categoria, Ações
        self.tabela.setHorizontalHeaderLabels(["Código", "Nome", "Preço", "Estoque", "Categoria", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Nome estica
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)  # Desabilita edição direta
        
        layout.addWidget(self.tabela)
        
        # Rodapé
        footer_layout = QHBoxLayout()
        
        footer_layout.addStretch()
        
        voltar_btn = QPushButton("Voltar ao Menu")
        voltar_btn.clicked.connect(self.voltar_menu)
        footer_layout.addWidget(voltar_btn)
        
        layout.addLayout(footer_layout)
    
    def carregar_produtos(self):
        """Carrega os produtos do banco de dados"""
        try:
            produtos = self.produto_controller.listar()
            self.preencher_tabela(produtos)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos: {e}")
    
    def preencher_tabela(self, produtos):
        """Preenche a tabela com os produtos"""
        self.tabela.setRowCount(0)  # Limpa a tabela
        
        for produto in produtos:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # Código
            self.tabela.setItem(row, 0, QTableWidgetItem(produto["codigo"]))
            
            # Nome
            self.tabela.setItem(row, 1, QTableWidgetItem(produto["nome"]))
            
            # Preço
            preco_item = QTableWidgetItem(f"R$ {produto['preco']:.2f}")
            preco_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela.setItem(row, 2, preco_item)
            
            # Estoque
            estoque_item = QTableWidgetItem(str(produto["estoque"]))
            estoque_item.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(row, 3, estoque_item)
            
            # Categoria
            self.tabela.setItem(row, 4, QTableWidgetItem(produto["categoria"]))
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            acoes_layout.setSpacing(5)
            
            # Botão editar
            editar_btn = QPushButton("✎")
            editar_btn.setToolTip("Editar")
            editar_btn.setStyleSheet("border: none; color: blue;")
            editar_btn.clicked.connect(lambda _, p=produto: self.editar_produto(p))
            acoes_layout.addWidget(editar_btn)
            
            # Botão excluir
            excluir_btn = QPushButton("×")
            excluir_btn.setToolTip("Excluir")
            excluir_btn.setStyleSheet("border: none; color: red; font-weight: bold;")
            excluir_btn.clicked.connect(lambda _, p=produto: self.confirmar_exclusao(p))
            acoes_layout.addWidget(excluir_btn)
            
            acoes_layout.addStretch()
            
            self.tabela.setCellWidget(row, 5, acoes_widget)