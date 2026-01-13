"""
Send2You - Sistema de Gestão de Entregas
==========================================
Ficheiro principal que contém os menus e a lógica de navegação do sistema.

Desenvolvido como projeto prático para a disciplina de Programação.
Autor: [Teu Nome]
Data: Janeiro 2026
"""

import csv
from cliente import (
    criar_pedido,
    listar_pedidos_cliente,
    atribuir_estafeta_automaticamente,
    autenticar_cliente,
    adicionar_item_pedido,
    calcular_total_pedido,
    listar_itens_pedido,
)
from estafeta import (
    listar_tarefas,
    aceitar_atribuicao,
    atualizar_estado,
    metricas_estafeta
)
from catalogo import listar_catalogo
from localizacao import (
    calcular_entrega,
    exibir_info_entrega,
    obter_coordenadas,
    RESTAURANTE_ENDERECO,
    verificar_raio_entrega,
)

# ============================================================================
# FUNÇÕES AUXILIARES DE INPUT/VALIDAÇÃO
# ============================================================================
# Estas funções garantem que os inputs do utilizador são válidos antes de
# prosseguir com a lógica do programa

def ler_int(mensagem, minimo=0):
    """
    Lê um número inteiro do utilizador com validação.
    
    Continua a pedir até receber um valor válido >= minimo.
    Usei um loop infinito com break implícito no return - pareceu-me
    a forma mais simples de garantir que só saímos com valor válido.
    """
    while True:
        try:
            valor = int(input(mensagem))
            if valor < minimo:
                print(f" Número inválido. Insira um número >= {minimo}.")
            else:
                return valor
        except ValueError:
            # Acontece quando o user escreve texto em vez de número
            print(" Entrada inválida. Insira um número inteiro.")

def ler_opcao(mensagem, opcoes):
    """
    Lê uma opção do menu, validando contra as opções permitidas.
    
    Retorna apenas quando o utilizador escolhe uma opção válida.
    A validação com 'in' é eficiente para listas pequenas como as do menu.
    """
    while True:
        opcao = input(mensagem)
        if opcao in opcoes:
            return opcao
        print(f" Opção inválida. Escolha uma das seguintes: {', '.join(opcoes)}")

def ler_morada(mensagem):
    """
    Lê e valida uma morada usando a API de geocodificação.
    
    A validação garante que:
    1. A morada não está vazia
    2. É reconhecida pelo OpenStreetMap (via Nominatim)
    
    Isto evita criar pedidos com moradas inválidas que falhariam mais tarde.
    """
    while True:
        morada = input(mensagem).strip()
        if not morada:
            print("❌ Morada inválida. Não pode estar vazia.")
            continue
        # Validação por geocodificação usando a API do Nominatim
        # Se a morada não for encontrada, coords = None
        coords = obter_coordenadas(morada)
        if not coords:
            print("❌ Morada não encontrada. Tente ser mais específico (rua, nº, cidade).")
            continue
        return morada

# NIF: A validação e leitura estão em cliente.py (evita duplicação)


# ============================================================================
# VISUALIZAÇÃO DO MENU/CATÁLOGO
# ============================================================================

def mostrar_menu():
    """
    Carrega e exibe o catálogo de produtos ativos.
    
    Filtra apenas itens com ativo='true' para não mostrar produtos
    descontinuados ou temporariamente indisponíveis.
    """
    from catalogo import ler_catalogo

    itens = ler_catalogo()

    # Filtrar apenas itens ativos
    itens_ativos = [
        item for item in itens
        if item.get("ativo", "").strip().lower() == "true"
    ]

    if not itens_ativos:
        print("📦 Menu vazio.")
        return []

    print("\n--- 🍽️ MENU DISPONÍVEL ---")

    for i, item in enumerate(itens_ativos, start=1):
        print(f"{i} - {item['nome']} ..... {item['preco']}€")

    return itens_ativos

# ============================================================================
# FUNÇÕES DE RESUMO E VISUALIZAÇÃO
# ============================================================================

# =====================
# RESUMO DO PEDIDO
# =====================

