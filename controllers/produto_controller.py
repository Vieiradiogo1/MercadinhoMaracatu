import sqlite3
import os

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'mercadinho.db')
)

class ProdutoController:
    @staticmethod
    def salvar_produto(nome, preco, codigo, estoque):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO produtos (nome, preco, codigo, estoque)
            VALUES (?, ?, ?, ?)
        """, (nome, preco, codigo, estoque))
        conn.commit()
        conn.close()
        return "Produto salvo com sucesso!"

    @staticmethod
    def listar():
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, nome, preco, codigo, estoque FROM produtos")
        produtos = []
        for row in cur.fetchall():
            produtos.append({
                "id": row[0],
                "nome": row[1],
                "preco": row[2],
                "codigo": row[3],
                "estoque": row[4]
            })
        conn.close()
        return produtos

    @staticmethod
    def buscar_por_codigo(codigo):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, nome, preco, codigo, estoque FROM produtos WHERE codigo = ?", (codigo,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "nome": row[1],
                "preco": row[2],
                "codigo": row[3],
                "estoque": row[4]
            }
        return None