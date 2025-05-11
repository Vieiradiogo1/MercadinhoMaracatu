import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database
from models.produtos import Produto
from models.vendas import Venda

def testar_banco_de_dados():
    print("=== Testando Banco de Dados ===")
    db = Database()
    db.criar_tabelas()
    print("Tabelas criadas com sucesso!\n")

def testar_produto():
    print("=== Testando Produto ===")
    # Criar um novo produto
    produto = Produto(nome="Cerveja", preco=4.50, codigo="123456", estoque=100)
    produto.salvar()
    print(f"Produto cadastrado: {produto.nome}, ID: {produto.id}")

    # Atualizar o produto
    produto.nome = "Cerveja Premium"
    produto.preco = 5.00
    produto.salvar()
    print(f"Produto atualizado: {produto.nome}, Preço: {produto.preco}")

    # Listar todos os produtos
    produtos = Produto.buscar_todos()
    print("Produtos cadastrados:")
    for p in produtos:
        print(f"- {p.nome} (ID: {p.id}, Preço: {p.preco}, Estoque: {p.estoque})")

    # Deletar o produto
    produto.deletar()
    print(f"Produto deletado: {produto.nome}\n")

def testar_venda():
    print("=== Testando Venda ===")
    
    # Criar um novo produto para testar a venda
    produto = Produto(nome="Suco Natural", preco=6.00, codigo="999999", estoque=30)
    produto.salvar()
    print(f"Produto para venda cadastrado: {produto.nome}, Estoque: {produto.estoque}")

    # Registrar uma venda
    venda = Venda(produto_id=produto.id, quantidade=5)
    venda.registrar()
    print(f"Venda registrada: Produto ID {venda.produto_id}, Quantidade: {venda.quantidade}, Total: {venda.total}")

    # Verificar o estoque atualizado
    produto_atualizado = Produto.buscar_por_id(produto.id)
    print(f"Estoque após venda: {produto_atualizado.estoque}")

    # Listar todas as vendas
    vendas = Venda.listar_todas()
    print("Vendas registradas:")
    for v in vendas:
        print(f"- Venda ID: {v.id}, Produto ID: {v.produto_id}, Quantidade: {v.quantidade}, Total: {v.total}, Data: {v.data_venda}")

        
if __name__ == "__main__":
    # Executar os testes
    testar_banco_de_dados()
    testar_produto()
    testar_venda()