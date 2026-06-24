import os

from modules.core.core import (
    parse_input,
    union,
    intersection,
    run_dataflow,
    print_result,
)

EXAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "example_statement.txt"
)


# Parser
def test_parse_block_count():
    cfg = parse_input(EXAMPLE_PATH)
    assert len(cfg.blocks) == 3, f"Esperado 3 blocos, obtido {len(cfg.blocks)}"
    assert cfg.block_order == [1, 2, 3]
    print("OK: quantidade e ordem dos blocos")


def test_parse_successors():
    cfg = parse_input(EXAMPLE_PATH)
    assert cfg.get(1).successors == [2]
    assert cfg.get(2).successors == [3]
    assert cfg.get(3).successors == []
    print("OK: sucessores")


def test_predecessors_calculated_correctly():
    cfg = parse_input(EXAMPLE_PATH)
    assert cfg.get(1).predecessors == []
    assert cfg.get(2).predecessors == [1]
    assert cfg.get(3).predecessors == [2]
    print("OK: predecessores calculados a partir dos sucessores")


def test_block1_instructions():
    cfg = parse_input(EXAMPLE_PATH)
    i1, i2 = cfg.get(1).instructions
    assert (i1.destination, i1.operand1, i1.operator, i1.operand2, i1.line_id) == ("a", "a", "+", "c", 1)
    assert (i2.destination, i2.operand1, i2.operator, i2.operand2, i2.line_id) == ("b", "4", "-", "a", 2)
    print("OK: instrucoes do bloco 1")


def test_global_line_id_unique_across_blocks():
    cfg = parse_input(EXAMPLE_PATH)
    ids = [instr.line_id for instr in cfg.all_instructions()]
    assert ids == [1, 2, 3, 4, 5], f"Esperado [1,2,3,4,5], obtido {ids}"
    print("OK: line_id global unico e crescente")


def test_parsing_tolerant_to_inconsistent_spacing():
    cfg = parse_input(EXAMPLE_PATH)
    instr = cfg.get(2).instructions[0]
    assert (instr.destination, instr.operand1, instr.operator, instr.operand2) == ("b", "20", "*", "c")
    print("OK: tolerancia a espacos inconsistentes")


def test_direct_assignment_without_operator():
    cfg = parse_input(EXAMPLE_PATH)
    instr = cfg.get(3).instructions[1]
    assert instr.destination == "b"
    assert instr.operand1 == "0"
    assert instr.operator is None
    assert instr.operand2 is None
    print("OK: atribuicao direta (b = 0)")


def test_parse_input_accepts_list_of_lines():
    cfg = parse_input(["1 1", "x = 5", "0"])
    assert len(cfg.blocks) == 1
    assert cfg.get(1).instructions[0].destination == "x"
    print("OK: parse_input aceita lista de linhas")


def test_single_block_graph():
    cfg = parse_input(["1 2", "a = b+c", "x = a", "0"])
    assert len(cfg.blocks) == 1
    assert cfg.get(1).successors == []
    assert cfg.get(1).predecessors == []
    assert len(cfg.get(1).instructions) == 2
    print("OK: grafo com bloco unico")


def test_block_with_no_instructions():
    cfg = parse_input(["1 0", "2", "2 1", "x = 1", "0"])
    assert cfg.get(1).instructions == []
    assert cfg.get(1).successors == [2]
    print("OK: bloco sem instrucoes (M=0)")


def test_block_use_and_def():
    cfg = parse_input(EXAMPLE_PATH)
    b1 = cfg.get(1)
    assert b1.block_use() == {"a", "c"}, b1.block_use()
    assert b1.block_def() == {"a", "b"}, b1.block_def()
    print("OK: block_use / block_def do bloco 1")


def test_block_use_respects_local_redefinition():
    cfg = parse_input(["1 2", "x = 1", "y = x+x", "0"])
    assert cfg.get(1).block_use() == set()
    assert cfg.get(1).block_def() == {"x", "y"}
    print("OK: block_use respeita redefinicao local")


