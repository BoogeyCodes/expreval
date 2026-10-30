from __future__ import annotations

import math

import pytest

from expreval import Evaluator, ExprError, evaluate


class TestArithmetic:
    def test_basic_precedence(self):
        assert evaluate("1 + 2 * 3") == 7
        assert evaluate("(1 + 2) * 3") == 9
        assert evaluate("10 / 4") == 2.5
        assert evaluate("10 % 3") == 1

    def test_exponentiation_is_right_associative(self):
        assert evaluate("2 ^ 3 ^ 2") == 512  # 2^(3^2)

    def test_unary_minus_binds_looser_than_power(self):
        assert evaluate("-2 ^ 2") == -4  # -(2^2)
        assert evaluate("2 ^ -2") == 0.25
        assert evaluate("-3 + 5") == 2
        assert evaluate("--5") == 5

    def test_scientific_notation(self):
        assert evaluate("1.5e3") == 1500
        assert evaluate("2e-2") == 0.02


class TestFunctionsAndConstants:
    def test_constants(self):
        assert evaluate("pi") == math.pi
        assert evaluate("2 * pi") == 2 * math.pi

    def test_single_arg_functions(self):
        assert evaluate("sqrt(16)") == 4
        assert evaluate("abs(-7)") == 7
        assert evaluate("floor(3.9)") == 3
        assert evaluate("ceil(3.1)") == 4

    def test_variadic_functions(self):
        assert evaluate("max(3, 7, 2)") == 7
        assert evaluate("min(3, 7, 2)") == 2
        assert evaluate("sum(1, 2, 3, 4)") == 10

    def test_optional_second_argument(self):
        assert evaluate("log(8, 2)") == pytest.approx(3)
        assert evaluate("round(3.14159, 2)") == 3.14

    def test_nested_calls(self):
        assert evaluate("sqrt(sum(9, 16))") == 5
        assert evaluate("max(abs(-10), sqrt(81))") == 10


class TestVariables:
    def test_variables_via_mapping_and_kwargs(self):
        assert evaluate("x * 2 + y", {"x": 5, "y": 1}) == 11
        assert Evaluator({"r": 2}).evaluate("pi * r ^ 2") == pytest.approx(math.pi * 4)

    def test_reuses_an_evaluator_with_different_values(self):
        ev = Evaluator()
        assert ev.evaluate("a + b", a=1, b=2) == 3
        assert ev.evaluate("a + b", a=10, b=20) == 30


class TestErrors:
    @pytest.mark.parametrize("expr", ["1 +", "(1 + 2", "1 + 2)", "2 ** 3", "max()", "sqrt(1, 2)", "1 2"])
    def test_malformed_expressions_raise(self, expr: str):
        with pytest.raises(ExprError):
            evaluate(expr)

    def test_division_and_modulo_by_zero(self):
        with pytest.raises(ExprError):
            evaluate("1 / 0")
        with pytest.raises(ExprError):
            evaluate("5 % 0")

    def test_unknown_names(self):
        with pytest.raises(ExprError):
            evaluate("nope")
        with pytest.raises(ExprError):
            evaluate("bogus(1)")

    def test_domain_error_is_wrapped(self):
        with pytest.raises(ExprError):
            evaluate("sqrt(-1)")
