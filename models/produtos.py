from MercadinhoMaracatu.models.database import Database

class Produto:
    def __init__(self, id=None, nome=None, preco=None, codigo=None, estoque=None):
        """
        Classe que representa um produto.
        :param id: ID do produto (opcional, usado para produtos já existentes)
        :param nome: Nome do produto
        :param preco: Preço do produto
        :param codigo: Código do produto
        :param estoque: Quantidade em estoque
        """
        self.id = id
        self.nome = nome
        self.preco = preco
        self.codigo = codigo
        self.estoque = estoque

    def salvar(self):
        """
        Salva o produto no banco de dados. Se já existir, atualiza.
        """
        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()

            # Verificar se o código já existe no banco de dados
            cursor.execute("SELECT id FROM produtos WHERE codigo = ?", (self.codigo,))
            resultado = cursor.fetchone()

            # Se o código já existir e não for o mesmo produto, lança um erro
            if resultado and (self.id is None or self.id != resultado[0]):
                raise ValueError(f"Já existe um produto com o código '{self.codigo}'.")

            if self.id is None:
                # Inserir novo produto
                cursor.execute('''
                    INSERT INTO produtos (nome, preco, codigo, estoque)
                    VALUES (?, ?, ?, ?)
                ''', (self.nome, self.preco, self.codigo, self.estoque))
                self.id = cursor.lastrowid
            else:
                # Atualizar produto existente
                cursor.execute('''
                    UPDATE produtos
                    SET nome = ?, preco = ?, codigo = ?, estoque = ?
                    WHERE id = ?
                ''', (self.nome, self.preco, self.codigo, self.estoque, self.id))

            # Confirmar as alterações
            conexao.commit()
        finally:
            conexao.close()

    @staticmethod
    def buscar_todos():
        """
        Retorna todos os produtos cadastrados no banco de dados.
        :return: Lista de instâncias de Produto.
        """
        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM produtos')
            resultados = cursor.fetchall()
        finally:
            conexao.close()

        produtos = []
        for resultado in resultados:
            produtos.append(Produto(
                id=resultado[0],
                nome=resultado[1],
                preco=resultado[2],
                codigo=resultado[3],
                estoque=resultado[4]
            ))
        return produtos

    @staticmethod
    def buscar_por_id(produto_id):
        """
        Busca um produto pelo ID.
        :param produto_id: ID do produto
        :return: Instância de Produto ou None
        """
        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,))
            resultado = cursor.fetchone()
        finally:
            conexao.close()

        if resultado:
            return Produto(
                id=resultado[0],
                nome=resultado[1],
                preco=resultado[2],
                codigo=resultado[3],
                estoque=resultado[4]
            )
        return None

    def deletar(self):
        """
        Deleta o produto do banco de dados.
        """
        if self.id is None:
            raise ValueError("Produto não está salvo no banco de dados.")

        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()
            cursor.execute('DELETE FROM produtos WHERE id = ?', (self.id,))
            conexao.commit()
        finally:
            conexao.close()