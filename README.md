# Trabalho II — Análises de Fluxo de Dados
**Compiladores — Prof. Lucas Ismaily — UFC Quixadá**

---

## Equipe

| Pessoa | Nome | Módulo |
|---|---|---|
| 1 | Francisco Kauan Pereira Cavalcante | Núcleo comum (core) |
| 2 | — | Liveness Analysis |
| 3 | — | Reaching Definitions |
| 4 | — | Available Expressions |

---

## Sobre o projeto

Implementação de três análises clássicas de fluxo de dados sobre um grafo de fluxo de controle (CFG):

- **Liveness Analysis** — quais variáveis estão vivas antes e depois de cada bloco
- **Reaching Definitions** — quais definições alcançam cada ponto do programa
- **Available Expressions** — quais expressões já foram calculadas em todos os caminhos até um ponto

As três análises compartilham um núcleo comum (parser + CFG + motor genérico), e cada uma é implementada de forma independente plugando suas próprias regras `gen`/`kill` no motor.

---

## Estrutura do projeto

```
trabalho2-compiladores/
├── main.py                                   # Integração final
├── README.md
├── modules/
│   ├── __init__.py
│   ├── core/                                 # Núcleo comum 
│   │   ├── __init__.py
|   |   ├── CORE.md
│   │   ├── core.py
│   │   └── test_core.py
│   ├── liveness/                             # Questão 1
│   │   ├── __init__.py
│   │   ├── liveness.py
│   │   └── test_liveness.py
│   ├── reaching_definitions/                 # Questão 2
│   │   ├── __init__.py
│   │   ├── reaching_definitions.py
│   │   └── test_reaching_definitions.py
│   └── available_expressions/                # Questão 3
│       ├── __init__.py
│       ├── available_expressions.py
│       └── test_available_expressions.py
│
└── examples/                          # Entradas de teste compartilhadas
    └── example_statement.txt
```

---
 
## Como executar
 
Todos os comandos devem ser rodados a partir da **raiz do projeto**.
 
### Integração completa
```bash
python main.py examples/example_statement.txt
```
## Módulos
 
Cada submódulo segue a mesma estrutura:
 
```
modulo/
├── __init__.py
├── modulo.py        # implementação da análise
└── test_modulo.py   # testes, executável de forma independente
```
 
O arquivo de teste de cada módulo pode ser rodado de forma isolada — sem precisar que os outros módulos estejam prontos — e valida a análise contra os exemplos da pasta `examples/`.
 
---

### core — Núcleo comum
**Responsável:** Francisco Kauan Pereira Cavalcante

> Parser da entrada, estrutura do CFG e motor genérico de fluxo de dados. É a base que os outros três módulos importam.

Componentes principais:
- `parse_input(source)` — lê o arquivo de entrada e monta o CFG
- `run_dataflow(cfg, direction, join, gen_func, kill_func)` — motor genérico, itera até ponto fixo
- `union` / `intersection` — funções de junção prontas para usar
- `print_result(name, result)` — impressão padronizada no formato do enunciado

Para detalhes de uso, consulte o `CORE.md`.

```bash
python -m modules.core.test_core
```

---

### liveness — Liveness Analysis
**Responsável:** —

> Em desenvolvimento.

---

### reaching_definitions — Reaching Definitions
**Responsável:** —

> Em desenvolvimento.

---

### available_expressions — Available Expressions
**Responsável:** —

> Em desenvolvimento.