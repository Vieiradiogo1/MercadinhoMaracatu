import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt

# Importando os controllers (quando estiver implementado)
# from controllers.produto_controller import ProdutoController

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
        
        # Inicializa o controller (quando estiver implementado)
        # self.produto_controller = ProdutoController()
        
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
        novo_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
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
        # Aqui você implementaria a lógica para carregar do controller
        # produtos = self.produto_controller.listar()
        
        # Vamos usar dados de exemplo por enquanto
        produtos = [
            {"codigo": "CAF-100", "nome": "Café com Leite", "preco": 5.35, "estoque": 100, "categoria": "Bebidas"},
            {"codigo": "BOL-50", "nome": "Bolo de Cenoura", "preco": 32.90, "estoque": 10, "categoria": "Doces"},
            {"codigo": "CHO-200", "nome": "Chocolate", "preco": 8.90, "estoque": 50, "categoria": "Doces"},
            {"codigo": "PAO-150", "nome": "Pão Francês", "preco": 0.75, "estoque": 200, "categoria": "Padaria"},
            {"codigo": "REF-120", "nome": "Refrigerante Cola", "preco": 6.50, "estoque": 48, "categoria": "Bebidas"},
        ]
        
        # Preencher a tabela
        self.preencher_tabela(produtos)
    
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
    
    def filtrar_produtos(self):
        """Filtra produtos baseado na busca"""
        texto = self.pesquisa_input.text().lower()
        
        # Implementação real conectaria ao controller
        # produtos = self.produto_controller.buscar(texto)
        
        # Dados de exemplo filtrados
        todos_produtos = [
            {"codigo": "CAF-100", "nome": "Café com Leite", "preco": 5.35, "estoque": 100, "categoria": "Bebidas"},
            {"codigo": "BOL-50", "nome": "Bolo de Cenoura", "preco": 32.90, "estoque": 10, "categoria": "Doces"},
            {"codigo": "CHO-200", "nome": "Chocolate", "preco": 8.90, "estoque": 50, "categoria": "Doces"},
            {"codigo": "PAO-150", "nome": "Pão Francês", "preco": 0.75, "estoque": 200, "categoria": "Padaria"},
            {"codigo": "REF-120", "nome": "Refrigerante Cola", "preco": 6.50, "estoque": 48, "categoria": "Bebidas"},
        ]
        
        # Filtragem local (para demonstração)
        if not texto:
            produtos_filtrados = todos_produtos
        else:
            produtos_filtrados = [
                p for p in todos_produtos 
                if texto in p["nome"].lower() or 
                   texto in p["codigo"].lower() or 
                   texto in p["categoria"].lower()
            ]
        
        # Atualizar tabela
        self.preencher_tabela(produtos_filtrados)
    
    def abrir_novo_produto(self):
        """Abre o diálogo para adicionar novo produto"""
        dialog = NovoProdutoDialog(parent=self)
        if dialog.exec_():
            produto = dialog.get_produto()
            
            # Aqui você chamaria o controller para salvar
            # self.produto_controller.criar(produto)
            
            # Como exemplo, vamos apenas atualizar a tabela
            QMessageBox.information(self, "Sucesso", f"Produto '{produto['nome']}' adicionado com sucesso!")
            self.carregar_produtos()
    
    def editar_produto(self, produto):
        """Abre o diálogo para editar um produto existente"""
        dialog = NovoProdutoDialog(produto=produto, parent=self)
        if dialog.exec_():
            produto_atualizado = dialog.get_produto()
            
            # Aqui você chamaria o controller para atualizar
            # self.produto_controller.atualizar(produto["id"], produto_atualizado)
            
            # Como exemplo, vamos apenas atualizar a tabela
            QMessageBox.information(self, "Sucesso", f"Produto '{produto_atualizado['nome']}' atualizado com sucesso!")
            self.carregar_produtos()
    
    def confirmar_exclusao(self, produto):
        """Confirma antes de excluir um produto"""
        resposta = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o produto '{produto['nome']}'?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            # Aqui você chamaria o controller para excluir
            # self.produto_controller.excluir(produto["id"])
            
            # Como exemplo, vamos apenas atualizar a tabela
            QMessageBox.information(self, "Sucesso", f"Produto '{produto['nome']}' excluído com sucesso!")
            self.carregar_produtos()
    
    def voltar_menu(self):
        """Volta para o menu principal"""
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GerenciamentoProdutosWindow()
    window.show()
    sys.exit(app.exec_())