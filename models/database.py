import sqlite3

class Database:
    def __init__(self, db_file="mercadinho.db"):
        """
        Inicializa a classe Database com o caminho do arquivo do banco de dados.
        :param db_file: Nome do arquivo do banco de dados SQLite.
        """
        self.db_file = db_file

    def conectar(self):
        """
        Estabelece e retorna uma conexão com o banco de dados.
        :return: Conexão SQLite.
        """
        return sqlite3.connect(self.db_file)

    def criar_tabelas(self):
        """
        Cria as tabelas necessárias no banco de dados.
        """
        conexao = self.conectar()
        try:
            cursor = conexao.cursor()

            # Ativar o modo WAL
            cursor.execute('PRAGMA journal_mode=WAL')

            # Criar tabela de produtos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    preco REAL NOT NULL,
                    codigo TEXT UNIQUE NOT NULL,
                    estoque INTEGER NOT NULL
                )
            ''')

            # Criar tabela de vendas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    quantidade INTEGER NOT NULL,
                    total REAL NOT NULL,
                    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (produto_id) REFERENCES produtos (id)
                )
            ''')

            # Confirmar alterações
            conexao.commit()
        finally:
            # Garantir que a conexão seja fechada
            conexao.close()

# Exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.criar_tabelas()
    print("Tabelas criadas com sucesso!")