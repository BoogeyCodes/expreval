"""Built-in constants and functions available to expressions."""

from __future__ import annotations

import math
from collections.abc import Callable

CONSTANTS: dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
}

# Each entry maps a name to (implementation, arity). Arity ``-1`` means variadic (one or more args).
FUNCTIONS: dict[str, tuple[Callable[..., float], int]] = {
    "abs": (abs, 1),
    "ceil": (math.ceil, 1),
    "floor": (math.floor, 1),
    "round": (lambda x, ndigits=0: round(x, int(ndigits)), 1),
    "sqrt": (math.sqrt, 1),
    "exp": (math.exp, 1),
    "log": (math.log, 1),   # natural log; log(x, base) also allowed via variadic handling below
    "log2": (math.log2, 1),
    "log10": (math.log10, 1),
    "sin": (math.sin, 1),
    "cos": (math.cos, 1),
    "tan": (math.tan, 1),
    "asin": (math.asin, 1),
    "acos": (math.acos, 1),
    "atan": (math.atan, 1),
    "atan2": (math.atan2, 2),
    "hypot": (math.hypot, 2),
    "pow": (math.pow, 2),
    "min": (min, -1),
    "max": (max, -1),
    "sum": (lambda *xs: math.fsum(xs), -1),
    "avg": (lambda *xs: math.fsum(xs) / len(xs), -1),
    "gcd": (math.gcd, -1),
    "sign": (lambda x: float((x > 0) - (x < 0)), 1),
    "cbrt": (lambda x: math.copysign(abs(x) ** (1 / 3), x), 1),  # cube root, defined for negatives
    "clamp": (lambda x, lo, hi: max(lo, min(hi, x)), 3),
    "degrees": (math.degrees, 1),
    "radians": (math.radians, 1),
}

# A few functions accept an optional extra argument; list their allowed arities here.
VARIADIC_ARITIES: dict[str, set[int]] = {
    "log": {1, 2},
    "round": {1, 2},
}
