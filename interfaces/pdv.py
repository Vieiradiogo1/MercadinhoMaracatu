import sys
import os
import requests
import ctypes
import ctypes.wintypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolButton, QLabel, QLineEdit, QListWidget, QListWidgetItem, QFrame, QComboBox, QSizePolicy, QScrollArea, QPushButton
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize

# >> Mude aqui para ajustar o tempo limite das requisições de imagem <<
TIMEOUT_SEGS = 12

def slugify(nome):
    return ''.join(c if c.isalnum() else '_' for c in nome.lower()).replace('__','_')

def get_assets_dir():
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base, 'assets')

def get_produto_img_path(nome_produto):
    assets = get_assets_dir()
    pasta_produtos = os.path.join(assets, 'produtos')
    if not os.path.exists(pasta_produtos):
        os.makedirs(pasta_produtos)
    nome_arquivo = slugify(nome_produto) + ".jpg"
    return os.path.join(pasta_produtos, nome_arquivo)

def buscar_imagem_open_food_facts(nome_produto):
    url = f"https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": nome_produto,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "fields": "product_name,image_front_small_url"
    }
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT_SEGS)
        if resp.status_code == 200:
            data = resp.json()
            produtos = data.get('products', [])
            for prod in produtos:
                img_url = prod.get("image_front_small_url")
                prod_name = prod.get("product_name", "").strip().lower()
                if img_url and prod_name and nome_produto.lower() in prod_name:
                    return img_url
            for prod in produtos:
                img_url = prod.get("image_front_small_url")
                if img_url:
                    return img_url
    except Exception as e:
        print(f"Erro buscando imagem do Open Food Facts: {e}")
    return None

class ProdutoCard(QWidget):
    def __init__(self, nome, preco, cor, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.preco = preco
        self.cor = cor
        self.produto = {"nome": nome, "preco": preco, "cor": cor}

        self.setStyleSheet("""
            background: #fff;
            border-radius: 16px;
            border: 1px solid #ececec;
        """)
        self.setFixedSize(170, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.img_label = QLabel()
        self.img_label.setFixedSize(70, 70)
        self.img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img_label, alignment=Qt.AlignHCenter)

        self.set_imagem_produto()

        nome_lbl = QLabel(nome)
        nome_lbl.setAlignment(Qt.AlignCenter)
        nome_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        nome_lbl.setStyleSheet("color: #23272f; margin-top: 2px;")
        layout.addWidget(nome_lbl)

        preco_lbl = QLabel(f"R$ {preco:.2f}")
        preco_lbl.setAlignment(Qt.AlignCenter)
        preco_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        preco_lbl.setStyleSheet("color: #22bb55; margin-bottom: 8px;")
        layout.addWidget(preco_lbl)

        btn_add = QPushButton("Adicionar")
        btn_add.setStyleSheet("""
            QPushButton {
                background: #22bb55; color: #fff; border-radius: 8px;
                font-weight: bold; font-size: 14px; padding: 8px 0;
            }
            QPushButton:hover {
                background: #006e3d;
            }
        """)
        btn_add.clicked.connect(lambda: self.adicionar_produto())
        layout.addWidget(btn_add)
        layout.addStretch()

    def set_imagem_produto(self):
        img_path = get_produto_img_path(self.nome)
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.img_label.setPixmap(pixmap)
                return
        img_url = buscar_imagem_open_food_facts(self.nome)
        if img_url:
            try:
                img_data = requests.get(img_url, timeout=TIMEOUT_SEGS).content
                with open(img_path, "wb") as f:
                    f.write(img_data)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.img_label.setPixmap(pixmap)
                return
            except Exception as e:
                print("Erro ao baixar/salvar imagem:", e)
        pixmap = QPixmap(70, 70)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        color = QColor(self.cor)
        painter.setRenderHint(QPainter.Antialiasing, True)
        brush = QBrush(color)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 70, 70)
        painter.setPen(Qt.white)
        font = QFont("Segoe UI", 18, QFont.Bold)
        painter.setFont(font)
        initials = "".join([p[0] for p in self.nome.split()[:2]]).upper()
        painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)
        painter.end()
        self.img_label.setPixmap(pixmap)

    def adicionar_produto(self):
        parent = self.parent()
        while parent and not hasattr(parent, "adicionar_carrinho"):
            parent = parent.parent()
        if parent and hasattr(self, "produto"):
            parent.adicionar_carrinho(self.produto)

class PDVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        user32 = ctypes.windll.user32
        work_area = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(work_area), 0)
        width = work_area.right - work_area.left
        height = work_area.bottom - work_area.top
        self.setGeometry(work_area.left, work_area.top, width, height)

        self.setWindowTitle("PDV Moderno - Sistema do Mercadinho da Gi")
        self.produtos_info = []
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central)
        central.setStyleSheet("background: #f7f8fa;")

        sidebar = QVBoxLayout()
        sidebar.setSpacing(0)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setAlignment(Qt.AlignTop)
        sidebar_labels = [
            ("Vender", "assets/sell.png"),
            ("Pedidos", "assets/orders.png"),
            ("Produtos", "assets/products.png"),
            ("Histórico", "assets/history.png"),
            ("Estatísticas", "assets/statistics.png"),
            ("Configurações", "assets/settings.png")
        ]
        base_dir = get_assets_dir()
        for label, icon_file in sidebar_labels:
            icon_path = os.path.join(base_dir, icon_file)
            btn = QToolButton()
            btn.setText(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(28, 28))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QToolButton {
                    background: transparent;
                    border: none;
                    color: #fff;
                    font-size: 15px;
                    font-weight: 600;
                    padding: 18px 4px 10px 4px;
                    border-radius: 0px;
                }
                QToolButton:hover {
                    background: #343a40;
                    color: #80bfff;
                }
            """)
            sidebar.addWidget(btn)

        btn_sair = QToolButton()
        btn_sair.setText("Sair")
        btn_sair.setIcon(QIcon(os.path.join(base_dir, "logout.png")))
        btn_sair.setIconSize(QSize(28, 28))
        btn_sair.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn_sair.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_sair.setCursor(Qt.PointingHandCursor)
        btn_sair.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                color: #fff;
                font-size: 15px;
                font-weight: 600;
                padding: 18px 4px 10px 4px;
                border-radius: 0px;
            }
            QToolButton:hover {
                background: #b71c1c;
                color: #fff176;
            }
        """)
        btn_sair.clicked.connect(QApplication.quit)
        sidebar.addStretch()
        sidebar.addWidget(btn_sair)
        frame_sidebar = QFrame()
        frame_sidebar.setLayout(sidebar)
        frame_sidebar.setFixedWidth(140)
        frame_sidebar.setStyleSheet("""
            background: #23272f;
            border: none;
            border-radius: 0px;
        """)
        main_layout.addWidget(frame_sidebar)

        mid_layout = QVBoxLayout()
        top_bar = QHBoxLayout()
        self.txt_busca = QLineEdit()
        self.txt_busca.setStyleSheet("""
            background: #fff;
            border-radius: 8px;
            padding-left: 10px;
            font-size: 15px;
        """)
        self.txt_busca.setPlaceholderText("Nome ou código")
        self.txt_busca.setFixedHeight(36)
        top_bar.addWidget(self.txt_busca)
        self.categorias = QComboBox()
        self.categorias.setStyleSheet("""
            background: #fff;
            border-radius: 8px;
            padding: 8px;
            font-size: 15px;
        """)
        self.categorias.addItem("Todas as Categorias")
        top_bar.addWidget(self.categorias)
        top_bar.addStretch()
        mid_layout.addLayout(top_bar)

        self.produtos_area = QScrollArea()
        self.produtos_area.setWidgetResizable(True)
        prod_widget = QWidget()
        self.prod_grid = QGridLayout(prod_widget)
        self.prod_grid.setSpacing(18)
        self.produtos_area.setWidget(prod_widget)
        mid_layout.addWidget(self.produtos_area)
        main_layout.addLayout(mid_layout, 3)

        carrinho_layout = QVBoxLayout()
        carrinho_layout.setAlignment(Qt.AlignTop)
        carrinho_label = QLabel("Carrinho")
        carrinho_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        carrinho_layout.addWidget(carrinho_label)
        self.list_carrinho = QListWidget()
        carrinho_layout.addWidget(self.list_carrinho)
        self.lbl_subtotal = QLabel("Subtotal: R$ 0,00")
        self.lbl_total = QLabel("Total: R$ 0,00")
        carrinho_layout.addWidget(self.lbl_subtotal)
        carrinho_layout.addWidget(self.lbl_total)
        btn_pagamento = QPushButton("Ir para pagamento")
        btn_pagamento.setStyleSheet("""
            font-size: 16px;
            background: #22bb55;
            color: white;
            padding: 14px;
            border-radius: 10px;
            font-weight: bold;
        """)
        carrinho_layout.addWidget(btn_pagamento)
        frame_carrinho = QFrame()
        frame_carrinho.setLayout(carrinho_layout)
        frame_carrinho.setFixedWidth(290)
        main_layout.addWidget(frame_carrinho)

        self.carregar_produtos()

    def carregar_produtos(self):
        produtos = [
            {"nome": "Brahma", "preco": 5.90, "cor": "#ffb74d"},
            {"nome": "Café com leite", "preco": 5.35, "cor": "#81c784"},
            {"nome": "Cookies chocolate", "preco": 4.00, "cor": "#64b5f6"},
            {"nome": "Capuccino Iced", "preco": 6.00, "cor": "#ba68c8"},
            {"nome": "Cheese cake de frutas", "preco": 16.00, "cor": "#ffd54f"},
            {"nome": "Chá de ervas", "preco": 8.00, "cor": "#aed581"},
            {"nome": "Cupcake belga", "preco": 6.70, "cor": "#e57373"},
        ]
        self.produtos_info = produtos

        for i in reversed(range(self.prod_grid.count())):
            widget_to_remove = self.prod_grid.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        for i, prod in enumerate(produtos):
            card = ProdutoCard(prod["nome"], prod["preco"], prod["cor"])
            card.produto = prod
            row, col = divmod(i, 4)
            self.prod_grid.addWidget(card, row, col, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.prod_grid.setHorizontalSpacing(18)
        self.prod_grid.setVerticalSpacing(18)
        self.prod_grid.setContentsMargins(20, 20, 20, 20)

    def adicionar_carrinho(self, produto):
        item = QListWidgetItem(f"{produto['nome']}   R$ {produto['preco']:.2f}")
        self.list_carrinho.addItem(item)
        self.atualizar_totais()

    def atualizar_totais(self):
        total = 0
        for i in range(self.list_carrinho.count()):
            text = self.list_carrinho.item(i).text()
            try:
                valor_str = text.split('R$')[-1].strip().replace(',', '.')
                total += float(valor_str)
            except Exception:
                pass
        self.lbl_subtotal.setText(f"Subtotal: R$ {total:,.2f}".replace('.', ','))
        self.lbl_total.setText(f"Total: R$ {total:,.2f}".replace('.', ','))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PDVWindow()
    w.show()
    sys.exit(app.exec_())