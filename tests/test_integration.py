import pytest
from pylarklispy import compile_and_run
from pylarklispy import entities as e


def result(code: str):
    """Evaluate zero or more expressions from a stringly piece of code"""
    expr, _ = compile_and_run(code)
    return expr


def test_arithmetics():
    expr = result("""
        (define x (+ 31 10 1))   # x = 31 + 10 + 1 = 42
        (define y (* x 2 5))   # y = 42 * 10 = 420
        (define z (- y (+ x 4))) # z = y - (x + 4) = 420 - 46 = 374
        (define w (+ z -372)) # w = z + (-372) = 2
        (define h (neg (** w 5))) # h = -(w**5) = -(2**5) = -32
        h
    """)
    assert expr == e.Integer(-32)


def test_custom_identity_function():
    expr = result("""
        (defun id [x] x)
        (id :hello!)
    """)
    assert expr == e.Atom("hello!")


def test_if():
    expr = result("""
        [(if 1 :one :not-one)
         (if 0 :zero :not-zero)]
    """)
    assert expr == e.Vector(e.Atom("one"), e.Atom("not-zero"))


def test_bool():
    expr = result("""
        [(bool ""), (bool 0), (bool []), (bool :False), (bool :Nil)]
    """)
    assert isinstance(expr, e.Vector)
    assert all([x == e.Atom("False") for x in expr.es])


def test_sigils():
    expr = result("""
        (defun sigil<!> [s] (join "!!!" s "!!!"))
        ~!"attention"
    """)
    assert expr == e.String("!!!attention!!!")


def test_loop():
    expr = result("""
        (defun factorial [n]
            (loop [1 n]
                (fun [acc x]
                    (if x
                        [:next   (* acc x) (- x 1)]
                        [:return acc]))))

        (factorial 10)
    """)
    assert expr == e.Integer(1 * 2 * 3 * 4 * 5 * 6 * 7 * 8 * 9 * 10)