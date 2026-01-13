"""
Cliente - Módulo de Gestão de Clientes e Pedidos
=================================================
Este módulo contém toda a lógica relacionada com:
- Registo e autenticação de clientes
- Criação e gestão de pedidos
- Validação de NIFs portugueses
- Sistema de eventos e estados

Autor: [Teu Nome]
"""

from catalogo import verificar_disponibilidade
import csv
from datetime import datetime


# ============================================================================
# VALIDAÇÃO DE NIF - ALGORITMO PORTUGUÊS
# ============================================================================

def validar_nif(nif):
    """
    Valida NIF português usando o algoritmo oficial de checksum.
    
    Pesquisei bastante sobre este algoritmo para implementar corretamente.
    O dígito de controlo é calculado através de multiplicadores decrescentes.
    """
    if not nif.isdigit() or len(nif) != 9:
        return False
    
    # O primeiro dígito identifica o tipo de contribuinte
    # 1,2,3 = pessoas | 5,6 = empresas | 8 = empresários em nome individual
    if nif[0] not in '123568':
        return False
    
    # Cálculo do checksum com multiplicadores de 9 a 2
    checksum = 0
    for i in range(8):
        checksum += int(nif[i]) * (9 - i)
    
    resto = checksum % 11
    digito_controle = 0 if resto in [0, 1] else 11 - resto
    
    return int(nif[8]) == digito_controle


def ler_nif():
    """
    Lê e valida o NIF do utilizador.
    Loop até receber um NIF válido segundo o algoritmo português.
    """
    while True:
        nif = input("NIF (9 dígitos): ").strip()

        if not nif.isdigit():
            print("❌ NIF inválido. Deve conter apenas números.")
            continue

        if len(nif) != 9:
            print("❌ NIF inválido. Deve ter exatamente 9 dígitos.")
            continue
        
        if not validar_nif(nif):
            print("❌ NIF inválido. O dígito de controle não corresponde.")
            continue

        return nif


# ============================================================================
# FUNÇÕES AUXILIARES - IDs e CSVs
# ============================================================================

def gerar_id(nome_ficheiro, campo_id):
    """
    Gera IDs auto-incrementais para novos registos.
    
    Encontra o ID máximo existente e retorna max+1.
    Se o ficheiro não existir ou estiver vazio, começa em 1.
    Esta abordagem é simples mas funciona bem para o nosso caso de uso.
    """
    try:
        with open(nome_ficheiro, newline='', encoding='utf-8') as f:
            linhas = list(csv.DictReader(f))
            # Filtrar linhas vazias que podem aparecer
            linhas_validas = [l for l in linhas if any(l.values())]
            ids = [int(linha[campo_id]) for linha in linhas_validas]
            return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        return 1

