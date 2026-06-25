### O que foi feito:

1. `modules/available_expressions/available_expressions.py`: Implementei a lógica da análise de **Expressões Disponíveis (Available Expressions)** utilizando o motor genérico `run_dataflow`, configurando a direção como **forward** e utilizando **intersection** como função de junção. Também implementei as funções responsáveis por calcular o universo de expressões, além dos conjuntos **GEN** e **KILL** de cada bloco.

2. `modules/available_expressions/test_available_expressions.py`: Criei o script de testes para validar a implementação da análise isoladamente. O teste utiliza um grafo de exemplo, executa a análise e verifica os conjuntos **IN** e **OUT** produzidos para cada bloco básico.

### Como testar:

```bash
python -m modules.available_expressions.test_available_expressions
```
