# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Built-in functions: `sign`, `cbrt` (cube root, defined for negatives), `clamp(x, lo, hi)`,
  `degrees`, `radians`, and the variadic `avg`.

## [0.1.0]

### Added
- Safe arithmetic evaluator (tokenizer + shunting-yard + postfix), no `eval`.
- Operators, unary minus, functions, constants and variables; a CLI.
