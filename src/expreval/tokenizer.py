"""Turn an expression string into a stream of tokens."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class ExprError(ValueError):
    """Raised for any tokenizing, parsing or evaluation error."""


class TokenType(Enum):
    NUMBER = auto()
    IDENT = auto()
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    pos: int


_OPERATORS = set("+-*/%^")


def tokenize(expression: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(expression)

    while i < n:
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit() or (ch == "." and i + 1 < n and expression[i + 1].isdigit()):
            start = i
            seen_dot = False
            while i < n and (expression[i].isdigit() or expression[i] == "."):
                if expression[i] == ".":
                    if seen_dot:
                        raise ExprError(f"malformed number at position {start}")
                    seen_dot = True
                i += 1
            # Scientific notation, e.g. 1.5e-3.
            if i < n and expression[i] in "eE":
                i += 1
                if i < n and expression[i] in "+-":
                    i += 1
                if i >= n or not expression[i].isdigit():
                    raise ExprError(f"malformed exponent at position {start}")
                while i < n and expression[i].isdigit():
                    i += 1
            tokens.append(Token(TokenType.NUMBER, expression[start:i], start))
            continue

        if ch.isalpha() or ch == "_":
            start = i
            while i < n and (expression[i].isalnum() or expression[i] == "_"):
                i += 1
            tokens.append(Token(TokenType.IDENT, expression[start:i], start))
            continue

        if ch in _OPERATORS:
            tokens.append(Token(TokenType.OPERATOR, ch, i))
        elif ch == "(":
            tokens.append(Token(TokenType.LPAREN, ch, i))
        elif ch == ")":
            tokens.append(Token(TokenType.RPAREN, ch, i))
        elif ch == ",":
            tokens.append(Token(TokenType.COMMA, ch, i))
        else:
            raise ExprError(f"unexpected character {ch!r} at position {i}")
        i += 1

    return tokens
