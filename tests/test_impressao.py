import sys
import os

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from impressao import imprimir_recibo

def criar_recibo_personalizado():
    mensagem = [
        ""
        "======ALERTA!!!!!!!!!!!"
        "=========================",
        "      RECIBO OFICIAL     ",
        "=========================",
        "o Edson é gado!",
        "Tem que trabaia em SP",
        "E largar da Salém porque",
        "ela é feia.",
        "=========================",
        "    FIM DA MENSAGEM      ",
        "========================="
    ]

    # Repetimos as linhas para garantir que o recibo tenha cerca de 10 cm
    # Cada linha aqui é uma simulação de espaço físico em papel
    linhas_replicadas = mensagem * 5  # Ajustar o fator para alcançar o tamanho desejado

    total = "Recibo gerado com sucesso!"  # Informação para o rodapé
    return linhas_replicadas, total

if __name__ == "__main__":
    # Criar recibo personalizado
    itens, total = criar_recibo_personalizado()

    # Imprimir recibo
    imprimir_recibo(itens, total)