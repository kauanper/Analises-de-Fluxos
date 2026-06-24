# Roteiro do Trabalho II — Opção 3 (Análises de Fluxo)
### Compiladores — Prof. Lucas Ismaily — UFC Quixadá

Este documento é o "contrato técnico" da equipe: define exatamente o que cada pessoa entrega, como ela acessa o núcleo comum, e como as quatro partes se encaixam sem que ninguém precise esperar ninguém.

---

## Princípio geral da divisão

Uma pessoa constrói a **base compartilhada** (parser + estrutura do grafo + motor de fluxo de dados). As outras três constroem **cada uma sua análise**, de forma paralela e independente entre si, e cada uma já entrega sua parte **integrada e testável sozinha** — sem depender da conclusão das outras duas.

A única coisa que precisa ser combinada **antes de codar** é o "contrato" abaixo: os nomes dos campos do grafo, e a assinatura das funções. Combinado isso, ninguém trava esperando ninguém.

---

## Pessoa 1 — Núcleo comum (parser + CFG + motor de fluxo de dados)

Esta é a entrega mais crítica do trabalho. Tudo depende dela, então deve ser a primeira a ficar pronta — mesmo que de forma simples no início, refinando depois.

### 1.1 — O parser

O parser é o módulo que lê o texto de entrada (no formato descrito no enunciado) e transforma isso em estruturas de dados que o resto do programa consegue manipular. Sem ele, ninguém mais tem o que processar.

**O que o parser precisa fazer, passo a passo:**

1. **Ler o cabeçalho de cada bloco**: a primeira linha de cada grupo tem dois inteiros `N M` — `N` é o identificador do bloco básico, `M` é quantas linhas de código de três endereços ele contém.
2. **Ler as M linhas de código** que seguem, cada uma no formato `destino = operando1 operador operando2` (ex: `a = a+c`, `b = 4-a`, `b = 20*c`). Atenção: o enunciado mistura espaços de forma inconsistente (`a = a+c` vs `b=20*c`), então o parser precisa ser tolerante a isso — não pode assumir que sempre vai ter espaço em volta do operador.
3. **Ler a linha de sucessores**: uma sequência de inteiros representando os blocos que sucedem o bloco `N` atual, ou `0` se não houver nenhum.
4. **Repetir esse processo** até o fim da entrada — a entrada tem **vários blocos seguidos**, não um só (no exemplo do enunciado, são 3 blocos consecutivos, cada um com seu próprio cabeçalho `N M`, suas linhas de código e sua linha de sucessores).
5. **Decidir a fonte da entrada**: ler de um arquivo de texto (mais fácil de testar com múltiplos exemplos) ou da entrada padrão (stdin). Sugestão: aceitar os dois — ler de arquivo se um caminho for passado por argumento, senão ler do stdin. Isso facilita tanto o teste automatizado quanto a entrega seguindo o que o professor esperar.

**Sugestão de robustez (vai evitar bugs nos outros três):**
- Validar que toda variável usada num operando vai sempre aparecer como string (não como número), exceto quando for de fato uma constante numérica.
- Decidir logo no início como representar uma instrução internamente — sugestão de estrutura:
  ```
  Instrucao:
      linha_id       (a posição/linha global da instrução, importante pra Reaching Definitions)
      destino         (ex: "a")
      operando1       (ex: "a")
      operador        (ex: "+", "-", "*", "/", ou None se for atribuição direta)
      operando2       (ex: "c", ou None se não houver)
  ```
- Gerar, para cada instrução, dois conjuntos auxiliares prontos — isso vai ser reaproveitado pelas 3 análises:
  - `def(instrucao)`: a variável escrita (sempre o destino)
  - `use(instrucao)`: as variáveis lidas (operando1 e operando2, quando forem variáveis e não constantes)

### 1.2 — A estrutura do grafo (CFG)

Depois de ler os blocos, a Pessoa 1 monta o grafo de fluxo de controle propriamente dito.

