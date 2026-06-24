## Estrutura do projeto

```
trabalho2-compiladores/
├── main.py                                   # Integração final — feito ao término dos módulos
├── README.md
│
├── modules/                                  # Código que resolve cada questão
│   ├── __init__.py
│   ├── core/                                 # Núcleo comum: parser + CFG + motor de fluxo de dados
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── test_core.py
│   ├── liveness/                             # Resolve a Questão 1
│   │   ├── __init__.py
│   │   ├── liveness.py
│   │   └── test_liveness.py
│   ├── reaching_definitions/                 # Resolve a Questão 2
│   │   ├── __init__.py
│   │   ├── reaching_definitions.py
│   │   └── test_reaching_definitions.py
│   └── available_expressions/                # Resolve a Questão 3
│       ├── __init__.py
│       ├── available_expressions.py
│       └── test_available_expressions.py
│
└── examples/                                 # Entradas de teste compartilhadas por todos
    └── example_statement.txt
```