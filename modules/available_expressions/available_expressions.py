from modules.core.core import CFG
from typing import Dict, Tuple, Set, List

def compute_universal_expressions(cfg: CFG) -> Set[Tuple[str, str, str]]:
    universal_exprs = set()
    for instr in cfg.all_instructions():
        expr = instr.expression_key()
        if expr is not None:
            normalized_expr = (expr[0].strip(), expr[1].strip(), expr[2].strip())
            universal_exprs.add(normalized_expr)
    return universal_exprs


def get_block_gen_expressions(block) -> Set[Tuple[str, str, str]]:
    gen = set()
    for instr in block.instructions:
        expr = instr.expression_key()
        dest = instr.defined_variable().strip()
        
        gen = {e for e in gen if dest != e[0].strip() and dest != e[2].strip()}
        
        if expr is not None:
            op1, op, op2 = expr[0].strip(), expr[1].strip(), expr[2].strip()
            if dest != op1 and dest != op2:
                gen.add((op1, op, op2))
    return gen

def get_block_kill_expressions(block, universal_exprs: Set[Tuple[str, str, str]]) -> Set[Tuple[str, str, str]]:
    killed_vars = {v.strip() for v in block.block_def()}
    kill = set()
    for expr in universal_exprs:
        if expr[0].strip() in killed_vars or expr[2].strip() in killed_vars:
            kill.add(expr)
    return kill

def run_available_expressions(cfg: CFG) -> Dict[int, Tuple[Set, Set]]:
    universal_exprs = compute_universal_expressions(cfg)
    
    IN: Dict[int, Set] = {}
    OUT: Dict[int, Set] = {}
    
    entry_id = cfg.block_order[0] if cfg.block_order else None
    
    for bid in cfg.blocks:
        IN[bid] = set()
        if bid == entry_id:
            OUT[bid] = get_block_gen_expressions(cfg.blocks[bid])
        else:
            OUT[bid] = universal_exprs.copy()

    changed = True
    while changed:
        changed = False
        for block in cfg.all_blocks():
            if block.id == entry_id:
                continue
                
            gen = get_block_gen_expressions(block)
            kill = get_block_kill_expressions(block, universal_exprs)

            if block.predecessors:
                preds_outs = [OUT[p] for p in block.predecessors]
                new_in = preds_outs[0].copy()
                for current_out in preds_outs[1:]:
                    new_in &= current_out
            else:
                new_in = set()

            new_out = gen | (new_in - kill)

            if new_in != IN[block.id] or new_out != OUT[block.id]:
                IN[block.id] = new_in
                OUT[block.id] = new_out
                changed = True

    return {bid: (IN[bid], OUT[bid]) for bid in cfg.blocks}