**Estrutura sugerida (o "contrato" que todo mundo vai usar):**

```
BasicBlock:
    id              (inteiro, o N do bloco)
    instructions    (lista ordenada de Instrucao)
    successors      (lista de ids dos blocos sucessores)
    predecessors    (lista de ids dos blocos predecessores — calculada pela Pessoa 1!)

CFG:
    blocks          (dicionário: id -> BasicBlock)
    block_ids_ordenados   (lista dos ids na ordem em que apareceram na entrada)
```

**Ponto importante**: os **predecessores não vêm prontos da entrada** (o enunciado só dá os sucessores) — é a Pessoa 1 que precisa calculá-los, percorrendo todos os blocos e, para cada sucessor `s` de um bloco `b`, registrando `b` como predecessor de `s`. Isso é usado pelas 3 análises (Liveness usa sucessores; Reaching Definitions e Available Expressions usam predecessores).

### 1.3 — O motor genérico de fluxo de dados

Esta é a peça que faz a Opção 3 valer a pena: ao invés de cada pessoa escrever seu próprio loop de iteração até ponto fixo, a Pessoa 1 escreve **um único motor parametrizável**, e as outras três só "plugam" suas regras.

**Assinatura sugerida:**

```
função resolver_fluxo_dados(cfg, direcao, juncao, funcao_gen, funcao_kill):
    # direcao: "forward" ou "backward"
    # juncao: função que recebe uma lista de conjuntos e devolve um conjunto (união ou interseção)
    # funcao_gen(bloco) -> conjunto
    # funcao_kill(bloco) -> conjunto
    #
    # devolve: dicionário { id_bloco: (IN, OUT) }
```

**Lógica interna (pseudocódigo):**
```
inicializar IN[b] = vazio e OUT[b] = vazio para todo bloco b
   (caso especial: se juncao é interseção e direção é forward,
    o bloco de entrada deve iniciar OUT vazio — não "tudo": ver nota da Pessoa 4)

repetir:
    mudou = falso
    para cada bloco b (na ordem apropriada à direção):
        se direção == forward:
            entrada = juncao([OUT[p] para p em predecessores(b)])
            novo_IN[b] = entrada
            novo_OUT[b] = gen(b) ∪ (novo_IN[b] - kill(b))
        se direção == backward:
            saida = juncao([IN[s] para s em sucessores(b)])
            novo_OUT[b] = saida
            novo_IN[b] = gen(b) ∪ (novo_OUT[b] - kill(b))
        se novo_IN[b] != IN[b] ou novo_OUT[b] != OUT[b]:
            mudou = verdadeiro
        atualizar IN[b], OUT[b]
até não mudar mais

devolver { b: (IN[b], OUT[b]) para todo bloco b }
```

Isso é só a casca — quem decide o que `gen` e `kill` significam, e se a junção é união ou interseção, são as Pessoas 2, 3 e 4, cada uma na sua análise.

### 1.4 — Função de impressão padronizada

Para que a saída de todo mundo saia no mesmo formato (o do enunciado: `OUT[1] = {a, c}` etc.), a Pessoa 1 também entrega uma função utilitária de impressão, para todo mundo reaproveitar:

```
função imprimir_resultado(nome_analise, resultado):
    # resultado: { id_bloco: (IN, OUT) }
    # imprime no formato:
    #   OUT[1] = { a, c }     IN[1] = { a, c }
    #   ...
```

### 1.5 — O papel da Pessoa 1 na integração final

Como cada pessoa (2, 3, 4) vai integrar e testar sua própria análise de forma independente (ver seção "Integração" mais abaixo), o papel da Pessoa 1 na integração final é leve:
- Garantir que o módulo do núcleo (parser + CFG + motor + impressão) está disponível num arquivo/módulo separado e bem documentado (`nucleo.py`, por exemplo), pronto para ser importado pelos outros três sem nenhuma alteração.
- Revisar, ao final, se as três análises estão de fato importando o núcleo da mesma forma (e não copiando/colando trechos do parser, o que geraria inconsistência).
- Disponibilizar 2-3 arquivos de teste de entrada (incluindo o exemplo do enunciado) para todo mundo validar contra a mesma base.

