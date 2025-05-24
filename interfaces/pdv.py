import sys
import os
import requests
import ctypes
import ctypes.wintypes
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QToolButton, QLabel, QLineEdit, QListWidget, QListWidgetItem, QFrame, QComboBox, QSizePolicy,
    QScrollArea, QPushButton, QSpacerItem, QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QRadioButton, QButtonGroup, QMessageBox, QStackedWidget
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize, QDateTime

# ==============================
# CONFIGURAÇÕES E UTILITÁRIOS
# ==============================
TIMEOUT_SEGS = 12
COR_BOTAO = "#39ceab"
COR_CARD = "#81c784"

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

def get_payment_icon_pixmap(size=34):
    svg = '''
    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="2.5" y="5.5" width="19" height="13" rx="2.5" stroke="#39ceab" stroke-width="2"/>
    <rect x="4.5" y="10" width="3" height="3" rx="1.5" fill="#39ceab"/>
    <rect x="9" y="13" width="7" height="1.5" rx="0.75" fill="#39ceab"/>
    <rect x="9" y="10" width="5" height="1.5" rx="0.75" fill="#39ceab"/>
    </svg>
    '''
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as tmp:
        tmp.write(svg.encode())
        tmp.close()
        pixmap = QPixmap(tmp.name)
    return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

# ==============================
# COMPONENTES DA TELA DE VENDER
# ==============================

