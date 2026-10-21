"""expreval: a safe arithmetic expression evaluator.

Evaluates mathematical expressions from a string without ``eval``: a tokenizer feeds a
shunting-yard parser, and the resulting postfix is evaluated. Supports the usual operators,
parentheses, variables, constants and a set of built-in functions.
"""

from expreval.evaluator import Evaluator, ExprError, evaluate

__version__ = "0.1.0"
__all__ = ["evaluate", "Evaluator", "ExprError"]
