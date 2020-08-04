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


def test_custom_identity_function():
    runtime = Runtime({})
    runtime.global_names["f"] =\
        create_function(runtime, "f", ["x"], Name("x"))
    expr = SExpr(Name("f"), Integer(42))
    assert expr.evaluate(runtime) == Integer(42)


def test_namespace_containment():
    runtime = Runtime({"x": Integer(1024)})
    runtime.global_names["f"] =\
        create_function(runtime, "f", ["x"], Name("x"))
    expr = SExpr(Name("f"), Integer(42))
    assert expr.evaluate(runtime) == Integer(42)
    assert runtime.global_names["x"] == Integer(1024)


def test_custom_double_function():
    runtime = Runtime({})
    runtime.global_names["f"] =\
        create_function(runtime, "f", ["x"], SExpr(Name("+"), Name("x"), Name("x")))
    runtime.global_names["+"] =\
        Function("+", (lambda r, a, b: Integer(a.n + b.n)))
    expr = SExpr(Name("f"), Integer(21))
    assert expr.evaluate(runtime) == Integer(42)


def test_custom_double_sum_function():
    runtime = Runtime({})
    runtime.global_names["double"] =\
        create_function(runtime, "double", ["x"], SExpr(Name("+"), Name("x"), Name("x")))
    runtime.global_names["f"] =\
        create_function(runtime, "f", ["x", "y"],
            SExpr(Name("double"), SExpr(Name("+"), Name("x"), Name("y")))
        )
    runtime.global_names["+"] =\
        Function("+", (lambda r, a, b: Integer(a.n + b.n)))
    expr = SExpr(Name("f"), Integer(2), Integer(3))
    assert expr.evaluate(runtime) == Integer(10)


def test_lazy_identity_function():
    runtime = Runtime({})
    runtime.global_names["q"] =\
        create_function(runtime, "q", ["x"], Name("x"), lazy=True)
    assert SExpr(Name("q"), Integer(42)).evaluate(runtime) == Quoted(Integer(42))
    assert SExpr(Name("q"), Name("w")).evaluate(runtime) == Quoted(Name("w"))


def test_equality():
    assert Integer(100) == Integer(100)
    assert Integer(100) != Integer(101)

    assert String("hello") == String("hello")
    assert String("hello") != String("Hello")

    assert Atom("yay") == Atom("yay")
    assert Atom("world") != Atom("wORlD")

    assert Vector() == Vector()
    assert Vector(Integer(1), Integer(2)) == Vector(Integer(1), Integer(2))
    assert Vector(Integer(1), Integer(2)) != Vector(Integer(1))
    assert Vector(Integer(1), Integer(2)) != Vector(Integer(1), Integer(3))

    assert Integer(128) != String("128")


def test_atom_colon():
    with pytest.raises(ValueError):
        Atom(":you-should-not-put-a-colon-when-creating-atoms-like-this")
    Atom("do-it-like this")


def test_call_the_uncallable():
    with pytest.raises(TypeError, match=r".*[cC]an(not|n't) call.*"):
        Integer(1).call( Runtime({}) )


def test_sigil_strings_can_be_strings():
    # the ~!"..." sigil will wrap the string in !!!...!!!

    runtime = Runtime({
        "sigil<!>": Function(
            "sigil<!>",
            lambda r, string: String("!!!" + string.s + "!!!")
        )
    })

    result = SigilString("!", "attention").evaluate(runtime)

    assert result == String("!!!attention!!!")
