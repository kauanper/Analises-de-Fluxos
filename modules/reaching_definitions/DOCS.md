# Reaching Definitions — Documentação do Módulo

Este submódulo implementa a análise de fluxo de dados **Reaching Definitions** (Definições Alcançantes) utilizando o motor genérico disponibilizado pelo núcleo comum (`modules.core.core`).

---

## Funcionamento Teórico

A análise determina quais as definições (atribuições de valores a variáveis) que podem alcançar cada ponto do programa sem serem intercetadas ("mortas") por outra definição intermédia.

### Configuração do Motor de Fluxo

| Parâmetro | Configuração | Justificação |
|---|---|---|
| **Direção** | `forward` | A informação propaga-se de cima para baixo, seguindo o fluxo natural de execução. |
| **Junção (`join`)** | `union` | Uma definição alcança o início de um bloco se alcançar o final de **pelo menos um** dos seus predecessores ($IN[b] = \bigcup OUT[p]$). |
| **Elementos dos Conjuntos** | Tuplas `(variavel, line_id)` | Diferentes linhas de código podem definir a mesma variável. Usar o `line_id` global permite distinguir qual a definição exata que está a alcançar o ponto. |

---

## Algoritmo e Implementação

O motor genérico aplica internamente a equação clássica de ponto fixo:
$$OUT[b] = GEN[b] \cup (IN[b] - KILL[b])$$

Para viabilizar este cálculo com a assinatura do motor, a lógica executa em duas etapas:

1. **Pré-computação Global:** Antes de iniciar as iterações, o programa mapeia todas as definições existentes no código fonte (`all_defs`). Isso permite saber exatamente quais os `line_ids` que cada variável possui no programa inteiro.
2. **Funções de Bloco (*Closures*):**
   - **`GEN` (`calcular_gen_reaching`)**: Varre as instruções do bloco básico de trás para a frente. A primeira definição encontrada para uma variável é adicionada ao conjunto `GEN` (garantindo que é a definição mais recente do bloco). As definições anteriores da mesma variável dentro do próprio bloco são mascaradas.
   - **`KILL` (`calcular_kill_reaching`)**: Se um bloco define uma variável, ele "mata" todas as outras definições existentes para essa mesma variável no resto do programa inteiro (recorrendo ao mapa global gerado na etapa 1).

---

## Estrutura de Funções

### `run_reaching_definitions(cfg: CFG) -> dict[int, tuple[set, set]]`
Função principal chamada para executar a análise sobre o Grafo de Fluxo de Controlo (CFG).

- **Entrada:** Instância de `CFG` obtida via `parse_input`.
- **Saída:** Um dicionário mapeando o ID do bloco para uma tupla `(IN, OUT)`, onde cada conjunto contém tuplas do tipo `(str, int)`.

---

## Como Executar e Testar

Para correr os testes deste módulo a partir da raiz do projeto, executa:
```bash
python -m modules.reaching_definitions.test_reaching_definitions