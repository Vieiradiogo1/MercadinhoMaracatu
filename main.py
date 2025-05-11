import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QGridLayout, QScrollArea, QFrame, QComboBox, QMessageBox, QInputDialog
)
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHeaderView
# Import controllers
from controllers.produto_controller import ProdutoController
from controllers.venda_controller import VendaController


class ProdutoCard(QFrame):
    """Card para exibir os produtos na tela de vendas"""
    def __init__(self, produto_dict, parent=None):
        super().__init__(parent)
        self.produto = produto_dict
        self.nome = produto_dict["nome"]
        self.preco = produto_dict["preco"]
        self.categoria = produto_dict["categoria"]
        self.codigo = produto_dict.get("codigo", "")
        
        # Configuração do card
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                background-color: #f0f0f0;
                border: 1px solid #c0c0c0;
            }
        """)
        self.setFixedSize(150, 100)
        
        # Layout do card
        layout = QVBoxLayout(self)
        
        # Nome do produto
        self.nome_label = QLabel(self.nome)
        self.nome_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.nome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.nome_label)
        
        # Preço do produto
        self.preco_label = QLabel(f"R$ {self.preco:.2f}")
        self.preco_label.setStyleSheet("font-size: 14px; color: #2a7d2a;")
        self.preco_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preco_label)
        
        # Espaçador
        layout.addStretch()
        
        # Sinal de clique
        self.mousePressEvent = self.card_clicked
    
    def card_clicked(self, event):
        """Função chamada quando o card é clicado"""
        # Obter a referência ao PDV e adicionar o item
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, PDVWindow):
                parent.adicionar_item_carrinho(self.produto)
                break
            parent = parent.parent()


class PDVWindow(QWidget):
    """Janela do PDV"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.produto_controller = ProdutoController()
        self.venda_controller = VendaController()
        
        self.setup_ui()
        
        # Inicializar totais
        self.subtotal = 0.0
        self.desconto = 0.0
        self.total = 0.0
        self.itens_carrinho = []
        self.atualizar_totais()
    
    def setup_ui(self):
        """Configura toda a interface do usuário"""
        main_layout = QHBoxLayout(self)
        
        # === LADO ESQUERDO (PRODUTOS) ===
        produtos_widget = QWidget()
        produtos_layout = QVBoxLayout(produtos_widget)
        
        # Barra de pesquisa e categorias
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nome ou código")
        self.search_input.textChanged.connect(self.filtrar_produtos)
        search_layout.addWidget(self.search_input)
        
        self.categorias_combo = QComboBox()
        self.categorias_combo.addItem("Todas as Categorias")
        self.categorias_combo.currentIndexChanged.connect(self.filtrar_produtos)
        search_layout.addWidget(self.categorias_combo)
        
        produtos_layout.addLayout(search_layout)
        
        # Área de rolagem para os produtos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        self.produtos_container = QWidget()
        self.produtos_grid = QGridLayout(self.produtos_container)
        self.produtos_grid.setSpacing(10)
        scroll_area.setWidget(self.produtos_container)
        produtos_layout.addWidget(scroll_area)
        
        # === LADO DIREITO (CARRINHO) ===
        carrinho_widget = QWidget()
        carrinho_widget.setFixedWidth(400)
        carrinho_layout = QVBoxLayout(carrinho_widget)
        
        self.carrinho_table = QTableWidget()
        self.carrinho_table.setColumnCount(5)
        self.carrinho_table.setHorizontalHeaderLabels(["Qtd", "Item", "Preço", "Total", ""])
        self.carrinho_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        carrinho_layout.addWidget(self.carrinho_table)
        
        # Botão de finalizar venda
        finalizar_btn = QPushButton("Finalizar Venda")
        finalizar_btn.clicked.connect(self.finalizar_venda)
        carrinho_layout.addWidget(finalizar_btn)
        
        main_layout.addWidget(produtos_widget, 7)
        main_layout.addWidget(carrinho_widget, 3)
    
    def carregar_produtos(self):
        """Carrega produtos do banco de dados usando o controller"""
        produtos = self.produto_controller.listar()
        
        # Limpar o grid existente
        while self.produtos_grid.count():
            item = self.produtos_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Adicionar produtos ao grid
        row, col = 0, 0
        max_cols = 4
        categorias = set()
        
        for produto in produtos:
            card = ProdutoCard(produto)
            self.produtos_grid.addWidget(card, row, col)
            
            if produto.get("categoria"):
                categorias.add(produto["categoria"])
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.categorias_combo.clear()
        self.categorias_combo.addItem("Todas as Categorias")
        self.categorias_combo.addItems(sorted(categorias))
    
    def filtrar_produtos(self):
        """Filtra produtos pelo texto de busca e categoria selecionada"""
        texto_busca = self.search_input.text().lower()
        categoria_selecionada = self.categorias_combo.currentText()
        
        produtos = self.produto_controller.listar()
        
        produtos_filtrados = [
            p for p in produtos
            if (categoria_selecionada == "Todas as Categorias" or p.get("categoria") == categoria_selecionada) and
               (texto_busca in p["nome"].lower() or texto_busca in p.get("codigo", "").lower())
        ]
        
        # Limpar o grid existente
        while self.produtos_grid.count():
            item = self.produtos_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Recriar o grid com produtos filtrados
        row, col = 0, 0
        max_cols = 4
        
        for produto in produtos_filtrados:
            card = ProdutoCard(produto)
            self.produtos_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def adicionar_item_carrinho(self, produto):
        """Adiciona um item ao carrinho de compras"""
        nome = produto["nome"]
        preco = produto["preco"]
        codigo = produto.get("codigo", "")
        
        # Verificar se o item já está no carrinho
        encontrado = False
        for row in range(self.carrinho_table.rowCount()):
            item_nome = self.carrinho_table.item(row, 1).text()
            if item_nome == nome:
                qtd_atual = int(self.carrinho_table.item(row, 0).text())
                self.carrinho_table.item(row, 0).setText(str(qtd_atual + 1))
                
                total_item = preco * (qtd_atual + 1)
                self.carrinho_table.item(row, 3).setText(f"R$ {total_item:.2f}")
                
                encontrado = True
                break
        
        if not encontrado:
            row = self.carrinho_table.rowCount()
            self.carrinho_table.insertRow(row)
            self.carrinho_table.setItem(row, 0, QTableWidgetItem("1"))
            self.carrinho_table.setItem(row, 1, QTableWidgetItem(nome))
            self.carrinho_table.setItem(row, 2, QTableWidgetItem(f"R$ {preco:.2f}"))
            self.carrinho_table.setItem(row, 3, QTableWidgetItem(f"R$ {preco:.2f}"))
        
        self.calcular_totais()
    
    def calcular_totais(self):
        """Calcula os totais do carrinho"""
        self.subtotal = sum(
            float(self.carrinho_table.item(row, 3).text().replace("R$ ", "").replace(",", "."))
            for row in range(self.carrinho_table.rowCount())
        )
        self.total = self.subtotal - self.desconto
        self.atualizar_totais()
    
    def atualizar_totais(self):
        """Atualiza os labels com os totais"""
        print(f"Subtotal: {self.subtotal}, Total: {self.total}")
    
    def finalizar_venda(self):
        """Finaliza a venda atual"""
        QMessageBox.information(self, "Venda Finalizada", "Venda concluída com sucesso!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDVWindow()
    window.carregar_produtos()
    window.show()
    sys.exit(app.exec_())