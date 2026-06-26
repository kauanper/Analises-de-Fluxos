# Trabalho II — Análises de Fluxo de Dados
**Disciplina de Compiladores com o Prof. Lucas Ismaily — UFC Quixadá**

---

## Equipe

| Pessoa | Nome | Módulo |
|---|---|---|
| 1 | Francisco Kauan Pereira Cavalcante | Núcleo comum (core) |
| 2 | Sávio de Carvalho Soares | Liveness Analysis |
| 3 | Francisco Samuel Cabral Leitão| Reaching Definitions |
| 4 | Ancelmo de Souza Lopes | Available Expressions |

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
    └── test_n.txt
```

---
 
## Como executar
 
Todos os comandos devem ser rodados a partir da **raiz do projeto**.
 
### Integração completa
```bash
python main.py examples/
```
Esse comando processa **todos** os arquivos `.txt` encontrados diretamente dentro da pasta `examples/`. 
Para testar um novo caso, basta adicionar um arquivo `.txt` (seguindo o formato de entrada esperado) 
dentro dessa pasta, sem necessidade de alterar nenhum código. Na próxima execução do comando acima, 
ele já será incluído automaticamente na bateria de testes.

> **Nota:** a busca por arquivos não é recursiva. Apenas `.txt` no nível raiz de `examples/` 
> são processados, não em subpastas.

### Testes de cada módulo
```bash
python -m modules.core.test_core
python -m modules.liveness.test_liveness
python -m modules.reaching_definitions.test_reaching_definitions
python -m modules.available_expressions.test_available_expressions
```

## Módulos
 
Cada submódulo segue a mesma estrutura:
 
```
modulo/
├── __init__.py
├── modulo.py        # implementação da análise
└── test_modulo.py   # testes, executável de forma independente
```

O arquivo de teste de cada módulo pode ser rodado de forma isolada, sem precisar que os outros módulos estejam prontos. Cada pessoa pode implementar e validar sua análise independentemente, apenas importando o núcleo comum (`modules.core.core`) e usando os arquivos de entrada da pasta `examples/` como base de comparação. Isso significa que não há dependência de implementação entre as análises.


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
**Responsável:** Sávio de Carvalho Soares

> Determina quais variáveis estão vivas em cada ponto do programa através do motor backward do núcleo.

- `modules/liveness/liveness.py`: lógica de inicialização do motor genérico chamando a função `run_dataflow` com a direção configurada para backward e usando a união de conjuntos (`union`). As funções gen como o `block_use()` e kill como `block_def()` foram definidas.

- `modules/liveness/test_liveness.py`: script de testes para validar o código isoladamente. O teste está passando corretamente no exemplo do PDF com os valores de IN e OUT dos 3 blocos.

### Como testar:
```bash
python -m modules.liveness.test_liveness
```

---

### reaching_definitions — Reaching Definitions
**Responsável:** Francisco Samuel Cabral Leitão

> Determina quais as definições alcançam cada ponto do programa através do motor forward do núcleo.

- `modules/reaching_definitions/reaching_definitions.py`: implementa a análise de definições alcançantes (Reaching Definitions). A lógica principal utiliza o motor genérico `run_dataflow` configurado para execução **forward**, com a função de junção definida como união (`union`). O módulo efetua um pré-mapeamento global das linhas de atribuição para calcular o conjunto **KILL** de forma precisa perante redefinições. O conjunto **GEN** captura a definição mais recente de uma variável dentro do próprio bloco.

- `modules/reaching_definitions/test_reaching_definitions.py`: script de testes para validar o código. O teste verifica se está passando corretamente com os valores de IN e OUT esperados para cada bloco.

### Como testar:
```bash
python -m modules.reaching_definitions.test_reaching_definitions
```
---

### available_expressions — Available Expressions
**Responsável:** — Ancelmo de Souza Lopes

>  Determina quais expressões estão disponíveis em cada ponto do programa através do motor forward do núcleo.

- `modules/available_expressions/available_expressions.py`: implementa a análise de expressões disponíveis (Available Expressions). A lógica principal utiliza o motor genérico `run_dataflow` configurado para execução **forward**, com operação de junção baseada em **interseção (`intersection`)**. O conjunto universo é formado por todas as expressões presentes no programa (`all_expressions`). O conjunto **GEN** contém as expressões calculadas dentro de cada bloco (`calculate_gen`), removendo aquelas invalidadas por redefinições de variáveis no próprio bloco. O conjunto **KILL** contém todas as expressões do programa que utilizam variáveis redefinidas no bloco (`calculate_kill`).

- `modules/available_expressions/test_available_expressions.py`: contém testes unitários para validar a implementação da análise de expressões disponíveis de forma isolada. Os testes utilizam o exemplo do PDF da disciplina e verificam os valores esperados dos conjuntos **IN** e **OUT** para cada bloco do grafo de fluxo de controle.

### Como testar:
```bash
python -m modules.available_expressions.test_available_expressions
