"""Command-line entry point: evaluate an expression, optionally with variables."""

from __future__ import annotations

import argparse
import sys

from expreval import __version__, evaluate
from expreval.tokenizer import ExprError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="expreval", description="Evaluate a mathematical expression.")
    parser.add_argument("expression", help="the expression, e.g. '2 + 3 * sqrt(16)'")
    parser.add_argument(
        "-s", "--set", action="append", default=[], metavar="NAME=VALUE", help="bind a variable (repeatable)"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    variables: dict[str, float] = {}
    for binding in args.set:
        name, sep, value = binding.partition("=")
        if not sep:
            print(f"expreval: expected NAME=VALUE, got {binding!r}", file=sys.stderr)
            return 2
        try:
            variables[name.strip()] = float(value)
        except ValueError:
            print(f"expreval: {value!r} is not a number", file=sys.stderr)
            return 2

    try:
        result = evaluate(args.expression, variables)
    except ExprError as exc:
        print(f"expreval: {exc}", file=sys.stderr)
        return 1

    # Print integers without a trailing ".0".
    print(int(result) if result == int(result) and abs(result) < 1e15 else result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
