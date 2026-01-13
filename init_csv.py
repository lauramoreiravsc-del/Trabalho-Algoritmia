import csv
import os

def criar_csv(nome, cabecalho):
    if not os.path.exists(nome):
        with open(nome, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cabecalho)
        print("criado:", nome)
    else:
        print("já existe:", nome)

criar_csv("pedidos.csv", ["idPedido","idCliente","origem","destino","dataCriacao","zona"])
criar_csv("eventos_pedido.csv", ["idEvento","idPedido","estado","timestamp","utilizador"])
criar_csv("avaliacoes.csv", ["idPedido","rating","comentario","data"])
criar_csv("clientes.csv", ["idCliente","nome","nif","cidade","concelho","distrito"])
criar_csv("catalogo.csv", ["idItem","tipo","nome","descricao","categoria","preco","duracaoPadraoMin","stock","ativo"])
criar_csv("atribuicoes.csv",["idAtribuicao", "idPedido", "idEstafeta", "dataAtribuicao"])
criar_csv("estafetas.csv",["idEstafeta", "nome", "zona", "turno", "ativo"])
criar_csv("anomalias.csv",["idPedido", "idEstafeta", "motivo", "descricao", "timestamp"])
criar_csv("mensagens.csv",["idMensagem", "idPedido", "texto", "timestamp"])