def test_block_use_constant_not_included():
    cfg = parse_input(["1 1", "a = 3+4", "0"])
    assert cfg.get(1).block_use() == set()
    print("OK: constantes nao entram em block_use")


# Funcoes de juncao
def test_union():
    assert union([{"a", "b"}, {"b", "c"}]) == {"a", "b", "c"}
    assert union([{"a"}]) == {"a"}
    assert union([]) == set()
    print("OK: union")


def test_intersection():
    assert intersection([{"a", "b"}, {"b", "c"}]) == {"b"}
    assert intersection([{"a"}]) == {"a"}
    print("OK: intersection")


def test_intersection_empty_list_returns_empty_set():
    assert intersection([]) == set()
    print("OK: intersection([]) == set()")


# Motor run_dataflow
def test_run_dataflow_backward_liveness_matches_expected_output():
    cfg = parse_input(EXAMPLE_PATH)
    result = run_dataflow(
        cfg,
        direction="backward",
        join=union,
        gen_func=lambda b: b.block_use(),
        kill_func=lambda b: b.block_def(),
    )
    assert result[1] == ({"a", "c"}, {"a", "c"}), result[1]
    assert result[2] == ({"a", "c"}, {"a", "b"}), result[2]
    assert result[3] == ({"a", "b"}, set()),       result[3]
    print("OK: run_dataflow (Liveness) bate exatamente com o enunciado")


def test_run_dataflow_forward_union():
    cfg = parse_input(["1 1", "a = 1", "2", "2 1", "b = a", "3", "3 1", "c = b", "0"])
    result = run_dataflow(
        cfg,
        direction="forward",
        join=union,
        gen_func=lambda b: b.block_def(),
        kill_func=lambda b: set(),
    )
    assert result[1][1] == {"a"}
    assert result[2][1] == {"a", "b"}
    assert result[3][1] == {"a", "b", "c"}
    print("OK: run_dataflow forward+union")


def test_run_dataflow_forward_intersection_diamond():
    cfg = parse_input([
        "1 0", "2 3",   
        "2 1", "x = a+b", "4",
        "3 0", "4",
        "4 0", "0",
    ])
    result = run_dataflow(
        cfg,
        direction="forward",
        join=intersection,
        gen_func=lambda b: b.block_def(),
        kill_func=lambda b: set(),
    )
    assert result[4][0] == set(), f"IN[B4] esperado vazio, obtido {result[4][0]}"
    print("OK: run_dataflow forward+intersection (diamante)")


def test_run_dataflow_invalid_direction():
    cfg = parse_input(["1 1", "a = 1", "0"])
    try:
        run_dataflow(cfg, direction="sideways", join=union,
                     gen_func=lambda b: set(), kill_func=lambda b: set())
        assert False, "Deveria ter lancado ValueError"
    except ValueError:
        pass
    print("OK: direction invalida lanca ValueError")


def test_print_result_does_not_raise():
    cfg = parse_input(EXAMPLE_PATH)
    result = run_dataflow(cfg, direction="backward", join=union,
                          gen_func=lambda b: b.block_use(),
                          kill_func=lambda b: b.block_def())
    print_result("Teste", result, block_order=cfg.block_order)
    print("OK: print_result sem erros")


# Execucao
if __name__ == "__main__":
    test_parse_block_count()
    test_parse_successors()
    test_predecessors_calculated_correctly()
    test_block1_instructions()
    test_global_line_id_unique_across_blocks()
    test_parsing_tolerant_to_inconsistent_spacing()
    test_direct_assignment_without_operator()
    test_parse_input_accepts_list_of_lines()
    test_single_block_graph()
    test_block_with_no_instructions()

    test_block_use_and_def()
    test_block_use_respects_local_redefinition()
    test_block_use_constant_not_included()

    test_union()
    test_intersection()
    test_intersection_empty_list_returns_empty_set()

    test_run_dataflow_backward_liveness_matches_expected_output()
    test_run_dataflow_forward_union()
    test_run_dataflow_forward_intersection_diamond()
    test_run_dataflow_invalid_direction()
    test_print_result_does_not_raise()

    print("\nTodos os testes do nucleo (core) passaram.")