class ProdutoCard(QWidget):
    def __init__(self, nome, preco, cor=COR_CARD, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.preco = preco
        self.cor = cor
        self.produto = {"nome": nome, "preco": preco, "cor": cor}

        self.setFixedSize(220, 320)
        self.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {cor}, stop:1 #fafafa);
            border-radius: 22px;
            border: 1px solid #e0e3ea;
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(30,185,94,40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self.img_label = QLabel()
        self.img_label.setFixedSize(98, 98)
        self.img_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.img_label, alignment=Qt.AlignHCenter)
        self.set_imagem_produto()

        nome_preco = QWidget()
        nome_preco_layout = QVBoxLayout(nome_preco)
        nome_preco_layout.setContentsMargins(0, 0, 0, 0)
        nome_preco_layout.setSpacing(2)
        
        nome_lbl = QLabel(nome)
        nome_lbl.setWordWrap(True)
        nome_lbl.setAlignment(Qt.AlignCenter)
        nome_lbl.setFont(QFont("Montserrat", 9, QFont.Bold))
        nome_lbl.setStyleSheet("""
            background: rgba(255,255,255,0.92);
            color: #23272f;
            border-radius: 7px;
            padding: 2px 3px;
        """)
        nome_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        nome_lbl.setMaximumHeight(56)
        nome_lbl.setMinimumHeight(25)
        nome_preco_layout.addWidget(nome_lbl)

        preco_lbl = QLabel(f"R$ {preco:.2f}")
        preco_lbl.setAlignment(Qt.AlignCenter)
        preco_lbl.setFont(QFont("Montserrat", 10, QFont.Bold))
        preco_lbl.setStyleSheet("""
            background: rgba(230,255,240,0.90);
            color: #1eb95e;
            border-radius: 7px;
            padding: 1px 3px;
        """)
        preco_lbl.setMaximumHeight(24)
        preco_lbl.setMinimumHeight(18)
        nome_preco_layout.addWidget(preco_lbl)
        layout.addWidget(nome_preco)

        btn_add = QPushButton("Adicionar")
        btn_add.setFont(QFont("Montserrat", 11, QFont.Bold))
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedHeight(33)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background: {COR_BOTAO};
                color: #fff;
                border-radius: 10px;
                font-weight: bold;
                border: none;
                letter-spacing: 0.3px;
                padding: 7px 22px;
            }}
            QPushButton:hover {{
                background: #22b88e;
            }}
        """)
        shadow_btn = QGraphicsDropShadowEffect(btn_add)
        shadow_btn.setBlurRadius(8)
        shadow_btn.setColor(QColor(57, 206, 171, 90))
        shadow_btn.setOffset(0, 4)
        btn_add.setGraphicsEffect(shadow_btn)
        btn_add.clicked.connect(lambda: self.adicionar_produto())
        layout.addWidget(btn_add, alignment=Qt.AlignHCenter)
        layout.addStretch()

    def set_imagem_produto(self):
        img_path = get_produto_img_path(self.nome)
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(98, 98, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.img_label.setPixmap(pixmap)
                return
        pixmap = QPixmap(98, 98)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(QColor(self.cor)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 98, 98)
        painter.setPen(Qt.white)
        font = QFont("Montserrat", 31, QFont.Bold)
        painter.setFont(font)
        initials = ''.join([p[0] for p in self.nome.split()[:2]]).upper()
        painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)
        painter.end()
        self.img_label.setPixmap(pixmap)
        img_url = buscar_imagem_open_food_facts(self.nome)
        if img_url:
            try:
                img_data = requests.get(img_url, timeout=TIMEOUT_SEGS).content
                with open(img_path, "wb") as f:
                    f.write(img_data)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(98, 98, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.img_label.setPixmap(pixmap)
            except Exception as e:
                print("Erro ao baixar/salvar imagem:", e)

    def adicionar_produto(self):
        parent = self.parent()
        while parent and not hasattr(parent, "adicionar_carrinho"):
            parent = parent.parent()
        if parent and hasattr(self, "produto"):
            parent.adicionar_carrinho(self.produto)

class CarrinhoItemWidget(QWidget):
    def __init__(self, nome, preco, quantidade, remover_callback):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        nome_lbl = QLabel(f"{quantidade}x {nome}")
        nome_lbl.setFont(QFont("Montserrat", 10))
        layout.addWidget(nome_lbl, 2)
        preco_lbl = QLabel(f"R$ {preco:.2f}")
        preco_lbl.setFont(QFont("Montserrat", 10, QFont.Bold))
        preco_lbl.setStyleSheet(f"color: {COR_CARD};")
        layout.addWidget(preco_lbl, 1)
        btn_remove = QPushButton()
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setFixedSize(26, 26)
        trash_path = os.path.join(get_assets_dir(), "trash.svg")
        btn_remove.setIcon(QIcon(trash_path) if os.path.exists(trash_path) else QIcon())
        btn_remove.setIconSize(QSize(18, 18))
        btn_remove.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: #f7d6d6;
                border-radius: 13px;
            }
        """)
        btn_remove_shadow = QGraphicsDropShadowEffect(btn_remove)
        btn_remove_shadow.setBlurRadius(10)
        btn_remove_shadow.setColor(QColor(57, 206, 171, 100))
        btn_remove_shadow.setOffset(0, 4)
        btn_remove.setGraphicsEffect(btn_remove_shadow)
        btn_remove.clicked.connect(remover_callback)
        layout.addWidget(btn_remove)

class LixeiraItemWidget(QWidget):
    def __init__(self, nome, quantidade, preco_unit, restaurar_callback):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        nome_lbl = QLabel(f"{quantidade}x {nome}")
        nome_lbl.setFont(QFont("Montserrat", 10))
        layout.addWidget(nome_lbl, 2)
        preco_lbl = QLabel(f"R$ {preco_unit*quantidade:.2f}")
        preco_lbl.setFont(QFont("Montserrat", 10, QFont.Bold))
        preco_lbl.setStyleSheet("color: #b71c1c;")
        layout.addWidget(preco_lbl, 1)
        btn_restore = QPushButton("Restaurar")
        btn_restore.setCursor(Qt.PointingHandCursor)
        btn_restore.setFixedHeight(24)
        btn_restore.setStyleSheet(f"""
            QPushButton {{
                background: {COR_BOTAO};
                color: #fff;
                border-radius: 7px;
                font-weight: bold;
                border: none;
                padding: 3px 14px;
            }}
            QPushButton:hover {{
                background: #22b88e;
            }}
        """)
        btn_restore_shadow = QGraphicsDropShadowEffect(btn_restore)
        btn_restore_shadow.setBlurRadius(8)
        btn_restore_shadow.setColor(QColor(57, 206, 171, 80))
        btn_restore_shadow.setOffset(0, 3)
        btn_restore.setGraphicsEffect(btn_restore_shadow)
        btn_restore.clicked.connect(restaurar_callback)
        layout.addWidget(btn_restore)

