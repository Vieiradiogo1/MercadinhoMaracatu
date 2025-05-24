import usb.core
import usb.util

# IDs da impressora (substitua pelos valores corretos)
VID = 0x20d1  # Vendor ID
PID = 0x7008  # Product ID

def configurar_impressora():
    """Configura e retorna o dispositivo USB."""
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        raise ValueError("Impressora não encontrada")
    try:
        dev.set_configuration()
    except usb.core.USBError as e:
        raise RuntimeError(f"Erro ao configurar o dispositivo: {e}")
    return dev

def enviar_comando(dev, comando):
    """Envia comandos ESC/POS para a impressora."""
    try:
        dev.write(0x02, comando)  # Endpoint OUT (verifique se é 0x02 para o seu dispositivo)
    except usb.core.USBError as e:
        raise RuntimeError(f"Erro ao enviar dados para a impressora: {e}")

def buscar_vendas():
    """
    Simula a busca de vendas cadastradas.
    Substitua isso com a lógica de acesso ao banco de dados ou arquivo.
    """
    vendas = [
        {"nome": "Arroz", "quantidade": 2, "preco": 20.50},
        {"nome": "Feijão", "quantidade": 1, "preco": 10.00},
        {"nome": "Macarrão", "quantidade": 3, "preco": 5.75}
    ]
    return vendas

def formatar_vendas(vendas):
    """
    Formata as vendas para impressão.
    """
    total = sum(venda["quantidade"] * venda["preco"] for venda in vendas)
    return vendas, total

def imprimir_recibo(itens, total):
    """
    Formata e imprime um recibo.

    :param itens: Lista de itens no formato [(nome, qtd, preco)]
    :param total: Total geral da venda
    """
    try:
        # Configurar a impressora
        dev = configurar_impressora()

        # Comandos ESC/POS
        comando_inicial = b'\x1b\x40'  # Reset da impressora
        enviar_comando(dev, comando_inicial)

        # Cabeçalho
        cabecalho = "MERCADINHO MARACATU\n"
        cabecalho += "---------------------------\n"
        enviar_comando(dev, cabecalho.encode("utf-8"))

        # Itens vendidos
        for item in itens:
            linha = f"{item['nome']:<20} {item['quantidade']} x {item['preco']:.2f}\n"
            enviar_comando(dev, linha.encode("utf-8"))

        # Total
        total_texto = f"\nTOTAL: R$ {total:.2f}\n"
        enviar_comando(dev, total_texto.encode("utf-8"))

        # Finalização
        enviar_comando(dev, "\nObrigado pela preferência!\n".encode("utf-8"))
        enviar_comando(dev, b'\x1d\x56\x01')  # Comando para corte de papel

        print("Impressão enviada com sucesso")
    except Exception as e:
        print(f"Erro ao imprimir recibo: {e}")