from modules.core.core import run_dataflow, union, CFG
from typing import Dict, Tuple, Set

def run_reaching_definitions(cfg: CFG) -> Dict[int, Tuple[Set, Set]]:
    """
    Executa a Análise de Definições Alcançantes (Reaching Definitions).
    Retorna um dicionário mapeando o ID do bloco para uma tupla (IN, OUT).
    Cada elemento do conjunto é uma tupla (variavel, line_id).
    """
    
    all_defs: Dict[str, Set[int]] = {}
    for instr in cfg.all_instructions():
        var = instr.defined_variable()
        if var not in all_defs:
            all_defs[var] = set()
        all_defs[var].add(instr.line_id)

    def calcular_gen_reaching(block) -> Set[Tuple[str, int]]:
        gen_set = set()
        killed_locally = set()
        for instr in reversed(block.instructions):
            var = instr.defined_variable()
            if var not in killed_locally:
                gen_set.add((var, instr.line_id))
                killed_locally.add(var) 
        return gen_set

    def calcular_kill_reaching(block) -> Set[Tuple[str, int]]:
        kill_set = set()
        vars_defined = block.block_def()
        
        for var in vars_defined:
            for line_id in all_defs.get(var, set()):
                kill_set.add((var, line_id))
        return kill_set

    return run_dataflow(
        cfg=cfg,
        direction="forward",
        join=union,
        gen_func=calcular_gen_reaching,
        kill_func=calcular_kill_reaching
    )