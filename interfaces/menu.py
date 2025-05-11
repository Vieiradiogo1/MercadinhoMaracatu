from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QMessageBox,
    QHBoxLayout,
)

class MercadinhoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mercadinho da Gi")
        self.setGeometry(100, 100, 600, 400)

        # Layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Título
        self.label_title = QLabel("Gerenciamento do Mercadinho", self)
        self.label_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.label_title)

        # Botões principais
        self.button_produtos = QPushButton("Gerenciar Produtos")
        self.button_produtos.clicked.connect(self.abrir_tela_produtos)
        self.layout.addWidget(self.button_produtos)

        self.button_vendas = QPushButton("Registrar Venda")
        self.button_vendas.clicked.connect(self.abrir_tela_vendas)
        self.layout.addWidget(self.button_vendas)

        self.button_sair = QPushButton("Sair")
        self.button_sair.clicked.connect(self.close)
        self.layout.addWidget(self.button_sair)

    def abrir_tela_produtos(self):
        self.tela_produtos = TelaProdutos(self)
        self.tela_produtos.show()

    def abrir_tela_vendas(self):
        self.tela_vendas = TelaVendas(self)
        self.tela_vendas.show()

class TelaProdutos(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Produtos")
        self.setGeometry(150, 150, 600, 400)

        # Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setRowCount(0)  # Número inicial de linhas
        self.tabela.setColumnCount(3)  # Colunas: Nome, Preço, Estoque
        self.tabela.setHorizontalHeaderLabels(["Nome", "Preço", "Estoque"])
        self.layout.addWidget(self.tabela)

        # Formulário para adicionar produtos
        self.form_layout = QHBoxLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome")
        self.form_layout.addWidget(self.input_nome)

        self.input_preco = QLineEdit()
        self.input_preco.setPlaceholderText("Preço")
        self.form_layout.addWidget(self.input_preco)

        self.input_estoque = QLineEdit()
        self.input_estoque.setPlaceholderText("Estoque")
        self.form_layout.addWidget(self.input_estoque)

        self.button_adicionar = QPushButton("Adicionar Produto")
        self.button_adicionar.clicked.connect(self.adicionar_produto)
        self.form_layout.addWidget(self.button_adicionar)

        self.layout.addLayout(self.form_layout)

    def adicionar_produto(self):
        nome = self.input_nome.text()
        preco = self.input_preco.text()
        estoque = self.input_estoque.text()

        if not nome or not preco or not estoque:
            QMessageBox.warning(self, "Erro", "Por favor, preencha todos os campos.")
            return

        # Adicionar produto na tabela
        linha = self.tabela.rowCount()
        self.tabela.insertRow(linha)
        self.tabela.setItem(linha, 0, QTableWidgetItem(nome))
        self.tabela.setItem(linha, 1, QTableWidgetItem(preco))
        self.tabela.setItem(linha, 2, QTableWidgetItem(estoque))

        # Limpar os campos
        self.input_nome.clear()
        self.input_preco.clear()
        self.input_estoque.clear()

class TelaVendas(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Venda")
        self.setGeometry(150, 150, 600, 400)

        # Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Mensagem de venda
        self.label_venda = QLabel("Funcionalidade de vendas em construção...")
        self.label_venda.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.label_venda)

        self.button_voltar = QPushButton("Voltar")
        self.button_voltar.clicked.connect(self.close)
        self.layout.addWidget(self.button_voltar)