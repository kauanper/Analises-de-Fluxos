import sys

from modules.available_expressions.available_expressions import (
    run_available_expressions,
)
from modules.core.core import parse_input, print_result


def main():
    example_input = [
        "1 2",
        "t1 = a+b",
        "t2 = c+d",
        "2 3",
        "2 2",
        "x = a+b",
        "c = 5",
        "4",
        "3 2",
        "y = a+b",
        "z = e+f",
        "5",
        "4 2",
        "k = g+h",
        "m = c+d",
        "6",
        "5 2",
        "g = 10",
        "n = c+d",
        "6",
        "6 2",
        "p = a+b",
        "q = g+h",
        "0",
    ]

    expected = {
        1: (
            set(),
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
            },
        ),

        2: (
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
            },
            {
                ("a", "+", "b"),
            },
        ),

        3: (
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
            },
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
                ("e", "+", "f"),
            },
        ),

        4: (
            {
                ("a", "+", "b"),
            },
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
                ("g", "+", "h"),
            },
        ),

        5: (
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
                ("e", "+", "f"),
            },
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
                ("e", "+", "f"),
            },
        ),

        6: (
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
            },
            {
                ("a", "+", "b"),
                ("c", "+", "d"),
                ("g", "+", "h"),
            },
        ),
    }

    if len(sys.argv) > 1:
        cfg = parse_input(sys.argv[1])
    else:
        cfg = parse_input(example_input)

    result = run_available_expressions(cfg)

    if len(sys.argv) == 1:
        assert result[1] == expected[1], result[1]
        assert result[2] == expected[2], result[2]
        assert result[3] == expected[3], result[3]
        assert result[4] == expected[4], result[4]
        assert result[5] == expected[5], result[5]
        assert result[6] == expected[6], result[6]

    print_result("Available Expressions", result, cfg.block_order)


if __name__ == "__main__":
    main()