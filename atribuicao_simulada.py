import csv
from datetime import datetime

def gerar_id(nome_ficheiro, campo):
    try:
        with open(nome_ficheiro, newline='', encoding='utf-8') as f:
            linhas = list(csv.DictReader(f))
            # Filtrar linhas vazias
            linhas_validas = [l for l in linhas if any(l.values())]
            ids = [int(l[campo]) for l in linhas_validas]
            return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        return 1

def escrever_csv(nome, linha):
    with open(nome, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(linha)

def estado_atual(idPedido):
    try:
        with open("eventos_pedido.csv", newline='', encoding='utf-8') as f:
            eventos = [
                l for l in csv.DictReader(f)
                if int(l["idPedido"]) == idPedido
            ]
            return eventos[-1]["estado"] if eventos else None
    except FileNotFoundError:
        return None

