from modules.core.core import run_dataflow, intersection, CFG


# Retorna todas as expressões existentes no programa.
# Essas expressões formam o "universo" usado para calcular KILL.
def all_expressions(cfg):
    expressions = set()

    for instruction in cfg.all_instructions():
        expression = instruction.expression_key()

        if expression is not None:
            expressions.add(expression)

    return expressions


# Calcula o conjunto GEN do bloco.
# Uma expressão entra em GEN quando é calculada.
# Se alguma variável da expressão for redefinida depois,
# ela deixa de estar disponível e é removida.
def calculate_gen(block):
    gen = set()

    for instruction in block.instructions:

        variable = instruction.defined_variable()

        expressions_to_remove = set()

        # Remove expressões que ficaram inválidas
        for expression in gen:
            operand1, operator, operand2 = expression

            if operand1 == variable or operand2 == variable:
                expressions_to_remove.add(expression)

        for expression in expressions_to_remove:
            gen.remove(expression)

        # Adiciona a expressão produzida pela instrução
        expression = instruction.expression_key()

        if expression is not None:
            gen.add(expression)

    return gen


# Calcula o conjunto KILL.
# Toda expressão do programa que utiliza alguma variável
# redefinida neste bloco pertence ao conjunto KILL.
def calculate_kill(block, universe):
    kill = set()

    defined_variables = block.block_def()

    for expression in universe:
        operand1, operator, operand2 = expression

        if operand1 in defined_variables:
            kill.add(expression)

        elif operand2 in defined_variables:
            kill.add(expression)

    return kill


# Executa a análise de Expressões Disponíveis.
def run_available_expressions(cfg: CFG):

    universe = all_expressions(cfg)

    return run_dataflow(
        cfg=cfg,
        direction="forward",
        join=intersection,
        gen_func=calculate_gen,
        kill_func=lambda block: calculate_kill(block, universe),
    )
