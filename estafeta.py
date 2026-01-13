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


def listar_pedidos_pendentes():
    """Lista todos os pedidos que ainda estão pendentes (não atribuídos)"""
    try:
        pedidos = []
        with open("pedidos.csv", newline='', encoding='utf-8') as f:
            for pedido in csv.DictReader(f):
                if not pedido or not pedido.get("idPedido"):
                    continue
                idPedido = int(pedido["idPedido"])
                
                # Verificar o estado atual do pedido
                with open("eventos_pedido.csv", newline='', encoding='utf-8') as f2:
                    eventos = list(csv.DictReader(f2))
                    eventos_validos = [e for e in eventos if any(e.values())]
                    eventos_pedido = [e for e in eventos_validos if int(e["idPedido"]) == idPedido]
                    
                    if eventos_pedido:
                        estado_atual = eventos_pedido[-1]["estado"]
                        if estado_atual == "pendente":
                            pedidos.append(pedido)
        
        return pedidos
    except FileNotFoundError:
        return []


def listar_estafetas():
    """Lista todos os estafetas cadastrados"""
    try:
        with open("estafetas.csv", newline='', encoding='utf-8') as f:
            estafetas = list(csv.DictReader(f))
            estafetas_validas = [e for e in estafetas if any(e.values())]
            return estafetas_validas
    except FileNotFoundError:
        return []


def criar_estafeta(nome, zona, turno):
    """Cria um novo estafeta"""
    idEstafeta = gerar_id("estafetas.csv", "idEstafeta")
    
    escrever_csv(
        "estafetas.csv",
        [idEstafeta, nome, zona, turno, "true"]
    )
    
    print(f"✅ Estafeta criado com ID: {idEstafeta}")
    return idEstafeta


def selecionar_pedido():
    """Interface para selecionar um pedido"""
    pedidos = listar_pedidos_pendentes()
    
    if not pedidos:
        print("❌ Nenhum pedido pendente para atribuir.")
        return None
    
    print("\n📋 PEDIDOS PENDENTES:")
    print("-"*60)
    for i, pedido in enumerate(pedidos, 1):
        print(f"{i} - Pedido #{pedido['idPedido']} | Cliente: {pedido['idCliente']} | {pedido['origem']} → {pedido['destino']}")
    print("0 - Voltar")
    
    escolha = input("\nEscolha o número do pedido: ").strip()
    
    if escolha == "0":
        return None
    
    try:
        idx = int(escolha) - 1
        if 0 <= idx < len(pedidos):
            return int(pedidos[idx]["idPedido"])
        else:
            print("❌ Opção inválida.")
            return None
    except ValueError:
        print("❌ Entrada inválida.")
        return None


def selecionar_estafeta():
    """Interface para selecionar um estafeta"""
    estafetas = listar_estafetas()
    
    if not estafetas:
        print("\n❌ Nenhum estafeta cadastrado. Não é possível atribuir pedidos.")
        return None
    
    print("\n👨‍💼 ESTAFETAS DISPONÍVEIS:")
    print("-"*60)
    for i, estafeta in enumerate(estafetas, 1):
        print(f"{i} - {estafeta['nome']} (ID: {estafeta['idEstafeta']}) | Zona: {estafeta['zona']} | Turno: {estafeta['turno']}")
    print("0 - Voltar")
    
    escolha = input("\nEscolha o número do estafeta: ").strip()
    
    if escolha == "0":
        return None
    
    try:
        idx = int(escolha) - 1
        if 0 <= idx < len(estafetas):
            return int(estafetas[idx]["idEstafeta"])
        else:
            print("❌ Opção inválida.")
            return None
    except ValueError:
        print("❌ Entrada inválida.")
        return None


def criar_evento(idPedido, estado, utilizador, localizacao=""):
    idEvento = gerar_id("eventos_pedido.csv", "idEvento")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    escrever_csv(
        "eventos_pedido.csv",
        [idEvento, idPedido, estado, timestamp, utilizador]
    )


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

def listar_tarefas(idEstafeta):
    print(f"Tarefas do estafeta {idEstafeta}:")
    try:
        with open("atribuicoes.csv", newline='', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                if int(linha["idEstafeta"]) == idEstafeta:
                    estado = estado_atual(int(linha["idPedido"]))
                    print(
                        f"Pedido {linha['idPedido']} | "
                        f"Estado: {estado}"
                    )
    except FileNotFoundError:
        print("Sem atribuições.")

def aceitar_atribuicao(idPedido, idEstafeta):
    estado = estado_atual(idPedido)

    if estado != "atribuída":
        print(f"❌ Aceitação não permitida. Estado atual: '{estado}' (esperado: 'atribuída').")
        return

    criar_evento(idPedido, "em_recolha", f"estafeta_{idEstafeta}")
    print("✅ Pedido aceite. Em recolha.")


def recusar_atribuicao(idPedido, idEstafeta, motivo):
    if estado_atual(idPedido) != "atribuída":
        print("Não é possível recusar.")
        return

    criar_evento(idPedido, "aprovada", f"estafeta_{idEstafeta}")

    escrever_csv(
        "mensagens.csv",
        [
            gerar_id("mensagens.csv", "idMensagem"),
            idPedido,
            f"Pedido não aceite: {motivo}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
    )

    print("Pedido não aceite.")

def atualizar_estado(idPedido, idEstafeta, novo_estado, localizacao=""):
    estado = estado_atual(idPedido)

    estados_finais = ["concluída", "falhada", "cancelada"]

    if estado in estados_finais:
        print("Pedido em estado final. Não pode ser alterado.")
        return

    # Permite qualquer transição para estados válidos
    estados_validos = ["em_recolha", "em_distribuicao", "concluída", "falhada", "cancelada"]
    
    if novo_estado not in estados_validos:
        print("Estado inválido.")
        return

    criar_evento(idPedido, novo_estado, f"estafeta_{idEstafeta}")
    print(f"Estado atualizado para {novo_estado}.")


def reportar_anomalia(idPedido, idEstafeta, motivo, descricao):
    escrever_csv(
        "anomalias.csv",
        [
            idPedido,
            idEstafeta,
            motivo,
            descricao,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
    )

    escrever_csv(
        "mensagens.csv",
        [
            gerar_id("mensagens.csv", "idMensagem"),
            idPedido,
            f"Anomalia reportada: {motivo}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
    )

    print("Anomalia reportada.")

def metricas_estafeta(idEstafeta):
    total = 0
    sucesso = 0
    falha = 0

    try:
        with open("eventos_pedido.csv", newline='', encoding='utf-8') as f:
            for e in csv.DictReader(f):
                if f"estafeta_{idEstafeta}" == e["utilizador"]:
                    if e["estado"] == "concluída":
                        sucesso += 1
                        total += 1
                    elif e["estado"] == "falhada":
                        falha += 1
                        total += 1
    except FileNotFoundError:
        pass

    taxa = (sucesso / total * 100) if total > 0 else 0

    print("Métricas do Estafeta:")
    print("Total:", total)
    print("Concluídas:", sucesso)
    print("Falhadas:", falha)
    print("Taxa de sucesso:", round(taxa, 2), "%")
