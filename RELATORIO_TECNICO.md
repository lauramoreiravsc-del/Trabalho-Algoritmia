# Relatório Técnico - Send2You
## Sistema de Gestão de Entregas

**Autores:** Marcio Senra / Laura Moreira / Dino Costa
**Disciplina:** Algoritmia e Programação
**Universidade do Minho**  
**Ano Letivo:** 2025/2026  
**Data:** Janeiro 2026

---

## 1. Introdução

O Send2You é um sistema completo de gestão de entregas desenvolvido em Python, que simula o funcionamento de uma plataforma de delivery de restaurante. O sistema abrange todo o ciclo de vida de um pedido, desde a criação pelo cliente até à entrega final pelo estafeta.

### 1.1 Objetivos do Projeto

- Criar um sistema funcional de gestão de pedidos
- Implementar validação robusta de dados (NIFs, moradas)
- Integrar APIs externas para geolocalização
- Gerir estados complexos de pedidos
- Aplicar conceitos de programação estruturada e modular

---

## 2. Arquitetura do Sistema

### 2.1 Estrutura Modular

O sistema foi dividido em vários módulos para facilitar a manutenção e compreensão:

- main.py: Interface principal e menus de navegação
- cliente.py: Lógica relacionada com clientes e criação de pedidos
- estafeta.py: Gestão de estafetas e atualizações de estado
- catalogo.py: Gestão do catálogo de produtos
- localizacao.py: Integração com APIs de geolocalização

Esta abordagem modular facilita:
- Teste individual de cada componente
- Reutilização de código
- Manutenção e debug
- Trabalho colaborativo (se necessário)

# 2.2 Armazenamento de Dados

Optei por usar ficheiros CSV para armazenamento pelos seguintes motivos:

*Vantagens:
- Simplicidade de implementação
- Fácil visualização e debug (podem ser abertos no Excel)
- Não requer instalação de base de dados
- Formato universal e portável

*Limitações conhecidas:
- Menor performance em grandes volumes
- Sem controlo de concorrência
- Possibilidade de corrupção se editados manualmente

### 2.3 Ficheiros CSV Utilizados

| Ficheiro | Descrição | Campos Principais |
|----------|-----------|-------------------|
| clientes.csv | Dados dos clientes | idCliente, nome, nif, cidade, concelho, distrito |
| pedidos.csv | Cabeçalhos dos pedidos | idPedido, idCliente, origem, destino, dataCriacao |
| itens_pedido.csv | Itens individuais | idItemPedido, idPedido, idItem, quantidade, preco_unitario |
| eventos_pedido.csv | Histórico de estados | idEvento, idPedido, estado, timestamp, utilizador |
| estafetas.csv | Dados dos estafetas | idEstafeta, nome, zona, turno, ativo |
| atribuicoes.csv | Ligação pedido-estafeta | idAtribuicao, idPedido, idEstafeta, dataAtribuicao |

---

## 3. Funcionalidades Implementadas

### 3.1 Validação de NIF Português

Implementei o algoritmo oficial de validação de NIF que inclui:

1. Verificação de formato: 9 dígitos numéricos
2. Validação do primeiro dígito: Deve ser 1, 2, 3, 5, 6 ou 8
3. Cálculo do dígito de controlo: Usando multiplicadores de 9 a 2

**Algoritmo:**
```
checksum = Σ(digito[i] × (9-i)) para i=0 até 7
resto = checksum % 11
digito_controlo = 0 se resto ∈ {0,1}, senão 11 - resto
```

Esta implementação garante que apenas NIFs válidos são aceites no sistema.

### 3.2 Sistema de Geocodificação e Rotas

#### APIs Utilizadas

**Nominatim (OpenStreetMap)**
- Converte moradas em coordenadas GPS
- Gratuito, sem necessidade de chave API
- Rate limit: 1 pedido por segundo

**OSRM (Open Source Routing Machine)**
- Calcula rotas reais de condução
- Retorna distância e tempo estimado
- Considera vias, velocidades e trânsito típico

#### Validação de Raio de Entrega

Implementei um sistema que:
1. Geocodifica a morada do cliente
2. Calcula a rota do restaurante até ao cliente
3. Verifica se a distância está dentro do raio máximo (30km)
4. Rejeita o pedido se estiver fora do raio

Esta validação acontece **antes** de criar o pedido, evitando pedidos inválidos no sistema.

### 3.3 Aceitar pedidos e Gestão de Estados

Implementei um fluxo de aceitação de pedidos (UI) e uma máquina de estados para rastrear o ciclo de vida:

```
pendente → aprovada → atribuída → em_recolha → em_distribuicao → concluída/falhada
```

Cada transição é registada em `eventos_pedido.csv` com timestamp, criando um histórico completo. A interface do sistema usa a terminologia "Aceitar pedidos" para as ações dos estafetas, mantendo internamente os estados técnicos (ex.: `atribuída`).

---

## 4. Desafios e Soluções

### 4.1 Integração com APIs Externas

**Desafio:** APIs podem falhar ou ter timeouts

**Solução:** 
- Implementei tratamento de exceções robusto
- Timeout configurado (10 segundos)
- Mensagens claras ao utilizador em caso de falha

### 4.2 Validação de Moradas

**Desafio:** Moradas genéricas não são encontradas pelo Nominatim

**Solução:**
- Pedir morada completa (rua, número, cidade)
- Validar via geocodificação antes de aceitar
- Mensagem clara pedindo mais detalhes se falhar

### 4.3 Gestão de Ficheiros CSV

**Desafio:** Sincronização entre múltiplos ficheiros

**Solução:**
- IDs auto-incrementais únicos
- Funções centralizadas para leitura/escrita
- Validação de integridade referencial onde crítico

### 4.4 User Experience

**Desafio:** Evitar mensagens técnicas confusas

**Solução:**
- Silenciei logs técnicos das APIs
- Mensagens claras em português
- Feedback visual (✅, ❌, 📦, etc.)

---

## 5. Limitações e Trabalho Futuro

### 5.1 Limitações Conhecidas

1. **Sem autenticação real**: Sistema usa apenas IDs, sem passwords
2. **Sem controlo de stock**: Não verifica stock disponível
3. **Geocodificação**: Dependente da qualidade dos dados do OSM
4. **Concorrência**: Não suporta múltiplos utilizadores simultâneos
5. **Persistência**: Dados podem ser perdidos se ficheiros CSV corrompidos

---

## 6. Conclusão

O desenvolvimento do Send2You permitiu-me aplicar diversos conceitos de programação:

- **Modularização**: Divisão lógica em módulos independentes
- **Validação de dados**: Algoritmos complexos (NIF) e integração com APIs
- **Gestão de estados**: Máquinas de estado e rastreamento de eventos
- **Tratamento de erros**: Exceções e validação robusta
- **Persistência**: Manipulação de ficheiros CSV
- **User Experience**: Interface de terminal amigável

Os principais desafios foram a integração com APIs externas e a garantia de validação robusta dos inputs. A solução final é funcional e demonstra a aplicação prática dos conceitos aprendidos na disciplina.

---

## 7. Referências

- Documentação Python: https://docs.python.org/3/
- Geopy Documentation: https://geopy.readthedocs.io/
- Nominatim API: https://nominatim.org/
- OSRM API: http://project-osrm.org/
- Algoritmo NIF: Autoridade Tributária e Aduaneira (AT)
- OpenStreetMap: https://www.openstreetmap.org/

---
