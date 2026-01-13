import csv

# =================================================
# CATÁLOGO / MENU (APENAS LEITURA NO PROGRAMA)
# =================================================

def ler_catalogo():
    try:
        with open("catalogo.csv", newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []

# =================================================
# FUNÇÃO DE ADMIN (USAR SÓ MANUALMENTE, UMA VEZ)
# =================================================
# ⚠️ NÃO CHAMAR NO main.py
# ⚠️ NÃO EXECUTAR catalogo.py DURANTE O PROGRAMA

def adicionar_produto(nome, descricao, categoria, preco, stock):
    itens = ler_catalogo()

    if itens:
        ultimo_id = max(int(item["idItem"]) for item in itens)
        novo_id = ultimo_id + 1
    else:
        novo_id = 1

    with open("catalogo.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not itens:
            writer.writerow([
                "idItem", "tipo", "nome", "descricao",
                "categoria", "preco", "duracaoPadraoMin",
                "stock", "ativo"
            ])

        writer.writerow([
            novo_id,
            "produto",
            nome,
            descricao,
            categoria,
            preco,
            "",
            stock,
            "true"
        ])
