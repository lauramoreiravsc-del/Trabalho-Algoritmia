import csv

# Lista de ficheiros CSV para limpar
ficheiros = [
    "pedidos.csv",
    "clientes.csv", 
    "itens_pedido.csv",
    "eventos_pedido.csv",
    "atribuicoes.csv",
    "mensagens.csv",
    "anomalias.csv"
]

# Cabeçalhos para cada ficheiro
cabecalhos = {
    "pedidos.csv": ["idPedido","idCliente","origem","destino","dataCriacao","zona"],
    "clientes.csv": ["idCliente","nome","nif","cidade","concelho","distrito"],
    "itens_pedido.csv": ["idItemPedido","idPedido","idItem","quantidade","preco_unitario"],
    "eventos_pedido.csv": ["idEvento","idPedido","estado","timestamp","utilizador"],
    "atribuicoes.csv": ["idAtribuicao", "idPedido", "idEstafeta", "dataAtribuicao"],
    "mensagens.csv": ["idMensagem", "idPedido", "texto", "timestamp"],
    "anomalias.csv": ["idPedido", "idEstafeta", "motivo", "descricao", "timestamp"]
}

for ficheiro in ficheiros:
    try:
        with open(ficheiro, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cabecalhos[ficheiro])
        print(f"✅ {ficheiro} limpo")
    except Exception as e:
        print(f"❌ Erro ao limpar {ficheiro}: {e}")

print("\n🎉 Todos os dados foram limpos!")