### Sugestões extras da minha parte (Pessoa 1):
- Escrever 1 ou 2 testes automatizados simples (ex: comparar a saída do CFG montado a partir do exemplo do enunciado com o resultado esperado manualmente) — isso evita que um bug no parser apareça só quando as outras pessoas já estiverem testando suas análises.
- Documentar, em um comentário no topo do arquivo, exatamente os nomes dos campos (`block.id`, `block.successors`, etc.) — isso é o que evita retrabalho.
- Linguagem sugerida: **Python**, porque `set()` nativo já faz união (`|`), interseção (`&`) e diferença (`-`) de forma direta — o motor de fluxo de dados fica bem mais simples de escrever e ler do que em Java/C++.

---

## Mecanismo comum de acesso ao núcleo (Pessoas 2, 3 e 4)

Antes de detalhar cada análise, vale explicar o mecanismo que as três pessoas vão usar — é o mesmo para todas:

1. **Importar o módulo do núcleo** (ex: `from nucleo import parse_input, resolver_fluxo_dados, imprimir_resultado`).
2. **Chamar o parser** para obter o objeto `cfg` a partir do arquivo de entrada.
3. **Definir duas funções locais**, específicas da própria análise: `gen(bloco)` e `kill(bloco)` — são essas duas funções (mais a direção e o tipo de junção) que diferenciam uma análise da outra. É só nisso que cada pessoa realmente precisa pensar.
4. **Chamar o motor genérico**, passando a direção, a junção (união ou interseção) e as funções `gen`/`kill` que ela mesma escreveu.
5. **Imprimir o resultado** usando a função utilitária do núcleo.
6. Empacotar os passos 2-5 dentro de uma função com a assinatura combinada (ex: `def liveness(cfg): ...`), e também deixar um bloco "se executado diretamente, roda standalone" no final do próprio arquivo — assim a pessoa testa sozinha, sem esperar a integração final.

Esse mecanismo é o que permite que cada pessoa trabalhe 100% isolada: ela só precisa saber a "forma" do `cfg` (definida pela Pessoa 1) e a assinatura combinada da própria função — o resto é problema só dela.

---

## Pessoa 2 — Liveness Analysis (Análise de Longevidade)

### Conceito
Para cada bloco, descobre quais variáveis estão "vivas" (podem ainda ser usadas no futuro) antes (`IN`) e depois (`OUT`) da execução do bloco.

### Direção e junção
- **Direção**: backward (anda do fim do grafo para o início)
- **Junção**: união

### Regras de gen/kill (o que essa pessoa escreve)
- `gen(bloco)` = conjunto `use` do bloco: as variáveis lidas antes de serem escritas dentro dele
- `kill(bloco)` = conjunto `def` do bloco: as variáveis escritas dentro dele

### Acesso ao núcleo
```
cfg = nucleo.parse_input(caminho_arquivo)
resultado = nucleo.resolver_fluxo_dados(
    cfg,
    direcao="backward",
    juncao=uniao,
    funcao_gen=calcular_use,
    funcao_kill=calcular_def
)
nucleo.imprimir_resultado("Liveness", resultado)
```

### Assinatura de entrega (combinada com a equipe)
```
def liveness(cfg) -> dict[int, tuple[set, set]]:
    ...
```

### Teste prioritário
O próprio exemplo do enunciado já traz a saída esperada (`OUT[1]={a,c}`, `IN[1]={a,c}`, etc.) — validar contra ele é obrigatório antes de considerar essa parte pronta, pois é provavelmente o primeiro caso que será conferido na correção.

