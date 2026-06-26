import sys

from modules.liveness.liveness import run_liveness
from modules.core.core import parse_input, print_result


def main():
    example_input = [
        "1 2",
        "a = a+c",
        "b = 4-a",
        "2",
        "2 1",
        "b=20*c",
        "3",
        "3 2",
        "d = a+b",
        "b = 0",
        "0"
    ]

    expected = {
        1: ({"a", "c"}, {"a", "c"}),
        2: ({"a", "c"}, {"a", "b"}),
        3: ({"a", "b"}, set()),
    }

    if len(sys.argv) > 1:
        cfg = parse_input(sys.argv[1])
    else:
        cfg = parse_input(example_input)

    result = run_liveness(cfg)

    if len(sys.argv) == 1:
        assert result[1] == expected[1], result[1]
        assert result[2] == expected[2], result[2]
        assert result[3] == expected[3], result[3]

    print_result("Liveness", result, cfg.block_order)


if __name__ == "__main__":
    main()
