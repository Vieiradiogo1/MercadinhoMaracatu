from MercadinhoMaracatu.models.produtos import Produto

class ProdutoController:
    @staticmethod
    def salvar_produto(nome, preco, codigo, estoque):
        produto = Produto(nome=nome, preco=preco, codigo=codigo, estoque=estoque)
        produto.salvar_no_banco()
        return "Produto salvo com sucesso!"