class BarraSuperior(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)
        lupa = QLabel()
        lupa.setPixmap(QIcon.fromTheme("edit-find").pixmap(22,22))
        lupa.setFixedWidth(30)
        lupa.setAlignment(Qt.AlignCenter)
        layout.addWidget(lupa)
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Buscar produto...")
        self.busca.setFixedHeight(38)
        self.busca.setFont(QFont("Montserrat", 11))
        self.busca.setStyleSheet("""
            QLineEdit {
                background: #fff;
                border-radius: 12px;
                padding-left: 38px;
                font-size: 15px;
                border: 1px solid #e0e3ea;
            }
        """)
        layout.addWidget(self.busca, 1)
        self.categorias = QComboBox()
        self.categorias.addItem("Todas as Categorias")
        self.categorias.setFixedHeight(38)
        self.categorias.setFont(QFont("Montserrat", 11))
        self.categorias.setStyleSheet("""
            QComboBox {
                background: #fff;
                border-radius: 13px;
                padding: 8px 24px 8px 14px;
                font-size: 15px;
                border: 1px solid #e0e3ea;
                min-width: 140px;
                color: #23272f;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 34px;
            }
            QComboBox QAbstractItemView {
                border-radius: 8px;
                background: #fff;
                font-size: 15px;
                outline: none;
            }
        """)
        layout.addWidget(self.categorias)
        layout.addStretch()

# ==============================
# DIALOG DE PAGAMENTO
# ==============================

