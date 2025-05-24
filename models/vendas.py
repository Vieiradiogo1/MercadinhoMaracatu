from MercadinhoMaracatu.models.database import Database
from MercadinhoMaracatu.models.produtos import Produto

class Venda:
    def __init__(self, produto_id, quantidade, total=None, data_venda=None, id=None):
        """
        Representa uma venda.
        :param produto_id: ID do produto vendido
        :param quantidade: Quantidade vendida
        :param total: Valor total da venda (calculado automaticamente se não fornecido)
        :param data_venda: Data e hora da venda (opcional, preenchida automaticamente pelo banco)
        :param id: ID da venda (opcional, usado para vendas já existentes)
        """
        self.id = id
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.total = total
        self.data_venda = data_venda

    def registrar(self):
        """
        Registra uma nova venda no banco de dados e atualiza o estoque do produto.
        """
        # Verificar se o produto existe e tem estoque suficiente
        produto = Produto.buscar_por_id(self.produto_id)
        if not produto:
            raise ValueError("Produto não encontrado.")
        if produto.estoque < self.quantidade:
            raise ValueError("Estoque insuficiente para realizar a venda.")

        # Calcular o total da venda
        self.total = produto.preco * self.quantidade

        # Registrar a venda no banco de dados
        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()

            # Inserir a venda
            cursor.execute('''
                INSERT INTO vendas (produto_id, quantidade, total)
                VALUES (?, ?, ?)
            ''', (self.produto_id, self.quantidade, self.total))
            self.id = cursor.lastrowid

            # Atualizar o estoque do produto diretamente no banco
            cursor.execute('''
                UPDATE produtos
                SET estoque = estoque - ?
                WHERE id = ?
            ''', (self.quantidade, self.produto_id))

            # Confirmar as alterações
            conexao.commit()
        finally:
            conexao.close()

    @staticmethod
    def buscar_por_id(venda_id):
        """
        Busca uma venda pelo ID.
        :param venda_id: ID da venda
        :return: Instância de Venda ou None
        """
        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM vendas WHERE id = ?', (venda_id,))
            resultado = cursor.fetchone()
        finally:
            conexao.close()

        if resultado:
            return Venda(
                id=resultado[0],
                produto_id=resultado[1],
                quantidade=resultado[2],
                total=resultado[3],
                data_venda=resultado[4]  # Incluindo a data da venda
            )
        return None

    @staticmethod
    def listar_todas():
        """
        Lista todas as vendas registradas no banco de dados.
        :return: Lista de instâncias de Venda
        """
        db = Database()
        conexao = db.conectar()
        try:
            cursor = conexao.cursor()
            cursor.execute('SELECT * FROM vendas')
            resultados = cursor.fetchall()
        finally:
            conexao.close()

        vendas = []
        for resultado in resultados:
            vendas.append(Venda(
                id=resultado[0],
                produto_id=resultado[1],
                quantidade=resultado[2],
                total=resultado[3],
                data_venda=resultado[4]  # Incluindo a data da venda
            ))
        return vendas