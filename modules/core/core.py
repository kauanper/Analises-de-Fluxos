"""
Nucleo comum do projeto

Exporta:
    parse_input(source)      -> CFG
    union(sets_list)         -> set
    intersection(sets_list)  -> set
    run_dataflow(...)        -> dict[int, tuple[set, set]]
    print_result(...)        -> None

Formato de entrada (enunciado, Trabalho II, Opcao 3):
    Cada bloco e descrito por:
        1. Cabecalho "N M"   — N: id do bloco, M: qtd de instrucoes
        2. M linhas de codigo de 3 enderecos  (ex: "a = a+c", "b=20*c")
        3. Linha de sucessores               (ex: "2 3" ou "0" se nao houver)
    Esse padrao se repete para cada bloco, um apos o outro.

Nomes dos campos (contrato com os outros modulos):
    Instruction:  line_id, destination, operand1, operator, operand2, raw_text
    BasicBlock:   id, instructions, successors, predecessors
    CFG:          blocks, block_order
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Union, List, Dict, Set, Tuple

# Estruturas de dados
@dataclass
class Instruction:
    line_id: int
    destination: str  
    operand1: str
    operator: Optional[str]
    operand2: Optional[str]
    raw_text: str

    @staticmethod
    def is_constant(operand: Optional[str]) -> bool:
        if operand is None:
            return False
        try:
            float(operand)
            return True
        except ValueError:
            return False

    def used_variables(self) -> Set[str]:
        used = set()
        if self.operand1 is not None and not self.is_constant(self.operand1):
            used.add(self.operand1)
        if self.operand2 is not None and not self.is_constant(self.operand2):
            used.add(self.operand2)
        return used

    def defined_variable(self) -> str:
        return self.destination

    def expression_key(self) -> Optional[Tuple[str, str, str]]:

        if self.operator is None:
            return None
        return (self.operand1, self.operator, self.operand2)

    def __repr__(self) -> str:
        return f"Instruction(#{self.line_id}: {self.raw_text})"


@dataclass
class BasicBlock:
    id: int
    instructions: List[Instruction] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)
    predecessors: List[int] = field(default_factory=list)

    def block_use(self) -> Set[str]:
        
        use = set()
        defined_so_far = set()
        for instr in self.instructions:
            for var in instr.used_variables():
                if var not in defined_so_far:
                    use.add(var)
            defined_so_far.add(instr.defined_variable())
        return use

    def block_def(self) -> Set[str]:


        return {instr.defined_variable() for instr in self.instructions}

    def __repr__(self) -> str:
        return f"BasicBlock(id={self.id}, successors={self.successors}, predecessors={self.predecessors})"


@dataclass
class CFG:
    blocks: Dict[int, BasicBlock]
    block_order: List[int]  

    def get(self, block_id: int) -> BasicBlock:
        return self.blocks[block_id]

    def all_blocks(self):

        for bid in self.block_order:
            yield self.blocks[bid]

    def all_instructions(self):
        for block in self.all_blocks():
            for instr in block.instructions:
                yield instr
