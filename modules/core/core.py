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


# Parser
def _parse_instruction_line(line: str, line_id: int) -> Instruction:
    raw_text = line.strip()
    destination, expression = raw_text.split("=", 1)
    destination = destination.strip()
    expression = expression.strip()

    for op in ["+", "-", "*", "/"]:
        idx = expression.find(op, 1) 
        if idx != -1:
            return Instruction(
                line_id=line_id,
                destination=destination,
                operand1=expression[:idx].strip(),
                operator=op,
                operand2=expression[idx + 1:].strip(),
                raw_text=raw_text,
            )

    return Instruction(
        line_id=line_id,
        destination=destination,
        operand1=expression,
        operator=None,
        operand2=None,
        raw_text=raw_text,
    )


def parse_input(source: Union[str, List[str]]) -> CFG:
    
    if isinstance(source, str):
        with open(source, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    else:
        raw_lines = list(source)

    lines = [l.strip() for l in raw_lines if l.strip() != ""]
    if not lines:
        raise ValueError("Entrada vazia.")

    blocks: Dict[int, BasicBlock] = {}
    block_order: List[int] = []
    global_line_counter = 0
    i = 0

    while i < len(lines):
        
        header = lines[i].split()
        
        if len(header) != 2:
            raise ValueError(f"Cabecalho invalido na linha {i}: '{lines[i]}'")
        block_id, num_instructions = int(header[0]), int(header[1])
        
        i += 1

        instructions: List[Instruction] = []
        for _ in range(num_instructions):
            if i >= len(lines):
                raise ValueError(f"Entrada truncada no bloco {block_id}.")
            global_line_counter += 1
            instructions.append(_parse_instruction_line(lines[i], global_line_counter))
            i += 1

        if i >= len(lines):
            raise ValueError(f"Faltou a linha de sucessores do bloco {block_id}.")
        successors = [int(s) for s in lines[i].split() if int(s) != 0]
        
        i += 1

        if block_id in blocks:
            raise ValueError(f"Bloco {block_id} definido mais de uma vez.")

        blocks[block_id] = BasicBlock(id=block_id, instructions=instructions, successors=successors)
        block_order.append(block_id)

    for block in blocks.values():
        for successor_id in block.successors:
            if successor_id not in blocks:
                raise ValueError(f"Bloco {block.id} aponta para sucessor {successor_id} inexistente.")
            blocks[successor_id].predecessors.append(block.id)

    return CFG(blocks=blocks, block_order=block_order)


# Funcoes de juncao
def union(sets_list: List[Set]) -> Set:


    result = set()
    for s in sets_list:
        result |= s
    return result


def intersection(sets_list: List[Set]) -> Set:
   
    if not sets_list:
        return set()
    result = sets_list[0].copy()
    for s in sets_list[1:]:
        result &= s
    return result

# Motor generico de fluxo de dados
def run_dataflow(
    cfg: CFG,
    direction: str,
    join: Callable[[List[Set]], Set],
    gen_func: Callable[[BasicBlock], Set],
    kill_func: Callable[[BasicBlock], Set],
) -> Dict[int, Tuple[Set, Set]]:
    
    if direction not in ("forward", "backward"):
        raise ValueError("direction deve ser 'forward' ou 'backward'")

    IN: Dict[int, Set] = {bid: set() for bid in cfg.blocks}
    OUT: Dict[int, Set] = {bid: set() for bid in cfg.blocks}

    changed = True
    while changed:
        changed = False
        for block in cfg.all_blocks():
            gen = gen_func(block)
            kill = kill_func(block)

            if direction == "forward":
                new_in = join([OUT[p] for p in block.predecessors])
                new_out = gen | (new_in - kill)
            else:
                new_out = join([IN[s] for s in block.successors])
                new_in = gen | (new_out - kill)

            if new_in != IN[block.id] or new_out != OUT[block.id]:
                changed = True
            IN[block.id] = new_in
            OUT[block.id] = new_out

    return {bid: (IN[bid], OUT[bid]) for bid in cfg.blocks}
