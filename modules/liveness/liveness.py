from modules.core.core import run_dataflow, union, CFG
from typing import Dict, Tuple, Set

def run_liveness(cfg: CFG) -> Dict[int, Tuple[Set, Set]]:
    """
    Executa a Análise de Longevidade (Liveness Analysis) no CFG fornecido.
    
    Retorna um dicionário mapeando o ID do bloco para uma tupla (IN, OUT).
    """
    return run_dataflow(
        cfg=cfg,
        direction="backward",
        join=union,
        gen_func=lambda block: block.block_use(),
        kill_func=lambda block: block.block_def()
    )
