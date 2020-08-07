import importlib.util
import importlib
from os.path import realpath
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
def _(runtime: e.Runtime, *args: e.Integer) -> e.Integer:
    return e.Integer(sum(arg.n for arg in args))


@_register("*")
@e.Function.make("*")
def _(runtime: e.Runtime, *args: e.Integer) -> e.Integer:
    product = 1
    for arg in args:
        product *= arg.n
    return e.Integer(product)


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
    elif x in [e.Atom("False"), e.Atom("Nil")]:
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


@_register("<")
@e.Function.make("<")
def _(runtime: e.Runtime, a: e.Integer, b: e.Integer) -> e.Atom:
    if a.n < b.n:
        return e.Atom("True")
    else:
        return e.Atom("False")


@_register(">")
@e.Function.make(">")
def _(runtime: e.Runtime, a: e.Integer, b: e.Integer) -> e.Atom:
    if a.n > b.n:
        return e.Atom("True")
    else:
        return e.Atom("False")


@_register("=")
@e.Function.make("=")
def _(runtime: e.Runtime, a: e.Entity, b: e.Entity) -> e.Atom:
    if a == b:
        return e.Atom("True")
    else:
        return e.Atom("False")


@_register("/=")
@e.Function.make("/=")
def _(runtime: e.Runtime, a: e.Entity, b: e.Entity) -> e.Atom:
    if a != b:
        return e.Atom("True")
    else:
        return e.Atom("False")


@_register(">=")
@e.Function.make(">=")
def _(runtime: e.Runtime, a: e.Entity, b: e.Entity):
    return e.SExpr(e.Name("or"),
            e.SExpr(e.Name(">"), a, b),
            e.SExpr(e.Name("="), a, b))


@_register("<=")
@e.Function.make("<=")
def _(runtime: e.Runtime, a: e.Entity, b: e.Entity):
    return e.SExpr(e.Name("or"),
            e.SExpr(e.Name("<"), a, b),
            e.SExpr(e.Name("="), a, b))


@_register("not")
@e.Function.make("not")
def _(runtime: e.Runtime, x: e.Entity):
    return e.SExpr(e.Name("if"), x, e.Atom("False"), e.Atom("True"))


@_register("and")
@e.Function.make("and", lazy=True)
def _(runtime: e.Runtime, *qxs: e.Quoted[e.Entity]):
    for qx in qxs:
        cond = e.SExpr(e.Name("bool"), qx.e).evaluate(runtime)
        if cond == e.Atom("False"):
            return cond
    return e.Atom("True")


@_register("or")
@e.Function.make("or", lazy=True)
def _(runtime: e.Runtime, *qxs: e.Quoted[e.Entity]):
    for qx in qxs:
        cond = e.SExpr(e.Name("bool"), qx.e).evaluate(runtime)
        if cond == e.Atom("True"):
            return cond
    return e.Atom("False")


@_register("interop")
@e.Function.make("interop")
def _(runtime: e.Runtime, module_name: e.String, path: e.String = e.String("")) -> e.Vector:
    if path.s == "":
        module = importlib.import_module(module_name.s)
    else:
        spec = importlib.util.spec_from_file_location(module_name.s, path.s)
        module = importlib.util.module_from_spec(spec)

    if not hasattr(module, "interop"):
        raise LookupError(f"module {module} doesn't define `interop`")

    module_dict: Dict[str, e.Entity] = module.interop(runtime) # type: ignore
    vector_guts = []
    for k, v in module_dict.items():
        vector_guts += (e.Atom(k), v)

    return e.Vector(*vector_guts)


@_register("+=")
@e.Function.make("+=")
def _(runtime: e.Runtime, target: e.Vector, source: e.Vector) -> e.Vector:
    es = []
    used_keys = []
    for (k, v) in target.pairs():
        for (k2, v2) in source.pairs():
            if k2 == k:
                es += (k2, v2)
                used_keys.append(k2)
                break
        else:
            es += (k, v)
    for (k2, v2) in source.pairs():
        if k2 not in used_keys:
            es += (k2, v2)
    return e.Vector(*es, _computed=len(es))


@_register("-=")
@e.Function.make("-=")
def _(runtime: e.Runtime, target: e.Vector, keys: e.Vector) -> e.Vector:
    es = []
    for (k, v) in target.pairs():
        for k2 in keys.es:
            if k2 == k:
                break
        else:
            es += (k, v)
    return e.Vector(*es, _computed=len(es))


@_register("at")
@e.Function.make("at")
def _(runtime: e.Runtime, vector: e.Vector, index: e.Integer):
    if index.n >= len(vector.es):
        raise ValueError(f"Index {index} too large for {vector}")
    return vector.es[index.n]


@_register("slice")
@e.Function.make("slice")
def _(runtime: e.Runtime, vector: e.Vector, a: e.Integer, b: e.Integer, c: e.Integer=e.Integer(1)):
    return e.Vector(*vector.es[a.n:b.n:c.n])


@_register("slice=")
@e.Function.make("slice=")
def _(runtime: e.Runtime, vector: e.Vector, a: e.Integer, b: e.Integer, source: e.Vector):
    es = list(vector.es)
    es[a.n:b.n] = source.es
    return e.Vector(*es)