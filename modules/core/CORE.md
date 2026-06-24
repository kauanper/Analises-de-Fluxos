# core.py — Documentação do Núcleo Comum

Este arquivo documenta tudo que as Pessoas 2, 3 e 4 precisam saber para usar o núcleo sem precisar ler o código.

---

## Importando

```python
from modules.core.core import parse_input, run_dataflow, union, intersection, print_result
```

---

## Formato de entrada

Cada bloco é descrito por três partes, repetidas para cada bloco do grafo:

```
N M
instrucao_1
instrucao_2
...
S1 S2 ...
```

- `N` — id do bloco, `M` — quantidade de instruções
- Cada instrução no formato `destino = operando1 operador operando2` (ex: `a = a+c`, `b=20*c`)
- Última linha: ids dos sucessores, ou `0` se não houver

Exemplo completo (o do enunciado):
```
1 2
a = a+c
b = 4-a
2
2 1
b=20*c
3
3 2
d = a+b
b = 0
0
```

---

## Estruturas de dados

### `Instruction`
Representa uma linha de código de 3 endereços.

| Campo | Tipo | Descrição |
|---|---|---|
| `line_id` | `int` | Posição global única no programa inteiro (não reinicia por bloco) |
| `destination` | `str` | Variável escrita (lado esquerdo do `=`) |
| `operand1` | `str` | Primeiro operando |
| `operator` | `str \| None` | `+`, `-`, `*`, `/` — ou `None` para atribuição direta (`b = 0`) |
| `operand2` | `str \| None` | Segundo operando, ou `None` |
| `raw_text` | `str` | Linha original, útil para debug |

Métodos úteis:
```python
instr.used_variables()   # set com variáveis LIDAS (exclui constantes numéricas)
instr.defined_variable() # str com a variável ESCRITA
instr.expression_key()   # tupla (op1, operator, op2) — usada por Available Expressions
                         # retorna None se for atribuição direta
```

### `BasicBlock`
Representa um bloco básico do CFG.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | `int` | Identificador do bloco |
| `instructions` | `list[Instruction]` | Instruções em ordem de execução |
| `successors` | `list[int]` | Ids dos blocos sucessores |
| `predecessors` | `list[int]` | Ids dos blocos predecessores (calculados pelo parser) |

Métodos úteis (Pessoas 2 e 3 usam diretamente):
```python
block.block_use()  # variáveis lidas ANTES de serem escritas no bloco
block.block_def()  # todas as variáveis escritas no bloco
```

### `CFG`
O grafo de fluxo de controle completo.

| Campo | Tipo | Descrição |
|---|---|---|
| `blocks` | `dict[int, BasicBlock]` | Mapeamento id → bloco |
| `block_order` | `list[int]` | Ids na ordem em que apareceram na entrada |

Métodos úteis:
```python
cfg.get(id)           # retorna o BasicBlock com aquele id
cfg.all_blocks()      # itera blocos na ordem de leitura
cfg.all_instructions() # itera todas as instruções do programa em ordem
```

---

## Funções

### `parse_input(source) -> CFG`
Lê a entrada e monta o CFG. Aceita caminho de arquivo ou lista de strings (útil em testes).

```python
cfg = parse_input("examples/example_statement.txt")

# ou direto em memória (para testes):
cfg = parse_input(["1 2", "a = a+c", "b = 4-a", "2", ...])
```

---

### `run_dataflow(cfg, direction, join, gen_func, kill_func) -> dict[int, tuple[set, set]]`
Motor genérico de fluxo de dados. Itera até ponto fixo.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `cfg` | `CFG` | Grafo vindo de `parse_input()` |
| `direction` | `str` | `"forward"` ou `"backward"` |
| `join` | `callable` | Função de junção: `union` ou `intersection` |
| `gen_func` | `callable` | `gen_func(block) -> set` |
| `kill_func` | `callable` | `kill_func(block) -> set` |

Retorna `{ id_bloco: (IN, OUT) }`.

**Equações aplicadas internamente:**
```
forward:  IN[b]  = join(OUT[p] for p in predecessors(b))
          OUT[b] = gen(b) ∪ (IN[b] − kill(b))

backward: OUT[b] = join(IN[s]  for s in successors(b))
          IN[b]  = gen(b) ∪ (OUT[b] − kill(b))
```

---

### `union(sets_list) -> set`
União de uma lista de conjuntos. Lista vazia retorna `set()`.

### `intersection(sets_list) -> set`
Interseção de uma lista de conjuntos. Lista vazia retorna `set()` — **não o universo** — o que é o comportamento correto para o bloco de entrada do grafo em Available Expressions.

---

### `print_result(analysis_name, result, block_order=None)`
Imprime o resultado no formato do enunciado.

```
--- Liveness ---
OUT[ 1 ] = { a , c }     IN[ 1 ] = { a , c }
OUT[ 2 ] = { a , b }     IN[ 2 ] = { a , c }
OUT[ 3 ] = { }           IN[ 3 ] = { a , b }
```

---

## Como cada análise usa o motor

### Pessoa 2 — Liveness

```python
result = run_dataflow(
    cfg,
    direction="backward",
    join=union,
    gen_func=lambda block: block.block_use(),
    kill_func=lambda block: block.block_def(),
)
```

### Pessoa 3 — Reaching Definitions

```python
result = run_dataflow(
    cfg,
    direction="forward",
    join=union,
    gen_func=calcular_gen_reaching,   # sua função
    kill_func=calcular_kill_reaching, # sua função
)
```

> **Atenção:** os elementos de `IN`/`OUT` aqui não são nomes de variáveis, mas pares `(variavel, line_id)` — porque duas definições da mesma variável em linhas diferentes são elementos distintos.

### Pessoa 4 — Available Expressions

```python
result = run_dataflow(
    cfg,
    direction="forward",
    join=intersection,                   # única análise que usa interseção
    gen_func=calcular_gen_expressoes,    # sua função
    kill_func=calcular_kill_expressoes,  # sua função
)
```

> **Atenção:** como a junção é interseção, o bloco de entrada do grafo (sem predecessores) começa com `OUT = {}` — e isso já está tratado corretamente em `intersection([]) == set()`.

---

## Tabela resumo

| Análise | direction | join | Elementos dos conjuntos |
|---|---|---|---|
| Liveness | `backward` | `union` | nomes de variáveis (`str`) |
| Reaching Definitions | `forward` | `union` | tuplas `(variavel, line_id)` |
| Available Expressions | `forward` | `intersection` | tuplas `(op1, operator, op2)` via `expression_key()` |