import sys
from typing import Dict, NoReturn
from . import entities as e


index: Dict[str, e.Function] = {}

def _register(name):
    def _(f):
        index[name] = f
        return f
    return _

@_register("+")
@e.Function.make("+")
def _(runtime: e.Runtime, a: e.Integer, b: e.Integer) -> e.Integer:
    return e.Integer(a.n + b.n)


@_register("*")
@e.Function.make("*")
def _(runtime: e.Runtime, a: e.Integer, b: e.Integer) -> e.Integer:
    return e.Integer(a.n * b.n)


@_register("-")
@e.Function.make("-")
def _(runtime: e.Runtime, a: e.Integer, b: e.Integer) -> e.Integer:
    return e.Integer(a.n - b.n)


@_register("neg")
@e.Function.make("neg")
def _(runtime: e.Runtime, a: e.Integer) -> e.Integer:
    return e.Integer(-a.n)


@_register("**")
@e.Function.make("**")
def _(runtime: e.Runtime, a: e.Integer, b: e.Integer) -> e.Integer:
    return e.Integer(a.n ** b.n)


@_register("join")
@e.Function.make("join")
def _(runtime: e.Runtime, *strings: e.String) -> e.String:
    return e.String("".join(s.s for s in strings))


@_register("bool")
@e.Function.make("bool")
def _(runtime: e.Runtime, x: e.Entity) -> e.Atom:
    if x == e.String(""):
        return e.Atom("False")
    elif x == e.Integer(0):
        return e.Atom("False")
    elif x == e.Vector():
        return e.Atom("False")
    else:
        return e.Atom("True")


@_register("print!")
@e.Function.make("print!")
def _(runtime: e.Runtime, x: e.Entity) -> e.Atom:
    print(x)
    return e.Atom("Nil")


@_register("quit!")
@e.Function.make("quit!")
def _(runtime: e.Runtime, status: e.Integer = e.Integer(0)) -> NoReturn:
    print("Bye for now!")
    sys.exit(status.n)


@_register("define")
@e.Function.make("define", lazy=True)
def _(runtime: e.Runtime, name: e.Quoted[e.Name], value: e.Quoted[e.Entity]) -> e.Atom:
    runtime.global_frame.insert(name.e.identifier, value.e.evaluate(runtime))
    return e.Atom("Nil")


@_register("fun")
@e.Function.make("fun", lazy=True)
def _(
        runtime: e.Runtime,
        arg_names: e.Quoted[e.Vector[e.Name]],
        body: e.Quoted[e.Entity]
    ) -> e.Function:
    return e.create_function(
        outer_runtime=runtime,
        name="~fun~",
        arg_names=[name.identifier for name in arg_names.e.es],
        body=body.e
    )


@_register("defun")
@e.Function.make("defun", lazy=True)
def _(
        runtime: e.Runtime,
        name: e.Quoted[e.Name],
        arg_names: e.Quoted[e.Vector[e.Name]],
        body: e.Quoted[e.Entity]
    ) -> e.Entity:
    fun = e.SExpr(e.Name("fun"), arg_names.e, body.e).evaluate(runtime)
    assert isinstance(fun, e.Function)
    named_fun = fun.with_name(name.e.identifier)
    return e.SExpr(e.Name("define"), name.e, named_fun)


@_register("if")
@e.Function.make("if", lazy=True)
def _(runtime: e.Runtime, qcond: e.Quoted, then: e.Quoted, else_: e.Quoted) -> e.Entity:
    condition = e.SExpr(e.Name("bool"), qcond.e).evaluate(runtime)
    if condition == e.Atom("True"):
        return then.e.evaluate(runtime)
    else:
        return else_.e.evaluate(runtime)


@_register("loop")
@e.Function.make("loop")
def _(runtime: e.Runtime, initial: e.Vector, fn: e.Function) -> e.Entity:
    acc = initial.es
    while True:
        result = fn.call(runtime, *acc)
        if not isinstance(result, e.Vector):
            raise TypeError(f"Expected vector, got {result}")
        if len(result.es) == 0:
            raise ValueError(f"Expected non-zero vector")
        status, *acc = result.es
        if status not in (e.Atom("return"), e.Atom("next")):
            raise TypeError(f"Expected :next/:return, got {status}")
        if status == e.Atom("return"):
            if len(acc) != 1:
                raise TypeError(f"Expected one argument after :return, got {len(acc)}")
            return acc[0]