class PagamentoDialog(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Pagamento")
        self.setModal(True)
        self.setFixedWidth(480)
        self.setMinimumHeight(460)
        self.setStyleSheet(f"""
            QDialog {{
                background: #fff;
                border-radius: 18px;
                border: 2.5px solid {COR_BOTAO};
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(57, 206, 171, 110))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)

        self.total = total
        self.pagamentos = []
        self.restante = total

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(22, 22, 22, 22)

        barra_sup = QHBoxLayout()
        icone = QLabel()
        icone.setPixmap(get_payment_icon_pixmap(36))
        barra_sup.addWidget(icone)
        titulo = QLabel("Pagamento")
        titulo.setFont(QFont("Montserrat", 18, QFont.Bold))
        titulo.setStyleSheet(f"color: {COR_BOTAO};")
        barra_sup.addWidget(titulo)
        barra_sup.addStretch()
        btn_fechar = QPushButton("✕")
        btn_fechar.setCursor(Qt.PointingHandCursor)
        btn_fechar.setFixedSize(30, 30)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #b71c1c;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background: #ffe0b2;
                border-radius: 14px;
            }
        """)
        btn_fechar.clicked.connect(self.reject)
        barra_sup.addWidget(btn_fechar)
        layout.addLayout(barra_sup)

        self.titulo = QLabel("Finalizar Venda")
        self.titulo.setFont(QFont("Montserrat", 17, QFont.Bold))
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet(f"color: {COR_BOTAO}; margin-bottom: 5px;")
        layout.addWidget(self.titulo)

        self.lbl_total = QLabel(f"Valor da compra: <b>R$ {total:,.2f}</b>")
        self.lbl_total.setFont(QFont("Montserrat", 14, QFont.Bold))
        self.lbl_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_total)

        self.lbl_restante = QLabel(f"Restante: <b>R$ {self.restante:,.2f}</b>")
        self.lbl_restante.setFont(QFont("Montserrat", 13))
        self.lbl_restante.setAlignment(Qt.AlignCenter)
        self.lbl_restante.setStyleSheet("color: #B71C1C; margin-bottom: 6px;")
        layout.addWidget(self.lbl_restante)

        self.forma_group = QButtonGroup(self)
        self.rb_credito = QRadioButton("Crédito")
        self.rb_debito = QRadioButton("Débito")
        self.rb_dinheiro = QRadioButton("Dinheiro")
        self.rb_pix = QRadioButton("Pix")
        for rb in [self.rb_credito, self.rb_debito, self.rb_dinheiro, self.rb_pix]:
            rb.setFont(QFont("Montserrat", 12))
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color: #222;
                    spacing: 8px;
                }}
                QRadioButton::indicator {{
                    width: 19px; height: 19px;
                }}
                QRadioButton::indicator:checked {{
                    background: {COR_BOTAO};
                    border: 2px solid {COR_BOTAO};
                }}
                QRadioButton::indicator:unchecked {{
                    border: 1.5px solid #bbb;
                }}
            """)
        self.forma_group.addButton(self.rb_credito)
        self.forma_group.addButton(self.rb_debito)
        self.forma_group.addButton(self.rb_dinheiro)
        self.forma_group.addButton(self.rb_pix)
        self.rb_dinheiro.setChecked(True)

        forma_layout = QHBoxLayout()
        for rb in [self.rb_credito, self.rb_debito, self.rb_dinheiro, self.rb_pix]:
            forma_layout.addWidget(rb)
        layout.addLayout(forma_layout)

        valor_layout = QHBoxLayout()
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Valor pago agora")
        self.input_valor.setFont(QFont("Montserrat", 12))
        self.input_valor.setFixedWidth(160)
        self.input_valor.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid #e0e3ea;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 15px;
                background: #f8fffd;
            }}
        """)
        self.input_valor.setText(str(round(self.restante, 2)))
        valor_layout.addWidget(self.input_valor)
        self.btn_adicionar = QPushButton("Adicionar Pagamento")
        self.btn_adicionar.setCursor(Qt.PointingHandCursor)
        self.btn_adicionar.setFont(QFont("Montserrat", 11, QFont.Bold))
        self.btn_adicionar.setStyleSheet(f"""
            QPushButton {{
                background: {COR_BOTAO};
                color: #fff;
                border-radius: 9px;
                padding: 7px 20px;
            }}
            QPushButton:hover {{
                background: #22b88e;
            }}
        """)
        btn_add_shadow = QGraphicsDropShadowEffect(self.btn_adicionar)
        btn_add_shadow.setBlurRadius(12)
        btn_add_shadow.setColor(QColor(57,206,171,70))
        btn_add_shadow.setOffset(0, 4)
        self.btn_adicionar.setGraphicsEffect(btn_add_shadow)
        self.btn_adicionar.clicked.connect(self.add_pagamento)
        valor_layout.addWidget(self.btn_adicionar)
        layout.addLayout(valor_layout)

        self.lbl_pagamentos = QLabel("")
        self.lbl_pagamentos.setFont(QFont("Montserrat", 10))
        self.lbl_pagamentos.setAlignment(Qt.AlignLeft)
        self.lbl_pagamentos.setWordWrap(True)
        layout.addWidget(self.lbl_pagamentos)

        self.box = QDialogButtonBox()
        self.btn_finalizar = QPushButton("Finalizar Venda")
        self.btn_finalizar.setFont(QFont("Montserrat", 12, QFont.Bold))
        self.btn_finalizar.setCursor(Qt.PointingHandCursor)
        self.btn_finalizar.setStyleSheet(f"""
            QPushButton {{
                background: {COR_BOTAO};
                color: #fff;
                border-radius: 9px;
                padding: 10px 32px;
            }}
            QPushButton:hover {{
                background: #22b88e;
            }}
        """)
        btn_finalizar_shadow = QGraphicsDropShadowEffect(self.btn_finalizar)
        btn_finalizar_shadow.setBlurRadius(13)
        btn_finalizar_shadow.setColor(QColor(57,206,171,90))
        btn_finalizar_shadow.setOffset(0, 5)
        self.btn_finalizar.setGraphicsEffect(btn_finalizar_shadow)
        self.btn_finalizar.clicked.connect(self.finalizar)
        self.box.addButton(self.btn_finalizar, QDialogButtonBox.AcceptRole)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFont(QFont("Montserrat", 12))
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background: #fff;
                color: #b71c1c;
                border-radius: 9px;
                border: 1.5px solid #ffd180;
                padding: 10px 22px;
            }
            QPushButton:hover {
                background: #ffe0b2;
            }
        """)
        btn_cancelar_shadow = QGraphicsDropShadowEffect(self.btn_cancelar)
        btn_cancelar_shadow.setBlurRadius(8)
        btn_cancelar_shadow.setColor(QColor(183, 28, 28, 70))
        btn_cancelar_shadow.setOffset(0, 3)
        self.btn_cancelar.setGraphicsEffect(btn_cancelar_shadow)
        self.btn_cancelar.clicked.connect(self.reject)
        self.box.addButton(self.btn_cancelar, QDialogButtonBox.RejectRole)
        layout.addWidget(self.box)

        self.update_pagamentos()

    def add_pagamento(self):
        try:
            valor = float(self.input_valor.text().replace(",", "."))
        except Exception:
            QMessageBox.warning(self, "Valor inválido", "Digite um valor numérico para o pagamento.")
            return
        if valor <= 0:
            QMessageBox.warning(self, "Valor inválido", "O valor deve ser maior que zero.")
            return
        if valor > self.restante:
            QMessageBox.warning(self, "Valor inválido", f"O valor inserido (R$ {valor:,.2f}) é maior que o restante (R$ {self.restante:,.2f})!")
            return
        forma = self.get_pagamento()
        self.pagamentos.append((valor, forma))
        self.restante -= valor
        self.input_valor.setText(str(round(self.restante,2)) if self.restante > 0 else "")
        self.update_pagamentos()

    def update_pagamentos(self):
        self.lbl_restante.setText(f"Restante: <b>R$ {self.restante:,.2f}</b>")
        texto = ""
        for val, f in self.pagamentos:
            texto += f"<b>{f}:</b> R$ {val:,.2f}<br>"
        self.lbl_pagamentos.setText(texto)
        self.btn_finalizar.setEnabled(self.restante <= 0 or (self.restante > 0 and len(self.pagamentos) > 0))

    def finalizar(self):
        if self.restante > 0:
            resp = QMessageBox.question(self, "Pagamento incompleto",
                f"Restam R$ {self.restante:,.2f} para quitar a venda.\nDeseja finalizar assim mesmo (venda pendente)?",
                QMessageBox.Yes|QMessageBox.No)
            if resp == QMessageBox.No:
                return
        self.accept()

    def get_pagamento(self):
        if self.rb_credito.isChecked():
            return "Crédito"
        elif self.rb_debito.isChecked():
            return "Débito"
        elif self.rb_pix.isChecked():
            return "Pix"
        else:
            return "Dinheiro"

    def get_result(self):
        return {
            "pagamentos": self.pagamentos,
            "restante": self.restante
        }

# ==============================
# TELA DE VENDER (FUNCIONAL)
# ==============================

class VenderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.produtos_info = []
        self.carrinho = []
        self.lixeira = []
        self.pedidos = []
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        mid_layout = QVBoxLayout()
        self.barra_superior = BarraSuperior()
        mid_layout.addWidget(self.barra_superior)
        self.produtos_area = QScrollArea()
        self.produtos_area.setWidgetResizable(True)
        prod_widget = QWidget()
        self.prod_grid = QGridLayout(prod_widget)
        self.prod_grid.setSpacing(24)
        self.prod_grid.setContentsMargins(30, 30, 30, 30)
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
        lixeira_title = QLabel("Lixeira")
        lixeira_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #b71c1c; margin-top: 10px;")
        carrinho_layout.addWidget(lixeira_title)
        self.list_lixeira = QListWidget()
        carrinho_layout.addWidget(self.list_lixeira)
        self.lbl_subtotal = QLabel("Subtotal: R$ 0,00")
        self.lbl_total = QLabel("Total: R$ 0,00")
        carrinho_layout.addWidget(self.lbl_subtotal)
        carrinho_layout.addWidget(self.lbl_total)
        btn_pagamento = QPushButton("Ir para pagamento")
        btn_pagamento.clicked.connect(self.abrir_pagamento)
        carrinho_layout.addWidget(btn_pagamento)
        frame_carrinho = QFrame()
        frame_carrinho.setLayout(carrinho_layout)
        frame_carrinho.setFixedWidth(400)
        main_layout.addWidget(frame_carrinho)
        self.barra_superior.busca.textChanged.connect(self.atualizar_lista_produtos)
        self.barra_superior.categorias.currentIndexChanged.connect(self.atualizar_lista_produtos)
        self.carregar_produtos()
        self.refresh_lixeira()

    def carregar_produtos(self):
        produtos = [
            {"nome": "Brahma", "preco": 5.90, "cor": COR_CARD, "categoria": "Bebidas"},
            {"nome": "Café com leite", "preco": 5.35, "cor": COR_CARD, "categoria": "Bebidas"},
            {"nome": "Cookies chocolate", "preco": 4.00, "cor": COR_CARD, "categoria": "Doces"},
            {"nome": "Capuccino Iced", "preco": 6.00, "cor": COR_CARD, "categoria": "Bebidas"},
            {"nome": "Cheese cake de frutas", "preco": 16.00, "cor": COR_CARD, "categoria": "Doces"},
            {"nome": "Chá de ervas", "preco": 8.00, "cor": COR_CARD, "categoria": "Bebidas"},
            {"nome": "Cupcake belga", "preco": 6.70, "cor": COR_CARD, "categoria": "Doces"},
            {"nome": "Guaraná Antartica", "preco": 6.50, "cor": COR_CARD, "categoria": "Bebidas"},
            {"nome": "Refrigerante Laranja", "preco": 5.00, "cor": COR_CARD, "categoria": "Bebidas"},
            {"nome": "Produto com nome muito grande que vai até o final do card e precisa caber inteiro", "preco": 7.99, "cor": COR_CARD, "categoria": "Diversos"},
        ]
        self.produtos_info = produtos

        categorias = set(prod.get("categoria", "Diversos") for prod in self.produtos_info)
        self.barra_superior.categorias.clear()
        self.barra_superior.categorias.addItem("Todas as Categorias")
        for cat in sorted(categorias):
            self.barra_superior.categorias.addItem(cat)

        self.atualizar_lista_produtos()

    def atualizar_lista_produtos(self):
        termo = self.barra_superior.busca.text().strip().lower()
        categoria = self.barra_superior.categorias.currentText()
        for i in reversed(range(self.prod_grid.count())):
            widget_to_remove = self.prod_grid.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        idx = 0
        for prod in self.produtos_info:
            if termo and termo not in prod['nome'].lower():
                continue
            if categoria != "Todas as Categorias" and ('categoria' not in prod or prod['categoria'] != categoria):
                continue
            card = ProdutoCard(prod["nome"], prod["preco"], prod["cor"])
            card.produto = prod
            row, col = divmod(idx, 4)
            self.prod_grid.addWidget(card, row, col, alignment=Qt.AlignHCenter | Qt.AlignTop)
            idx += 1

    def adicionar_carrinho(self, produto):
        for item in self.carrinho:
            if item["nome"] == produto["nome"]:
                item["quantidade"] += 1
                self.refresh_carrinho()
                return
        self.carrinho.append({
            "nome": produto["nome"],
            "preco_unit": produto["preco"],
            "quantidade": 1
        })
        self.refresh_carrinho()

    def refresh_carrinho(self):
        self.list_carrinho.clear()
        for item in self.carrinho:
            widget = CarrinhoItemWidget(
                item["nome"],
                item["preco_unit"] * item["quantidade"],
                item["quantidade"],
                lambda checked=False, nome=item["nome"]: self.remover_do_carrinho(nome)
            )
            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.sizeHint())
            self.list_carrinho.addItem(list_item)
            self.list_carrinho.setItemWidget(list_item, widget)
        self.atualizar_totais()

    def remover_do_carrinho(self, nome_produto):
        for item in self.carrinho:
            if item["nome"] == nome_produto:
                item["quantidade"] -= 1
                for lixo in self.lixeira:
                    if lixo["nome"] == nome_produto:
                        lixo["quantidade"] += 1
                        break
                else:
                    self.lixeira.append({
                        "nome": item["nome"],
                        "preco_unit": item["preco_unit"],
                        "quantidade": 1
                    })
                if item["quantidade"] == 0:
                    self.carrinho.remove(item)
                break
        self.refresh_carrinho()
        self.refresh_lixeira()

    def refresh_lixeira(self):
        self.list_lixeira.clear()
        for lixo in self.lixeira:
            if lixo["quantidade"] > 0:
                widget = LixeiraItemWidget(
                    lixo["nome"], lixo["quantidade"], lixo["preco_unit"],
                    lambda checked=False, nome=lixo["nome"]: self.restaurar_da_lixeira(nome)
                )
                list_item = QListWidgetItem()
                list_item.setSizeHint(widget.sizeHint())
                self.list_lixeira.addItem(list_item)
                self.list_lixeira.setItemWidget(list_item, widget)

    def restaurar_da_lixeira(self, nome_produto):
        for lixo in self.lixeira:
            if lixo["nome"] == nome_produto and lixo["quantidade"] > 0:
                lixo["quantidade"] -= 1
                for item in self.carrinho:
                    if item["nome"] == nome_produto:
                        item["quantidade"] += 1
                        break
                else:
                    self.carrinho.append({
                        "nome": lixo["nome"],
                        "preco_unit": lixo["preco_unit"],
                        "quantidade": 1
                    })
                if lixo["quantidade"] == 0:
                    self.lixeira.remove(lixo)
                break
        self.refresh_carrinho()
        self.refresh_lixeira()

    def atualizar_totais(self):
        total = sum(item["preco_unit"] * item["quantidade"] for item in self.carrinho)
        self.lbl_subtotal.setText(f"Subtotal: R$ {total:,.2f}".replace('.', ','))
        self.lbl_total.setText(f"Total: R$ {total:,.2f}".replace('.', ','))

    def abrir_pagamento(self):
        if not self.carrinho:
            QMessageBox.warning(self, "Carrinho vazio", "Adicione produtos ao carrinho antes de finalizar a venda.")
            return
        total = sum(item["preco_unit"] * item["quantidade"] for item in self.carrinho)
        pag_dialog = PagamentoDialog(total, self)
        if pag_dialog.exec_() == QDialog.Accepted:
            pag_result = pag_dialog.get_result()
            if pag_result["restante"] > 0:
                status = "PENDENTE"
            else:
                status = "PAGO"
            pedido = {
                "itens": [item.copy() for item in self.carrinho],
                "total": total,
                "pagamentos": pag_result["pagamentos"],
                "restante": pag_result["restante"],
                "status": status,
                "data": QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            }
            self.pedidos.append(pedido)
            self.carrinho.clear()
            self.lixeira.clear()
            self.refresh_carrinho()
            self.refresh_lixeira()
            self.atualizar_totais()
            if status == "PAGO":
                QMessageBox.information(self, "Venda registrada", f"Venda salva com sucesso!\nPagamento quitado.")
            else:
                QMessageBox.warning(self, "Venda pendente", f"Venda salva mas ainda resta R$ {pag_result['restante']:,.2f} para quitar.")

# ==============================
# TELAS EXTRAS (Estoque, Histórico, Estatísticas, Configurações)
# ==============================

class EstoqueWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        lbl = QLabel("Estoque de Produtos")
        lbl.setFont(QFont("Montserrat", 18, QFont.Bold))
        layout.addWidget(lbl)
        self.table = QTableWidget(10, 4)
        self.table.setHorizontalHeaderLabels(["Produto", "Categoria", "Qtd. em Estoque", "Preço"])
        fake_produtos = [
            ("Brahma", "Bebidas", 15, "R$ 5,90"),
            ("Café com leite", "Bebidas", 23, "R$ 5,35"),
            ("Cookies chocolate", "Doces", 10, "R$ 4,00"),
            ("Cheese cake de frutas", "Doces", 3, "R$ 16,00"),
        ]
        for row, (nome, cat, qtd, preco) in enumerate(fake_produtos):
            self.table.setItem(row, 0, QTableWidgetItem(nome))
            self.table.setItem(row, 1, QTableWidgetItem(cat))
            self.table.setItem(row, 2, QTableWidgetItem(str(qtd)))
            self.table.setItem(row, 3, QTableWidgetItem(preco))
        layout.addWidget(self.table)
        btns = QHBoxLayout()
        btn_novo = QPushButton("Cadastrar Produto")
        btn_editar = QPushButton("Editar Produto")
        btn_remover = QPushButton("Remover Produto")
        btns.addWidget(btn_novo)
        btns.addWidget(btn_editar)
        btns.addWidget(btn_remover)
        layout.addLayout(btns)
        layout.addStretch()

class HistoricoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        lbl = QLabel("Histórico de Vendas")
        lbl.setFont(QFont("Montserrat", 18, QFont.Bold))
        layout.addWidget(lbl)
        self.table = QTableWidget(8, 4)
        self.table.setHorizontalHeaderLabels(["Data/Hora", "Itens", "Total", "Status"])
        fake_vendas = [
            ("24/05/2025 09:12", "Brahma, Cookies", "R$ 9,90", "PAGO"),
            ("23/05/2025 14:45", "Capuccino, Cupcake", "R$ 12,70", "PENDENTE"),
        ]
        for row, (data, itens, total, status) in enumerate(fake_vendas):
            self.table.setItem(row, 0, QTableWidgetItem(data))
            self.table.setItem(row, 1, QTableWidgetItem(itens))
            self.table.setItem(row, 2, QTableWidgetItem(total))
            self.table.setItem(row, 3, QTableWidgetItem(status))
        layout.addWidget(self.table)
        layout.addStretch()

class EstatisticasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("Estatísticas - Em breve!")
        lbl.setFont(QFont("Montserrat", 21, QFont.Bold))
        layout.addWidget(lbl)

class ConfiguracoesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("Configurações - Em breve!")
        lbl.setFont(QFont("Montserrat", 21, QFont.Bold))
        layout.addWidget(lbl)

# ==============================
# MAIN WINDOW COM NAVEGAÇÃO LATERAL E TROCA DE TELAS
# ==============================

class PDVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDV Moderno - Sistema do Mercadinho da Gi")
        self.showFullScreen()
        self.setMinimumSize(1200, 800)
        self.setWindowFlags(Qt.Window)

        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central)

        # ----------- Sidebar -----------
        sidebar = QVBoxLayout()
        sidebar.setSpacing(0)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setAlignment(Qt.AlignTop)
        self.menu_labels = [
            ("Vender", "sell.svg"),
            ("Estoque", "products.svg"),
            ("Histórico", "history.svg"),
            ("Estatísticas", "statistics.svg"),
            ("Configurações", "settings.svg")
        ]
        base_dir = get_assets_dir()
        self.sidebar_buttons = []
        for idx, (label, icon_file) in enumerate(self.menu_labels):
            icon_path = os.path.join(base_dir, icon_file)
            btn = QToolButton()
            btn.setText(label)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(28, 28))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self.mudar_tela(i))
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
                QToolButton:checked {
                    background: #39ceab22;
                    color: #39ceab;
                }
                QToolButton:hover {
                    background: #343a40;
                    color: #80bfff;
                }
            """)
            sidebar.addWidget(btn)
            self.sidebar_buttons.append(btn)
        btn_sair = QToolButton()
        btn_sair.setText("Sair")
        btn_sair.setIcon(QIcon(os.path.join(base_dir, "logout.svg")))
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
        frame_sidebar.setStyleSheet("background: #23272f; border: none; border-radius: 0px;")
        main_layout.addWidget(frame_sidebar)

        # ----------- Central Stacked Widget -----------
        self.central_stack = QStackedWidget()
        self.telas = [
            VenderWidget(self),         # 0 - Vender
            EstoqueWidget(self),        # 1 - Estoque
            HistoricoWidget(self),      # 2 - Histórico
            EstatisticasWidget(self),   # 3 - Estatísticas
            ConfiguracoesWidget(self),  # 4 - Configurações
        ]
        for tela in self.telas:
            self.central_stack.addWidget(tela)
        main_layout.addWidget(self.central_stack, 1)
        self.mudar_tela(0)

    def mudar_tela(self, idx):
        self.central_stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.sidebar_buttons):
            btn.setChecked(i == idx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PDVWindow()
    w.showFullScreen()
    sys.exit(app.exec_())