"""Parse and evaluate an expression with the shunting-yard algorithm."""

from __future__ import annotations

from collections.abc import Mapping

from expreval.functions import CONSTANTS, FUNCTIONS, VARIADIC_ARITIES
from expreval.tokenizer import ExprError, Token, TokenType, tokenize

# operator -> (precedence, right_associative)
_BINARY = {
    "+": (2, False),
    "-": (2, False),
    "*": (3, False),
    "/": (3, False),
    "%": (3, False),
    "^": (4, True),
}
_UNARY_PREC = 3.5  # tighter than * and /, looser than ^, so -2^2 == -(2^2)


class Evaluator:
    """Reusable evaluator with configurable variables."""

    def __init__(self, variables: Mapping[str, float] | None = None) -> None:
        self.variables = dict(variables or {})

    def evaluate(self, expression: str, **extra: float) -> float:
        scope = {**self.variables, **extra}
        postfix = _to_postfix(tokenize(expression))
        return _eval_postfix(postfix, scope)


def evaluate(expression: str, variables: Mapping[str, float] | None = None, **extra: float) -> float:
    """Evaluate ``expression`` with optional variables. Shortcut for a one-off :class:`Evaluator`."""
    return Evaluator(variables).evaluate(expression, **extra)


# -- parsing (shunting-yard) -------------------------------------------------


def _to_postfix(tokens: list[Token]) -> list[Token]:
    output: list[Token] = []
    stack: list[Token] = []
    arg_counts: list[int] = []
    prev: Token | None = None

    def is_value_end(tok: Token | None) -> bool:
        return tok is not None and tok.type in (TokenType.NUMBER, TokenType.IDENT, TokenType.RPAREN)

    for token in tokens:
        if token.type == TokenType.NUMBER:
            output.append(token)
        elif token.type == TokenType.IDENT:
            # A function is an identifier followed by '(' — detected in the LPAREN branch.
            stack.append(token) if _is_function_name(tokens, token) else output.append(token)
        elif token.type == TokenType.OPERATOR:
            if token.value == "-" and not is_value_end(prev):
                # Unary minus: push a marker operator with higher precedence.
                stack.append(Token(TokenType.OPERATOR, "u-", token.pos))
            elif token.value == "+" and not is_value_end(prev):
                pass  # unary plus is a no-op
            else:
                prec, right = _BINARY[token.value]
                while stack and _should_pop(stack[-1], prec, right):
                    output.append(stack.pop())
                stack.append(token)
        elif token.type == TokenType.LPAREN:
            stack.append(token)
        elif token.type == TokenType.COMMA:
            while stack and stack[-1].type != TokenType.LPAREN:
                output.append(stack.pop())
            if not arg_counts:
                raise ExprError("comma outside a function call")
            arg_counts[-1] += 1
        elif token.type == TokenType.RPAREN:
            while stack and stack[-1].type != TokenType.LPAREN:
                output.append(stack.pop())
            if not stack:
                raise ExprError(f"unbalanced parenthesis at position {token.pos}")
            stack.pop()  # discard the '('
            if stack and stack[-1].type == TokenType.IDENT:
                func = stack.pop()
                count = arg_counts.pop() if arg_counts else 1
                output.append(Token(TokenType.IDENT, f"{func.value}/{count}", func.pos))
        prev = token

        if token.type == TokenType.LPAREN and _opened_a_call(stack, output):
            arg_counts.append(1)

    while stack:
        top = stack.pop()
        if top.type in (TokenType.LPAREN, TokenType.RPAREN):
            raise ExprError("unbalanced parenthesis")
        output.append(top)
    return output


def _is_function_name(tokens: list[Token], ident: Token) -> bool:
    nxt = _token_after(tokens, ident)
    return nxt is not None and nxt.type == TokenType.LPAREN


def _opened_a_call(stack: list[Token], output: list[Token]) -> bool:
    # True when the '(' just pushed follows a function identifier on the stack.
    return len(stack) >= 2 and stack[-1].type == TokenType.LPAREN and stack[-2].type == TokenType.IDENT


def _token_after(tokens: list[Token], token: Token) -> Token | None:
    for i, t in enumerate(tokens):
        if t is token:
            return tokens[i + 1] if i + 1 < len(tokens) else None
    return None


def _should_pop(top: Token, prec: int, right: bool) -> bool:
    if top.type != TokenType.OPERATOR:
        return False
    if top.value == "u-":
        return prec < _UNARY_PREC
    top_prec = _BINARY[top.value][0]
    return top_prec > prec or (top_prec == prec and not right)


# -- evaluation --------------------------------------------------------------


def _eval_postfix(postfix: list[Token], scope: Mapping[str, float]) -> float:
    stack: list[float] = []

    for token in postfix:
        if token.type == TokenType.NUMBER:
            stack.append(float(token.value))
        elif token.type == TokenType.OPERATOR:
            if token.value == "u-":
                stack.append(-_pop(stack))
            else:
                b = _pop(stack)
                a = _pop(stack)
                stack.append(_apply_binary(token.value, a, b))
        elif token.type == TokenType.IDENT:
            if "/" in token.value:
                stack.append(_apply_function(token.value, stack))
            elif token.value in scope:
                stack.append(float(scope[token.value]))
            elif token.value in CONSTANTS:
                stack.append(CONSTANTS[token.value])
            else:
                raise ExprError(f"unknown name {token.value!r}")

    if len(stack) != 1:
        raise ExprError("malformed expression")
    return stack[0]


def _apply_binary(op: str, a: float, b: float) -> float:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ExprError("division by zero")
        return a / b
    if op == "%":
        if b == 0:
            raise ExprError("modulo by zero")
        return a % b
    if op == "^":
        return a**b
    raise ExprError(f"unknown operator {op!r}")


def _apply_function(encoded: str, stack: list[float]) -> float:
    name, _, count_text = encoded.partition("/")
    count = int(count_text)
    if name not in FUNCTIONS:
        raise ExprError(f"unknown function {name!r}")

    func, arity = FUNCTIONS[name]
    allowed = VARIADIC_ARITIES.get(name)
    if allowed is not None:
        if count not in allowed:
            raise ExprError(f"{name}() got {count} argument(s)")
    elif arity == -1:
        if count < 1:
            raise ExprError(f"{name}() needs at least one argument")
    elif count != arity:
        raise ExprError(f"{name}() takes {arity} argument(s), got {count}")

    args = [_pop(stack) for _ in range(count)][::-1]
    try:
        return float(func(*args))
    except (ValueError, OverflowError, TypeError, ZeroDivisionError) as exc:
        raise ExprError(f"{name}(): {exc}") from exc


def _pop(stack: list[float]) -> float:
    if not stack:
        raise ExprError("malformed expression")
    return stack.pop()
