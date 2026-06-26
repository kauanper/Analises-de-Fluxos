import sys
import os
import glob
from modules.core.core import parse_input, print_result
from modules.liveness.liveness import run_liveness
from modules.reaching_definitions.reaching_definitions import run_reaching_definitions

from modules.available_expressions.available_expressions import run_available_expressions

def run_analyses_for_file(input_file):
    try:
        cfg = parse_input(input_file)
    except Exception as e:
        print(f"Erro ao analisar o arquivo '{input_file}': {e}")
        return

    print("=" * 60)
    print(f"Executando Análises para: {os.path.basename(input_file)}")
    print("=" * 60)
    print()
    
    try:
        liveness_result = run_liveness(cfg)
        print_result("Análise de Longevidade (Liveness)", liveness_result, cfg.block_order)
    except Exception as e:
        print(f"Erro ao executar Liveness: {e}\n")

    try:
        reaching_result = run_reaching_definitions(cfg)
        print_result("Reaching Definitions (Definições Alcançantes)", reaching_result, cfg.block_order)
    except Exception as e:
        print(f"Erro ao executar Reaching Definitions: {e}\n")

    try:
        available_result = run_available_expressions(cfg)
        print_result("Análise de Expressões Disponíveis (Available Expressions)", available_result, cfg.block_order)
    except Exception as e:
        print(f"Erro ao executar Available Expressions: {e}\n")
    print("\n")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_ou_diretorio> [arquivo2...]")
        print("Exemplo: python main.py examples/testes_genericos/")
        return

    targets = sys.argv[1:]
    files_to_process = []

    for target in targets:
        if os.path.isfile(target):
            files_to_process.append(target)
        elif os.path.isdir(target):
            for filepath in glob.glob(os.path.join(target, "*.txt")):
                files_to_process.append(filepath)
        else:
            print(f"Aviso: Alvo '{target}' não encontrado.")

    if not files_to_process:
        print("Nenhum arquivo válido encontrado para processar.")
        return

    files_to_process.sort()

    for f in files_to_process:
        run_analyses_for_file(f)


if __name__ == "__main__":
    main()