### Observação
Essa mesma análise também é pedida na Opção 2 (Alocação de Registradores) — então se a equipe quiser, esse código fica reaproveitável caso, por algum motivo, precisem revisitar esse conteúdo depois.

---

## Pessoa 3 — Reaching Definitions (Definições Alcançantes)

### Conceito
Em vez de rastrear variáveis, rastreia **definições específicas** (uma atribuição em uma linha específica do código). `IN[b]`/`OUT[b]` indicam quais definições "alcançam" aquele ponto do programa sem terem sido sobrescritas no caminho.

### Direção e junção
- **Direção**: forward (anda do início do grafo para o fim)
- **Junção**: união

### Regras de gen/kill (a parte mais delicada desta análise)
- `gen(bloco)`: as definições feitas dentro do próprio bloco — atenção: se a mesma variável for redefinida mais de uma vez dentro do mesmo bloco, só a **última** definição dela sobrevive como gen daquele bloco (as anteriores já morrem internamente).
- `kill(bloco)`: para cada variável definida no bloco, **todas as outras definições daquela variável que existem em qualquer outro bloco do programa**. Isso exige que essa pessoa monte, antes de tudo, um mapeamento global: para cada variável, todas as linhas onde ela é definida em todo o programa — não só dentro do bloco atual.

### Como representar uma "definição" (ponto de atenção que pode gerar bug)
Diferente de Liveness (que trabalha com nomes de variáveis), aqui cada elemento dos conjuntos `IN`/`OUT` deve identificar **a variável + a linha onde foi definida** (ex: `("a", linha=2)`), porque pode haver várias definições da mesma variável em blocos diferentes, e cada uma é um elemento distinto do conjunto — usar só o nome da variável quebraria a análise.

### Acesso ao núcleo
```
cfg = nucleo.parse_input(caminho_arquivo)
resultado = nucleo.resolver_fluxo_dados(
    cfg,
    direcao="forward",
    juncao=uniao,
    funcao_gen=calcular_gen_definicoes,
    funcao_kill=calcular_kill_definicoes
)
nucleo.imprimir_resultado("Reaching Definitions", resultado)
```

### Assinatura de entrega
```
def reaching_definitions(cfg) -> dict[int, tuple[set, set]]:
    ...
```

### Teste prioritário
Montar um grafo de teste próprio (não tem exemplo pronto no enunciado para esta análise) que tenha **a mesma variável redefinida em pelo menos dois blocos diferentes** — esse é o caso que exercita o `kill` global e é onde normalmente aparecem bugs.

---

## Pessoa 4 — Available Expressions (Expressões Disponíveis)

### Conceito
Uma expressão (ex: `a+c`) está "disponível" em um ponto do programa se ela já foi calculada antes, em **todos** os caminhos possíveis até aquele ponto, e nenhum dos operandos foi reatribuído depois do cálculo.

### Direção e junção
- **Direção**: forward
- **Junção**: **interseção** (esta é a única análise das três que usa interseção — exercita de fato se o motor da Pessoa 1 foi escrito de forma genérica)

### Regras de gen/kill
- `gen(bloco)`: expressões calculadas dentro do bloco que **não são invalidadas** depois, dentro do próprio bloco (ex: se o bloco calcula `a+c` e depois redefine `a`, essa expressão não entra no gen daquele bloco).
- `kill(bloco)`: qualquer expressão, em qualquer lugar do programa, que use uma variável que é redefinida dentro deste bloco (mesma lógica do Reaching Definitions, mas aplicada a expressões, não a definições).

### Ponto de atenção crítico (a pegadinha mais comum desta análise)
Como a junção é interseção, o **bloco de entrada do grafo** (o que não tem predecessores) precisa começar com `OUT` vazio, e **nunca** com "o conjunto de todas as expressões possíveis" — porque a primeira interseção feita a partir de um conjunto cheio travaria a análise, impedindo que ela convirja corretamente. Isso é diferente do caso geral de inicialização (que normalmente começa vazio em ambas as junções, mas no caso de interseção é importante confirmar esse comportamento explicitamente no bloco de entrada).

