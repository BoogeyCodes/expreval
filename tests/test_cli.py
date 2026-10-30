from __future__ import annotations

from expreval.cli import main


def test_cli_evaluates_and_prints_integer(capsys):
    assert main(["2 + 3 * 4"]) == 0
    assert capsys.readouterr().out.strip() == "14"


def test_cli_prints_float(capsys):
    assert main(["10 / 4"]) == 0
    assert capsys.readouterr().out.strip() == "2.5"


def test_cli_binds_variables(capsys):
    assert main(["x ^ 2 + y", "-s", "x=3", "-s", "y=1"]) == 0
    assert capsys.readouterr().out.strip() == "10"


def test_cli_reports_errors(capsys):
    assert main(["1 / 0"]) == 1
    assert "expreval:" in capsys.readouterr().err


def test_cli_rejects_bad_binding(capsys):
    assert main(["x", "-s", "x"]) == 2
    assert "NAME=VALUE" in capsys.readouterr().err
