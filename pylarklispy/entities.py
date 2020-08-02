from typing import Callable, Mapping, Tuple, Literal
"""
This module contains the classes that represent all the language
entities like S-Expr, Integer etc.

An entity is an internal representation of a value or a computation.
"""


Runtime = Mapping[str, "Entity"]
EvaluationStatus = Tuple[Literal["full", "partial"], "Entity"]


class Entity:
    @property
    def is_threadsafe(self):
        """An entity is threadsafe if its `compute` method does not
        depend on the runtime
        """
        return True

    def fmap(self, f: Callable[["Entity"], "Entity"]) -> "Entity":
        return self

    def compute(self, runtime: Runtime) -> "Entity":
        return self

    def evaluate(self, runtime: Runtime) -> "Entity":
        """Run `compute` an entity until it's no longer
        reducable"""
        state = self
        while True:
            # compute until the entity is final
            next_state = state.compute(runtime)
            if next_state is state:
                return state
            state = next_state

    def evaluate_while_threadsafe(self, runtime: Runtime) -> EvaluationStatus:
        """Like `evaluate`, but stops as soon as computing the next
        step is not threadsafe.

        If computataion was full, return ("full", <entity>)

        If computataion was partial, return ("partial", <entity>)
        """
        state = self
        while True:
            if not state.is_threadsafe:
                return ("partial", state)
            # compute until the entity is final
            next_state = state.compute(runtime)
            if next_state is state:
                return ("full", state)
            state = next_state


class Integer(Entity):
    def __init__(self, n: int):
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"<Int {self.n}>"


class String(Entity):
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return repr(self.s)

    def __repr__(self):
        return f"<String {self.s!r}>"


class Atom(Entity):
    def __init__(self, s: str):
        self.s = s

    def __str__(self):
        return f":{self.s}"

    def __repr__(self):
        return f"<Atom :{self.s}>"


class Quoted(Entity):
    def __init__(self, e: Entity):
        self.e = e

    def __str__(self):
        return f"&{self.e}"

    def __repr__(self):
        return f"<Quoted {self.e!r}>"


class SExpr(Entity):
    def __init__(self, *es: Entity):
        self.es = es

    is_threadsafe = False

    def compute(self, runtime: Runtime) -> Entity:
        raise NotImplementedError # TODO

    def __str__(self):
        return "(" + " ".join(map(str, self.es)) + ")"

    def __repr__(self):
        return f"<SExpr {self.es}>"


class Vector(Entity):
    def __init__(self, *es: Entity):
        self.es = es

    @property
    def is_threadsafe(self):
        return all(e.is_threadsafe for e in self.es)

    def compute(self, runtime: Runtime) -> Entity:
        raise NotImplementedError # TODO

    def __str__(self):
        return "[" + " ".join(map(str, self.es)) + "]"

    def __repr__(self):
        return f"<Vector {self.es}>"


class Name(Entity):
    is_threadsafe = False

    def __init__(self, identifier: str):
        self.identifier = identifier

    def compute(self, runtime: Runtime) -> Entity:
        return runtime[self.identifier]

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return "<Name {self.identifier}>"


class SigilString(Entity):
    def __init__(self, sigil: str, string: str):
        self.sigil = sigil
        self.string = string

    @property
    def sigil_function_name(self) -> str:
        return f"sigil<{self.sigil}>"

    def compute(self, _runtime) -> Entity:
        return SExpr(
            Name(self.sigil_function_name),
            String(self.string)
        )

    def __str__(self):
        return f"~{self.sigil}{self.string!r}"

    def __repr__(self):
        return "<Sigil {self.sigil} {self.string!r}>"