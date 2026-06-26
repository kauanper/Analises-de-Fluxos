import sys
import os
from modules.core.core import parse_input, print_result

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.reaching_definitions.reaching_definitions import run_reaching_definitions

def main():
    example_input = [
        "1 2",
        "a = a+c",
        "b = 4-a",
        "2",
        "2 1",
        "b = 20*c",
        "3",
        "3 2",
        "d = a+b",
        "b = 0",
        "0"
    ]

    if len(sys.argv) > 1:
        cfg = parse_input(sys.argv[1])
    else:
        cfg = parse_input(example_input)

    result = run_reaching_definitions(cfg)

    print_result("Reaching Definitions", result, cfg.block_order)

if __name__ == "__main__":
    main()