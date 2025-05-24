import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QMessageBox, QDialog, QSpinBox, QComboBox,
    QDateEdit, QFormLayout, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon

from MercadinhoMaracatu.controllers.venda_controller import VendaController
from MercadinhoMaracatu.controllers.produto_controller import ProdutoController

# Importando os controllers (quando estiver implementado)
# from controllers.venda_controller import VendaController
# from controllers.produto_controller import ProdutoController

class FormaPagamentoDialog(QDialog):
    """Diálogo para seleção da forma de pagamento"""
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.total = total
        self.setWindowTitle("Finalizar Venda")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do diálogo"""
        layout = QVBoxLayout(self)
        
        # Total da venda
        total_frame = QFrame()
        total_frame.setFrameShape(QFrame.StyledPanel)
        total_frame.setStyleSheet("background-color: #f8f8f8; padding: 10px;")
        total_layout = QVBoxLayout(total_frame)
        
        total_label = QLabel("Total da Venda:")
        total_label.setStyleSheet("font-size: 14px;")
        total_layout.addWidget(total_label)
        
        valor_total = QLabel(f"R$ {self.total:.2f}")
        valor_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #2a7d2a;")
        total_layout.addWidget(valor_total)
        
        layout.addWidget(total_frame)
        
        # Forma de pagamento
        pagamento_layout = QFormLayout()
        
        self.forma_combo = QComboBox()
        self.forma_combo.addItems(["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX"])
        self.forma_combo.currentIndexChanged.connect(self.atualizar_campos_pagamento)
        pagamento_layout.addRow("Forma de Pagamento:", self.forma_combo)
        
        # Campo para valor recebido (visível apenas para dinheiro)
        valor_recebido_widget = QWidget()
        valor_recebido_layout = QHBoxLayout(valor_recebido_widget)
        valor_recebido_layout.setContentsMargins(0, 0, 0, 0)
        
        self.valor_recebido_input = QLineEdit()
        self.valor_recebido_input.setPlaceholderText("0.00")
        self.valor_recebido_input.textChanged.connect(self.calcular_troco)
        valor_recebido_layout.addWidget(self.valor_recebido_input)
        
        # Botões de valor rápido
        for valor in [self.total, self.total + 10, self.total + 20, self.total * 2]:
            btn = QPushButton(f"R${valor:.0f}")
            btn.setStyleSheet("padding: 5px;")
            btn.clicked.connect(lambda _, v=valor: self.valor_recebido_input.setText(str(v)))
            valor_recebido_layout.addWidget(btn)
        
        self.valor_recebido_row = pagamento_layout.addRow("Valor Recebido (R$):", valor_recebido_widget)
        
        # Troco
        self.troco_label = QLabel("R$ 0.00")
        self.troco_label.setStyleSheet("font-weight: bold;")
        self.troco_row = pagamento_layout.addRow("Troco:", self.troco_label)
        
        # Parcelas (para cartão de crédito)
        self.parcelas_combo = QComboBox()
        self.parcelas_combo.addItems(["1x sem juros", "2x sem juros", "3x sem juros", "4x sem juros"])
        self.parcelas_row = pagamento_layout.addRow("Parcelas:", self.parcelas_combo)
        
        # Chave PIX (para PIX)
        self.pix_input = QLineEdit()
        self.pix_input.setPlaceholderText("CPF, E-mail ou Telefone")
        self.pix_row = pagamento_layout.addRow("Chave PIX:", self.pix_input)
        
        layout.addLayout(pagamento_layout)
        
        # Configurações iniciais dos campos de pagamento
        self.atualizar_campos_pagamento(0)  # Dinheiro
        
        # Botões
        button_layout = QHBoxLayout()
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancelar_btn)
        
        finalizar_btn = QPushButton("Finalizar Venda")
        finalizar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        finalizar_btn.clicked.connect(self.aceitar)
        button_layout.addWidget(finalizar_btn)
        
        layout.addLayout(button_layout)
    
    def atualizar_campos_pagamento(self, index):
        """Atualiza os campos visíveis de acordo com a forma de pagamento"""
        forma = self.forma_combo.currentText()
        
        # Esconder todos os campos específicos
        self.valor_recebido_row.labelItem.widget().setVisible(forma == "Dinheiro")
        self.valor_recebido_row.fieldItem.widget().setVisible(forma == "Dinheiro")
        self.troco_row.labelItem.widget().setVisible(forma == "Dinheiro")
        self.troco_row.fieldItem.widget().setVisible(forma == "Dinheiro")
        
        self.parcelas_row.labelItem.widget().setVisible(forma == "Cartão de Crédito")
        self.parcelas_row.fieldItem.widget().setVisible(forma == "Cartão de Crédito")
        
        self.pix_row.labelItem.widget().setVisible(forma == "PIX")
        self.pix_row.fieldItem.widget().setVisible(forma == "PIX")
    
    def calcular_troco(self):
        """Calcula o troco quando valor recebido é alterado"""
        try:
            valor_recebido = float(self.valor_recebido_input.text())
            troco = valor_recebido - self.total
            self.troco_label.setText(f"R$ {troco:.2f}")
            
            # Muda a cor do troco
            if troco < 0:
                self.troco_label.setStyleSheet("font-weight: bold; color: red;")
            else:
                self.troco_label.setStyleSheet("font-weight: bold; color: green;")
        except ValueError:
            self.troco_label.setText("R$ 0.00")
            self.troco_label.setStyleSheet("font-weight: bold;")
    
    def aceitar(self):
        """Valida e aceita o formulário"""
        forma = self.forma_combo.currentText()
        
        if forma == "Dinheiro":
            try:
                valor_recebido = float(self.valor_recebido_input.text())
                if valor_recebido < self.total:
                    QMessageBox.warning(self, "Erro", "Valor recebido insuficiente!")
                    return
            except ValueError:
                QMessageBox.warning(self, "Erro", "Valor recebido inválido!")
                return
        elif forma == "PIX":
            if not self.pix_input.text():
                QMessageBox.warning(self, "Erro", "Informe a chave PIX!")
                return
        
        self.accept()
    
    def get_dados_pagamento(self):
        """Retorna os dados do pagamento"""
        forma = self.forma_combo.currentText()
        dados = {"forma": forma}
        
        if forma == "Dinheiro":
            dados["valor_recebido"] = float(self.valor_recebido_input.text())
            dados["troco"] = dados["valor_recebido"] - self.total
        elif forma == "Cartão de Crédito":
            dados["parcelas"] = self.parcelas_combo.currentText()
        elif forma == "PIX":
            dados["chave"] = self.pix_input.text()
        
        return dados

class HistoricoVendasWindow(QMainWindow):
    """Janela para visualização do histórico de vendas"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Vendas")
        self.setGeometry(100, 100, 1000, 600)
        self.setup_ui()
        self.carregar_vendas()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Histórico de Vendas")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Filtros por data
        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("De:"))
        
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addDays(-30))
        data_layout.addWidget(self.data_inicio)
        
        data_layout.addWidget(QLabel("Até:"))
        
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        data_layout.addWidget(self.data_fim)
        
        filtrar_btn = QPushButton("Filtrar")
        filtrar_btn.clicked.connect(self.filtrar_vendas)
        data_layout.addWidget(filtrar_btn)
        
        header_layout.addLayout(data_layout)
        
        layout.addLayout(header_layout)
        
        # Tabela de vendas
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)  # ID, Data, Cliente, Items, Total, Ações
        self.tabela.setHorizontalHeaderLabels(["ID", "Data", "Cliente", "Itens", "Total", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Items estica
        
        layout.addWidget(self.tabela)
        
        # Rodapé com resumo
        footer_frame = QFrame()
        footer_frame.setFrameShape(QFrame.StyledPanel)
        footer_frame.setStyleSheet("background-color: #f8f8f8; padding: 10px;")
        footer_layout = QHBoxLayout(footer_frame)
        
        self.total_vendas_label = QLabel("Total de Vendas: 0")
        footer_layout.addWidget(self.total_vendas_label)
        
        footer_layout.addStretch()
        
        self.valor_total_label = QLabel("Valor Total: R$ 0,00")
        self.valor_total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        footer_layout.addWidget(self.valor_total_label)
        
        layout.addWidget(footer_frame)
        
        # Botão voltar
        voltar_layout = QHBoxLayout()
        voltar_layout.addStretch()
        
        voltar_btn = QPushButton("Voltar ao Menu")
        voltar_btn.clicked.connect(self.close)
        voltar_layout.addWidget(voltar_btn)
        
        layout.addLayout(voltar_layout)
    
    def carregar_vendas(self):
        """Carrega as vendas do banco de dados"""
        # Aqui você implementaria a lógica para carregar do controller
        # vendas = self.venda_controller.listar(
        #     data_inicio=self.data_inicio.date().toPyDate(),
        #     data_fim=self.data_fim.date().toPyDate()
        # )
        
        # Vamos usar dados de exemplo por enquanto
        vendas = [
            {
                "id": "V001", 
                "data": "10/05/2025", 
                "cliente": "Cliente 1", 
                "itens": [
                    {"nome": "Café com Leite", "qtd": 2, "preco": 5.35},
                    {"nome": "Pão de Queijo", "qtd": 3, "preco": 3.50}
                ],
                "total": 21.20
            },
            {
                "id": "V002", 
                "data": "09/05/2025", 
                "cliente": "Cliente 2", 
                "itens": [
                    {"nome": "Bolo de Cenoura", "qtd": 1, "preco": 32.90}
                ],
                "total": 32.90
            },
            {
                "id": "V003", 
                "data": "08/05/2025", 
                "cliente": "Cliente 3", 
                "itens": [
                    {"nome": "Refrigerante Cola", "qtd": 2, "preco": 6.50},
                    {"nome": "Cookies", "qtd": 4, "preco": 4.00}
                ],
                "total": 29.00
            },
        ]
        
        # Preencher a tabela
        self.preencher_tabela(vendas)
        
        # Atualizar totais
        self.atualizar_totais(vendas)
    
    def preencher_tabela(self, vendas):
        """Preenche a tabela com as vendas"""
        self.tabela.setRowCount(0)  # Limpa a tabela
        
        for venda in vendas:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            # ID
            self.tabela.setItem(row, 0, QTableWidgetItem(venda["id"]))
            
            # Data
            self.tabela.setItem(row, 1, QTableWidgetItem(venda["data"]))
            
            # Cliente
            self.tabela.setItem(row, 2, QTableWidgetItem(venda["cliente"]))
            
            # Itens (concatenados)
            itens_str = ", ".join([f"{item['qtd']}x {item['nome']}" for item in venda["itens"]])
            self.tabela.setItem(row, 3, QTableWidgetItem(itens_str))
            
            # Total
            total_item = QTableWidgetItem(f"R$ {venda['total']:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela.setItem(row, 4, total_item)
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            acoes_layout.setSpacing(5)
            
            # Botão visualizar detalhes
            visualizar_btn = QPushButton("👁")
            visualizar_btn.setToolTip("Visualizar Detalhes")
            visualizar_btn.setStyleSheet("border: none; color: blue;")
            visualizar_btn.clicked.connect(lambda _, v=venda: self.visualizar_detalhes(v))
            acoes_layout.addWidget(visualizar_btn)
            
            # Botão imprimir
            imprimir_btn = QPushButton("🖨")
            imprimir_btn.setToolTip("Imprimir")
            imprimir_btn.setStyleSheet("border: none;")
            imprimir_btn.clicked.connect(lambda _, v=venda: self.imprimir_recibo(v))
            acoes_layout.addWidget(imprimir_btn)
            
            acoes_layout.addStretch()
            
            self.tabela.setCellWidget(row, 5, acoes_widget)
    
    def atualizar_totais(self, vendas):
        """Atualiza os totais exibidos no rodapé"""
        total_vendas = len(vendas)
        valor_total = sum(v["total"] for v in vendas)
        
        self.total_vendas_label.setText(f"Total de Vendas: {total_vendas}")
        self.valor_total_label.setText(f"Valor Total: R$ {valor_total:.2f}")
    
    def filtrar_vendas(self):
        """Filtra vendas por data"""
        # No sistema real, isso chamaria o controller
        # vendas = self.venda_controller.listar(
        #     data_inicio=self.data_inicio.date().toPyDate(),
        #     data_fim=self.data_fim.date().toPyDate()
        # )
        
        # Vamos apenas recarregar para demonstração
        self.carregar_vendas()
        
        QMessageBox.information(
            self, 
            "Filtro Aplicado", 
            f"Filtro aplicado de {self.data_inicio.date().toString('dd/MM/yyyy')} até {self.data_fim.date().toString('dd/MM/yyyy')}"
        )
    
    def visualizar_detalhes(self, venda):
        """Mostra detalhes de uma venda"""
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Detalhes da Venda {venda['id']}")
        
        # Constrói o texto de detalhes
        detalhes = f"<b>Data:</b> {venda['data']}<br>"
        detalhes += f"<b>Cliente:</b> {venda['cliente']}<br><br>"
        detalhes += "<b>Itens:</b><br>"
        
        for item in venda['itens']:
            subtotal = item['qtd'] * item['preco']
            detalhes += f"{item['qtd']}x {item['nome']} - R$ {item['preco']:.2f} = R$ {subtotal:.2f}<br>"
        
        detalhes += f"<br><b>Total:</b> R$ {venda['total']:.2f}"
        
        msg.setText(detalhes)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def imprimir_recibo(self, venda):
        """Simula a impressão de um recibo"""
        # No sistema real, isso chamaria a função de impressão
        QMessageBox.information(
            self, 
            "Impressão", 
            f"Imprimindo recibo da venda {venda['id']}..."
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HistoricoVendasWindow()
    window.show()
    sys.exit(app.exec_())