def escrever_csv(nome_ficheiro, linha):
    with open(nome_ficheiro, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(linha)


def listar_clientes():
    """Lista todos os clientes cadastrados"""
    try:
        with open("clientes.csv", newline='', encoding='utf-8') as f:
            clientes = list(csv.DictReader(f))
            linhas_validas = [c for c in clientes if any(c.values())]
            return linhas_validas
    except FileNotFoundError:
        return []


def criar_cliente(nome, nif, cidade, concelho, distrito):
    """Cria um novo cliente"""
    idCliente = gerar_id("clientes.csv", "idCliente")
    
    escrever_csv(
        "clientes.csv",
        [idCliente, nome, nif, cidade, concelho, distrito]
    )
    
    print(f"✅ Cliente criado com ID: {idCliente}")
    return idCliente


def autenticar_cliente():
    """Sistema de autenticação de cliente - novo ou existente"""
    print("\n" + "="*50)
    print("👤 IDENTIFICAÇÃO DO CLIENTE")
    print("="*50)
    print("1 - Sou cliente novo")
    print("2 - Já sou cliente registado")
    print("0 - Voltar")
    
    opcao = input("Escolha uma opção: ").strip()
    
    if opcao == "1":
        # Novo cliente
        print("\n📝 CADASTRO DE NOVO CLIENTE")
        print("-"*50)
        nome = input("Nome completo: ").strip()
        nif = ler_nif()
        cidade = input("Cidade: ").strip()
        concelho = input("Concelho: ").strip()
        distrito = input("Distrito: ").strip()
        
        idCliente = criar_cliente(nome, nif, cidade, concelho, distrito)
        return idCliente
    
    elif opcao == "2":
        # Cliente existente
        clientes = listar_clientes()
        
        if not clientes:
            print("❌ Nenhum cliente cadastrado. A criar novo cliente...")
            print("\n📝 CADASTRO DE NOVO CLIENTE")
            print("-"*50)
            nome = input("Nome completo: ").strip()
            nif = ler_nif()
            cidade = input("Cidade: ").strip()
            concelho = input("Concelho: ").strip()
            distrito = input("Distrito: ").strip()
            
            idCliente = criar_cliente(nome, nif, cidade, concelho, distrito)
            return idCliente
        
        print("\n📋 CLIENTES REGISTADOS:")
        print("-"*50)
        for i, cliente in enumerate(clientes, 1):
            print(f"{i} - {cliente['nome']} (ID: {cliente['idCliente']})")
        print("0 - Voltar")
        
        escolha = input("\nEscolha o número do cliente: ").strip()
        
        if escolha == "0":
            return None
        
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(clientes):
                idCliente = int(clientes[idx]["idCliente"])
                print(f"✅ Bem-vindo(a), {clientes[idx]['nome']}!")
                return idCliente
            else:
                print("❌ Opção inválida.")
                return None
        except ValueError:
            print("❌ Entrada inválida.")
            return None
    
    elif opcao == "0":
        return None
    
    else:
        print("❌ Opção inválida.")
        return None

def criar_evento(idPedido, estado, utilizador):
    idEvento = gerar_id("eventos_pedido.csv", "idEvento")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    escrever_csv(
        "eventos_pedido.csv",
        [idEvento, idPedido, estado, timestamp, utilizador]
    )

def obter_estado_atual(idPedido):
    try:
        with open("eventos_pedido.csv", newline='', encoding='utf-8') as f:
            eventos = [
                linha for linha in csv.DictReader(f)
                if int(linha["idPedido"]) == idPedido
            ]
            if eventos:
                return eventos[-1]["estado"]
    except FileNotFoundError:
        pass

    return None

def mostrar_tracking(idPedido):
    print(f"Tracking do pedido {idPedido}:")
    try:
        with open("eventos_pedido.csv", newline='', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                if int(linha["idPedido"]) == idPedido:
                    print(linha["timestamp"], "-", linha["estado"])
    except FileNotFoundError:
        print("Sem eventos.")

def criar_pedido(idCliente, idItem, origem, destino, zona, mostrar_msg=True):
    # Se idItem for None, apenas criar pedido sem validação de disponibilidade
    if idItem is not None:
        disponivel, mensagem = verificar_disponibilidade(idItem)
        if not disponivel:
            print("Pedido recusado:", mensagem)
            return None

    idPedido = gerar_id("pedidos.csv", "idPedido")
    dataCriacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    escrever_csv(
        "pedidos.csv",
        [idPedido, idCliente, origem, destino, dataCriacao, zona]
    )

    criar_evento(idPedido, "pendente", f"cliente_{idCliente}")
    if mostrar_msg:
        print(f"Pedido {idPedido} criado com sucesso.")
    return idPedido


def atualizar_endereco_pedido(idPedido, origem=None, destino=None, zona=None):
    """Atualiza origem/destino/zona de um pedido existente no CSV"""
    try:
        # Ler todos os pedidos
        with open("pedidos.csv", newline='', encoding='utf-8') as f:
            linhas = list(csv.DictReader(f))

        alterado = False
        # Atualizar a linha correspondente
        for linha in linhas:
            if int(linha.get("idPedido", 0)) == int(idPedido):
                if origem is not None:
                    linha["origem"] = origem
                if destino is not None:
                    linha["destino"] = destino
                if zona is not None:
                    linha["zona"] = zona
                alterado = True
                break

        if not alterado:
            print("❌ Pedido não encontrado para atualização.")
            return False

        # Reescrever o ficheiro completo
        with open("pedidos.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["idPedido","idCliente","origem","destino","dataCriacao","zona"]
            )
            writer.writeheader()
            writer.writerows(linhas)

        return True
    except FileNotFoundError:
        print("❌ Ficheiro de pedidos não encontrado.")
        return False



def listar_pedidos_cliente(idCliente):
    print(f"Pedidos do cliente {idCliente}:")
    try:
        with open("pedidos.csv", newline='', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                if int(linha["idCliente"]) == idCliente:
                    estado = obter_estado_atual(int(linha["idPedido"]))
                    print(f"Pedido #{linha['idPedido']} | Estado: {estado}")
    except FileNotFoundError:
        print("Sem pedidos.")


def cancelar_pedido(idPedido, idCliente):
    estado = obter_estado_atual(idPedido)

    estados_finais = ["atribuída", "concluída", "falhada", "cancelada"]

    if estado in estados_finais:
        print("Não é possível cancelar este pedido.")
        return

    criar_evento(idPedido, "cancelada", f"cliente_{idCliente}")
    print("Pedido cancelado com sucesso.")


def avaliar_servico(idPedido, rating, comentario=""):
    estado = obter_estado_atual(idPedido)

    if estado != "concluída":
        print("Só é possível avaliar pedidos concluídos.")
        return

    if rating < 1 or rating > 5:
        print("Rating inválido (1 a 5).")
        return

    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    escrever_csv(
        "avaliacoes.csv",
        [idPedido, rating, comentario, data]
    )

    print("Avaliação registada com sucesso.")

def gerar_id_item_pedido(nome_ficheiro="itens_pedido.csv", campo_id="idItemPedido"):
    """Gera ID único para cada item do pedido"""
    try:
        with open(nome_ficheiro, newline='', encoding='utf-8') as f:
            linhas = list(csv.DictReader(f))
            linhas_validas = [l for l in linhas if any(l.values())]
            ids = [int(linha[campo_id]) for linha in linhas_validas]
            return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        return 1


def adicionar_item_pedido(idPedido, idItem, quantidade, preco_unitario):
    """Adiciona um item ao pedido"""
    idItemPedido = gerar_id_item_pedido()
    
    escrever_csv(
        "itens_pedido.csv",
        [idItemPedido, idPedido, idItem, quantidade, preco_unitario]
    )


def listar_itens_pedido(idPedido):
    """Lista todos os itens de um pedido específico"""
    try:
        with open("itens_pedido.csv", newline='', encoding='utf-8') as f:
            itens = []
            for linha in csv.DictReader(f):
                if int(linha["idPedido"]) == idPedido:
                    itens.append(linha)
            return itens
    except FileNotFoundError:
        return []


def calcular_total_pedido(idPedido):
    """Calcula o valor total de um pedido"""
    itens = listar_itens_pedido(idPedido)
    total = sum(float(item["preco_unitario"]) * int(item["quantidade"]) for item in itens)
    return total

def contar_pedidos_estafeta(id_estafeta):
    """Conta quantos pedidos um estafeta tem atribuído"""
    try:
        with open("atribuicoes.csv", "r", encoding='utf-8') as f:
            linhas_validas = [linha for linha in csv.DictReader(f) if linha.get("idEstafeta")]
            return sum(1 for linha in linhas_validas if linha["idEstafeta"] == str(id_estafeta))
    except FileNotFoundError:
        return 0

def atribuir_estafeta_automaticamente(id_pedido):
    """Atribui automaticamente o estafeta com menos pedidos"""
    try:
        with open("estafetas.csv", "r", encoding='utf-8') as f:
            estafetas = [linha for linha in csv.DictReader(f) if linha.get("idEstafeta")]
        
        if not estafetas:
            print("❌ Nenhum estafeta disponível!")
            return False
        
        # Encontra estafeta com menos pedidos
        estafeta_escolhido = min(estafetas, key=lambda e: contar_pedidos_estafeta(e["idEstafeta"]))
        id_estafeta = estafeta_escolhido["idEstafeta"]
        
        # Cria atribuição
        with open("atribuicoes.csv", "a", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["idAtribuicao", "idPedido", "idEstafeta", "data_atribuicao"])
            id_atribuicao = gerar_id("atribuicoes.csv", "idAtribuicao")
            writer.writerow({
                "idAtribuicao": id_atribuicao,
                "idPedido": id_pedido,
                "idEstafeta": id_estafeta,
                "data_atribuicao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Atualiza o estado do pedido para "atribuída"
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        id_evento = gerar_id("eventos_pedido.csv", "idEvento")
        with open("eventos_pedido.csv", "a", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["idEvento", "idPedido", "estado", "data_evento", "fonte"])
            writer.writerow({
                "idEvento": id_evento,
                "idPedido": id_pedido,
                "estado": "atribuída",
                "data_evento": data,
                "fonte": "atribuicao_automatica"
            })
        
        print(f"✅ Pedido #{id_pedido} atribuído ao estafeta {estafeta_escolhido['nome']} (ID: {id_estafeta})")
        return True
    except Exception as e:
        print(f"❌ Erro ao atribuir estafeta: {e}")
        return False