### Acesso ao núcleo
```
cfg = nucleo.parse_input(caminho_arquivo)
resultado = nucleo.resolver_fluxo_dados(
    cfg,
    direcao="forward",
    juncao=intersecao,
    funcao_gen=calcular_gen_expressoes,
    funcao_kill=calcular_kill_expressoes
)
nucleo.imprimir_resultado("Available Expressions", resultado)
```

### Assinatura de entrega
```
def available_expressions(cfg) -> dict[int, tuple[set, set]]:
    ...
```

### Teste prioritário
Montar um grafo em formato de **diamante** (um bloco que se divide em dois caminhos e depois os dois se reúnem em um bloco comum) — é o único tipo de estrutura que de fato testa se a interseção está sendo aplicada corretamente (com só um caminho, união e interseção dão o mesmo resultado e o bug passaria despercebido).

---

## Como cada pessoa integra e testa sua própria parte

Como todas as três análises seguem o mesmo mecanismo de acesso ao núcleo, cada pessoa (2, 3, 4) consegue, sozinha:

1. Importar o núcleo já pronto.
2. Implementar sua função (`liveness`, `reaching_definitions` ou `available_expressions`).
3. Adicionar um pequeno bloco no final do próprio arquivo, do tipo:
   ```
   se este arquivo for executado diretamente:
       cfg = nucleo.parse_input("exemplo.txt")
       resultado = liveness(cfg)   # ou a função correspondente
       nucleo.imprimir_resultado("Liveness", resultado)
   ```
4. Rodar e validar com seus próprios casos de teste — **sem precisar que as outras duas análises estejam prontas**.

## Junção final (qualquer pessoa pode fazer, é rápido)

Quando as três análises estiverem prontas e testadas individualmente, juntar tudo em um `main.py` único é trivial — basta importar as três funções e chamar em sequência:

```
from nucleo import parse_input
from liveness import liveness
from reaching_definitions import reaching_definitions
from available_expressions import available_expressions

cfg = parse_input(caminho_da_entrada)
print_resultado("Liveness", liveness(cfg))
print_resultado("Reaching Definitions", reaching_definitions(cfg))
print_resultado("Available Expressions", available_expressions(cfg))
```

---

## Combinados que a equipe precisa travar ANTES de codar

1. **Linguagem única** — todos no mesmo Python (ou outra linguagem escolhida em conjunto), para evitar incompatibilidade na hora de juntar.
2. **Nomes dos campos do CFG** — exatamente como descrito na seção 1.2 (`block.id`, `block.successors`, `block.predecessors`, `block.instructions`).
3. **Assinatura das três funções de análise** — exatamente como descrito nas seções de cada pessoa (`liveness(cfg)`, `reaching_definitions(cfg)`, `available_expressions(cfg)`), todas devolvendo `dict[int, tuple[set, set]]`.
4. **Formato de impressão** — usar a função utilitária da Pessoa 1, e não cada um inventar o próprio formato de saída.

## Sugestões extras para reduzir risco de falha

- **Revisão cruzada antes do envio**: cada pessoa lê rapidamente o código de um colega (não precisa ser profundo, só verificar se a lógica de gen/kill bate com a explicação acima).
- **Casos de teste compartilhados**: usar os mesmos 2-3 arquivos de entrada (incluindo o do enunciado) nas três análises — isso facilita comparar resultados entre si e detectar inconsistência de leitura do grafo.
- **Arquivo com nomes da equipe**: não esquecer de incluir, como exige o enunciado, um arquivo com o nome de todos os membros dentro da pasta zipada — e confirmar que são pelo menos 3 alunos, já que menos que isso zera o trabalho automaticamente.
- **Entregar antes do prazo final** (26/06/2026), como o próprio professor recomenda, para ter margem de reação a qualquer imprevisto de última hora.