def obter_cliente_por_id(idCliente):
    try:
        with open("clientes.csv", newline='', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                if int(linha["idCliente"]) == idCliente:
                    return linha
    except FileNotFoundError:
        return None
    return None

def obter_nome_item(idItem):
    try:
        from catalogo import ler_catalogo
        itens = ler_catalogo()
        for it in itens:
            if int(it.get("idItem", 0)) == idItem:
                return it.get("nome", f"Item #{idItem}")
    except Exception:
        pass
    return f"Item #{idItem}"

def mostrar_resumo_pedido(idPedido, idCliente):
    cliente = obter_cliente_por_id(idCliente)
    if not cliente:
        print("\n❌ Não foi possível obter os dados do cliente.")
        return

    nome_cliente = cliente.get("nome", f"Cliente #{idCliente}")
    # Preferir a morada do pedido (destino) se existir
    endereco_cliente = None
    try:
        with open("pedidos.csv", newline='', encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                if int(linha.get("idPedido", 0)) == int(idPedido):
                    endereco_cliente = linha.get("destino")
                    break
    except FileNotFoundError:
        pass
    if not endereco_cliente:
        endereco_cliente = f"{cliente.get('cidade','')}, {cliente.get('concelho','')}, {cliente.get('distrito','')}, Portugal".strip(', ')

    itens = listar_itens_pedido(idPedido)
    
    print("\n" + "="*50)
    print(" RESUMO DO PEDIDO")
    print("="*50)
    print(f" Cliente: {nome_cliente} (ID: {idCliente})")
    print(f" Pedido: #{idPedido}")
    print(f" Morada de entrega: {endereco_cliente}")
    print(" Itens:")
    if not itens:
        print("  - (nenhum item)")
    else:
        for it in itens:
            nome_item = obter_nome_item(int(it["idItem"]))
            print(f"  - {nome_item} x{it['quantidade']} @ {float(it['preco_unitario']):.2f}€")

    # Estimativa de entrega
    try:
        from localizacao import calcular_entrega
        resultado = calcular_entrega(endereco_cliente)
        if resultado:
            distancia_km, tempo_min = resultado
            print(f" Distância estimada: {distancia_km:.2f} km")
            print(f" Tempo estimado: {int(tempo_min)} minutos")
        else:
            print(" ⚠️ Não foi possível calcular a estimativa de entrega.")
    except Exception as e:
        print(f" ⚠️ Erro ao calcular a entrega: {e}")
    
    total = calcular_total_pedido(idPedido)
    print(f" Total: {total:.2f}€")
    print("="*50)

def menu_cliente():
    while True:
        print("\n--- PORTAL CLIENTE ---")
        print("1 - Ver menu")
        print("2 - Criar pedido")
        print("3 - Listar meus pedidos")
        print("0 - Voltar")

        opcao = ler_opcao("Escolha uma opção: ", ["1", "2", "3", "0"])

        if opcao == "1":
            mostrar_menu()
            input("\nPrima ENTER para continuar...")

        elif opcao == "2":
            # Identificação do cliente (novo ou existente)
            idCliente = autenticar_cliente()
            if not idCliente:
                input("\nOperação cancelada. Prima ENTER para continuar...")
                continue

            # Morada de entrega (validada por geocodificação)
            morada = ler_morada("Morada de entrega (rua, nº, cidade): ")

            # Verificar raio de entrega antes de criar o pedido
            resultado = calcular_entrega(morada)
            if not resultado:
                print("⚠️ Não foi possível calcular a rota para a morada indicada.")
                input("\nPrima ENTER para voltar ao início...")
                continue
            distancia_km, tempo_min = resultado
            permitido, _msg = verificar_raio_entrega(distancia_km)
            if not permitido:
                print("❌ Morada não abrangida por nossos estafetas")
                input("\nPrima ENTER para voltar ao início...")
                continue

            # Cria o pedido (cabeçalho) já com origem/destino
            origem_str = RESTAURANTE_ENDERECO if RESTAURANTE_ENDERECO else "Restaurante Send2You"
            idPedido = criar_pedido(
                idCliente,
                None,
                origem_str,
                morada,
                None,
                mostrar_msg=False,
            )

            # Seleção de múltiplos itens
            while True:
                itens = mostrar_menu()
                if not itens:
                    print("\n⚠️ Menu vazio. Não é possível adicionar itens.")
                    break

                escolha = ler_int(
                    "Escolha o número do item (ou 0 para finalizar): ", minimo=0
                )

                if escolha == 0:
                    break

                if escolha > len(itens):
                    print("❌ Número inválido.")
                    continue

                item_escolhido = itens[escolha - 1]
                idItem = int(item_escolhido["idItem"])

                quantidade = ler_int("Quantidade: ", minimo=1)
                try:
                    preco_unitario = float(item_escolhido["preco"])
                except ValueError:
                    print("❌ Preço inválido no catálogo. Item não adicionado.")
                    continue

                adicionar_item_pedido(idPedido, idItem, quantidade, preco_unitario)
                print("✅ Item adicionado ao pedido.")

            total = calcular_total_pedido(idPedido)
            print(f"\n🧾 Total do pedido: {total:.2f}€")

            # Mostrar resumo do pedido (cliente, itens, estimativa)
            mostrar_resumo_pedido(idPedido, idCliente)
            input("\nPedido criado. Prima ENTER para continuar...")

        elif opcao == "3":
            idCliente = ler_int("ID Cliente: ")
            listar_pedidos_cliente(idCliente)
            input("\nPrima ENTER para continuar...")

        elif opcao == "0":
            break


def menu_atribuicao():
    """Menu para aceitar pedidos"""
    while True:
        print("\n" + "="*50)
        print(" ACEITAR PEDIDOS")
        print("="*50)
        print("1 - Aceitar pedido pendente")
        print("2 - Ver pedidos por aceitar")
        print("3 - Voltar")
        
        opcao = ler_opcao("Escolha uma opção: ", ["1", "2", "3"])
        
        if opcao == "1":
            
            try:
                from estafeta import estado_atual
                pedidos_para_atribuir = []
                
                with open("pedidos.csv", "r", encoding='utf-8') as f:
                    todos_pedidos = [linha for linha in csv.DictReader(f) if linha.get("idPedido")]
                
               
                for pedido in todos_pedidos:
                    pedido_id = int(pedido["idPedido"])
                    estado = estado_atual(pedido_id)
                    if estado in ["aprovada", "pendente"]:
                        pedidos_para_atribuir.append(pedido)
                
                if not pedidos_para_atribuir:
                    print("Todos os pedidos já foram aceites!")
                    continue
                
                print("\n PEDIDOS PENDENTES DE ACEITAÇÃO:")
                for i, pedido in enumerate(pedidos_para_atribuir, 1):
                    estado = estado_atual(int(pedido["idPedido"]))
                    print(f"{i} - Pedido #{pedido['idPedido']} | Cliente #{pedido['idCliente']} | Estado: {estado}")
                
                escolha = ler_int("Escolha o número do pedido (ou 0 para cancelar): ")
                if 0 < escolha <= len(pedidos_para_atribuir):
                    id_pedido = pedidos_para_atribuir[escolha - 1]["idPedido"]
                    atribuir_estafeta_automaticamente(id_pedido)
                elif escolha != 0:
                    print(" Opção inválida!")
            except FileNotFoundError:
                print(" Arquivo de pedidos não encontrado!")
        
        elif opcao == "2":
            
            try:
                with open("atribuicoes.csv", "r", encoding='utf-8') as f:
                    atribuidos = [linha["idPedido"] for linha in csv.DictReader(f) if linha.get("idPedido")]
                
                with open("pedidos.csv", "r", encoding='utf-8') as f:
                    todos_pedidos = [linha for linha in csv.DictReader(f) if linha.get("idPedido")]
                    pendentes = [p for p in todos_pedidos if p["idPedido"] not in atribuidos]
                
                if not pendentes:
                    print(" Todos os pedidos estão aceites!")
                else:
                    print("\n PEDIDOS POR ACEITAR:")
                    for pedido in pendentes:
                        print(f"Pedido #{pedido['idPedido']} | Cliente #{pedido['idCliente']}")
            except FileNotFoundError:
                print(" Arquivo não encontrado!")
        
        elif opcao == "3":
            break
        else:
            print(" Opção inválida!")

def menu_estafeta():
    while True:
        print("\n--- PORTAL ESTAFETA ---")
        print("1 - Listar tarefas")
        print("2 - Aceitar pedido")
        print("3 - Atualizar estado")
        print("4 - Ver métricas")
        print("0 - Voltar")

        opcao = ler_opcao("Escolha uma opção: ", ["1", "2", "3", "4", "0"])

        if opcao == "1":
            idEstafeta = ler_int("ID Estafeta: ")
            listar_tarefas(idEstafeta)

        elif opcao == "2":
            # Listar pedidos atribuídos ao estafeta que ainda não foram aceites
            idEstafeta = ler_int("ID Estafeta: ")
            try:
                pedidos_para_aceitar = []
                with open("atribuicoes.csv", "r", encoding='utf-8') as f:
                    atribuicoes = [linha for linha in csv.DictReader(f) if linha.get("idPedido") and int(linha.get("idEstafeta", 0)) == idEstafeta]
                
                for atrib in atribuicoes:
                    pedido_id = atrib["idPedido"]
                    from estafeta import estado_atual
                    estado = estado_atual(int(pedido_id))
                    # Mostra pedidos que estão atribuídos mas ainda não foram aceites (antes de "em_recolha")
                    if estado in ["atribuída", "aprovada", "pendente"]:
                        pedidos_para_aceitar.append(pedido_id)
                
                if not pedidos_para_aceitar:
                    print(" Nenhum pedido disponível para aceitar!")
                    continue
                
                print("\n PEDIDOS PARA ACEITAR DISTRIBUIÇÃO:")
                for i, pedido_id in enumerate(pedidos_para_aceitar, 1):
                    from estafeta import estado_atual
                    estado = estado_atual(int(pedido_id))
                    print(f"{i} - Pedido #{pedido_id} (Estado: {estado})")
                
                escolha = ler_int("Escolha o número do pedido (ou 0 para cancelar): ")
                if 0 < escolha <= len(pedidos_para_aceitar):
                    idPedido = int(pedidos_para_aceitar[escolha - 1])
                    aceitar_atribuicao(idPedido, idEstafeta)
                elif escolha != 0:
                    print(" Opção inválida!")
            except FileNotFoundError:
                print(" Arquivo não encontrado!")

        elif opcao == "3":
            idPedido = ler_int("ID Pedido: ")
            idEstafeta = ler_int("ID Estafeta: ")

            print("\nEscolha o novo estado:")
            print("1 - Em distribuição")
            print("2 - Concluída")
            print("3 - Falhada")
            
            escolha = ler_int("Opção: ")
            
            estados_map = {1: "em_distribuicao", 2: "concluída", 3: "falhada"}
            
            if escolha in estados_map:
                novo_estado = estados_map[escolha]
                atualizar_estado(idPedido, idEstafeta, novo_estado)
            else:
                print(" Opção inválida!")

        elif opcao == "4":
            idEstafeta = ler_int("ID Estafeta: ")
            metricas_estafeta(idEstafeta)

        elif opcao == "0":
            break

def main():
    while True:
        print("\n====== SEND2YOU ======")
        print("1 - Portal Cliente")
        print("2 - Aceitar pedidos")
        print("3 - Portal Estafeta")
        print("0 - Sair")

        opcao = ler_opcao(
            "Escolha uma opção: ",
            ["1", "2", "3", "0"]
        )

        if opcao == "1":
            menu_cliente()
        elif opcao == "2":
            menu_atribuicao()
        elif opcao == "3":
            menu_estafeta()
        elif opcao == "0":
            print(" A sair da aplicação...")
            break

if __name__ == "__main__":
    main()

