### O que foi feito:

1. `modules/liveness/liveness.py`: Implementei a lógica de inicialização do motor genérico chamando a função run_dataflow com a direção configurada para backward e usando a união de conjuntos (union). Defini as funções de gen como o block_use() e kill como block_def().

2. `modules/liveness/test_liveness.py`: Criei o script de testes para validar o código isoladamente. Inclusive o teste está passando corretamente no exemplo do PDF com os valores de IN e OUT dos 3 blocos.

### Como testar:
```bash
python -m modules.liveness.test_liveness
```