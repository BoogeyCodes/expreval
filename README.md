# expreval

[![CI](https://github.com/BoogeyCodes/expreval/actions/workflows/ci.yml/badge.svg)](https://github.com/BoogeyCodes/expreval/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
![No dependencies](https://img.shields.io/badge/dependencies-none-success)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A safe arithmetic expression evaluator for Python — **without `eval`**. A tokenizer feeds a
shunting-yard parser and the result is evaluated, so it handles only maths: operators, parentheses,
functions, constants and variables.

```python
from expreval import evaluate

evaluate("2 + 3 * sqrt(16)")        # 14.0
evaluate("(1 + 2) ^ 2 % 5")         # 4.0
evaluate("pi * r ^ 2", {"r": 2})    # 12.566...
evaluate("max(3, 7, abs(-9))")      # 9.0
```

## Why

Evaluating a user-supplied formula with Python's `eval` is a security hole — it runs arbitrary code.
expreval computes the expression itself: it tokenizes the string, parses it with the shunting-yard
algorithm, and evaluates the postfix form, so the only things it can do are arithmetic and the
functions you allow. It is dependency-free and small enough to read.

## Features

- **Operators**: `+ - * / % ^`, unary minus, and parentheses, with correct precedence and
  right-associative `^`. Unary minus binds looser than `^`, so `-2^2` is `-4`.
- **Numbers** including decimals and scientific notation (`1.5e-3`).
- **Constants**: `pi`, `e`, `tau`, `inf`.
- **Functions**: `abs`, `ceil`, `floor`, `round`, `sqrt`, `exp`, `log` (natural, or `log(x, base)`),
  `log2`, `log10`, the trig family, `atan2`, `hypot`, `pow`, and the variadic `min`, `max`, `sum`,
  `gcd`.
- **Variables**, passed as a mapping or keyword arguments.
- **Clear errors**: every problem — unbalanced parentheses, unknown names, wrong argument counts,
  division by zero, a math domain error — raises `ExprError` with a message, never a bare crash.

## Usage

```python
from expreval import evaluate, Evaluator, ExprError

# one-off
evaluate("x * 2 + y", {"x": 5, "y": 1})      # 11.0

# reuse an evaluator with preset variables
calc = Evaluator({"rate": 0.2})
calc.evaluate("price * (1 + rate)", price=100)   # 120.0

# errors are explicit
try:
    evaluate("1 / 0")
except ExprError as exc:
    print(exc)   # "division by zero"
```

### CLI

```bash
expreval "2 + 3 * sqrt(16)"           # 14
expreval "x^2 + y" -s x=3 -s y=1      # 10
```

## How it works

```
  "2 + 3 * sqrt(16)"
        │ tokenize
        ▼
  tokens: 2 + 3 * sqrt ( 16 )
        │ shunting-yard (precedence, associativity, function arg counting)
        ▼
  postfix: 2 3 16 sqrt/1 * +
        │ stack evaluation
        ▼
  14.0
```

The parser tracks function argument counts so `max(1, 2, 3)` and `log(8, 2)` work, and distinguishes
unary from binary minus by what precedes it.

## Testing

```bash
pip install -e ".[dev]"
pytest
```

Twenty-six tests covering precedence and associativity, unary minus, scientific notation, constants,
single-argument, variadic and optional-argument functions, nested calls, variables, and every error
path. CI runs on Python 3.10 through 3.13.

## Project layout

```
src/expreval
├── tokenizer.py   string -> tokens
├── functions.py   constants and built-in functions
├── evaluator.py   shunting-yard parse + postfix evaluation
└── cli.py         command-line entry point
tests/             pytest suite
```

## Ideas for later

- Boolean and comparison operators.
- A pluggable function registry.
- Exact arithmetic via `decimal` or `fractions`.

## License

MIT
