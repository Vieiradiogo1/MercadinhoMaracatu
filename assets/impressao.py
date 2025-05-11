from escpos.printer import Usb

def configurar_impressora():
    # Substituir pelos IDs corretos da sua impressora
    return Usb(0x04b8, 0x0202, timeout=0)

def imprimir_recibo_real(itens, total):
    try:
        # Configura a impressora
        impressora = configurar_impressora()

        # Cabeçalho do recibo
        impressora.set(align='center', font='a', width=2, height=2)
        impressora.text("----- RECIBO -----\n")
        impressora.set(align='left', font='a', width=1, height=1)

        # Itens vendidos
        for item, qtd, preco in itens:
            impressora.text(f"{qtd}x {item} - R${preco:.2f}\n")
        # Total
        impressora.text("------------------\n")
        impressora.text(f"TOTAL: R${total:.2f}\n")
        impressora.text("------------------\n")

        # Finalizando a impressão
        impressora.cut() # Corta o papel
        print("Recibo impresso com sucesso!")
    except Exception as e:
        print(f"Erro ao imprimir recibo: {e}")



if __name__ == "__main__":
    itens_vendidos = [("Arroz", 2, 20.50), ("Feijão", 1, 10.00)]
    total = sum(qtd * preco for _, qtd, preco in itens_vendidos)
    imprimir_recibo_real(itens_vendidos, total)