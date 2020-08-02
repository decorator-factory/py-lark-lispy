import pytest
from pylarklispy.entities import *

def test_name():
    runtime = Runtime({"pi": Integer(31415926)})
    expr = Name("pi")
    assert expr.evaluate(runtime) == Integer(31415926)


def test_name_not_found():
    runtime = Runtime({"pi": Integer(31415926)})
    expr = Name("e")
    with pytest.raises(KeyError):
        expr.evaluate(runtime)


def test_builtin_function():
    runtime = Runtime({})
    add = Function("+", (lambda r, a, b: Integer(a.n + b.n)))
    expr = SExpr(add, Integer(1), Integer(2))
    assert expr.evaluate(runtime) == Integer(3)


def test_builtin_function2():
    add = Function("+", (lambda r, a, b: Integer(a.n + b.n)))
    runtime = Runtime({"+": add})
    expr = SExpr(Name("+"), Integer(1), Integer(2))
    assert expr.evaluate(runtime) == Integer(3)


def test_builtin_function3():
    add = Function("+", (lambda r, a, b: Integer(a.n + b.n)))
    runtime = Runtime({"+": add, "one": Integer(1), "two": Integer(2)})
    expr = SExpr(Name("+"), Name("one"), Name("two"))
    assert expr.evaluate(runtime) == Integer(3)
