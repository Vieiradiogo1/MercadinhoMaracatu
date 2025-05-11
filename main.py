from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label  # Use o Label do Kivy
from models.produtos import Produto
from models.vendas import Venda
from kivy.lang import Builder
from kivy.lang import Builder
Builder.load_file('mercadinho.kv')

# Telas da aplicação
class MenuScreen(Screen):
    pass

class ProdutosScreen(Screen):
    def on_enter(self):
        """Carregado automaticamente ao entrar na tela."""
        self.listar_produtos()

    def listar_produtos(self):
        """Busca os produtos do banco de dados e os exibe na interface."""
        produtos = Produto.buscar_todos()  # Método que retorna uma lista de produtos
        lista_layout = self.ids.produtos_lista
        lista_layout.clear_widgets()  # Limpar widgets antigos

        if not produtos:
            lista_layout.add_widget(Label(text="Nenhum produto cadastrado."))
        else:
            for p in produtos:
                lista_layout.add_widget(
                    Label(text=f"{p.nome} - Preço: R${p.preco} - Estoque: {p.estoque}")
                )

class VendasScreen(Screen):
    pass

# Tela de cadastro de produtos
class CadastroProdutoScreen(Screen):
    def salvar_produto(self):
        nome = self.ids.nome_input.text
        preco = self.ids.preco_input.text
        estoque = self.ids.estoque_input.text

        if not nome or not preco or not estoque:
            print("Por favor, preencha todos os campos.")
            return

        # Salvar produto no banco de dados
        produto = Produto(nome=nome, preco=float(preco), codigo=f"{nome[:3]}-{estoque}", estoque=int(estoque))
        produto.salvar()

        # Limpar os campos e voltar para a tela de produtos
        self.ids.nome_input.text = ""
        self.ids.preco_input.text = ""
        self.ids.estoque_input.text = ""
        app = App.get_running_app()
        app.root.current = 'produtos'

# Tela principal da aplicação
class MercadinhoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(ProdutosScreen(name='produtos'))
        sm.add_widget(VendasScreen(name='vendas'))
        sm.add_widget(CadastroProdutoScreen(name='cadastro'))
        sm.current = 'menu'  # Define a tela inicial como "menu"
        return sm

if __name__ == '__main__':
    MercadinhoApp().run()