from typing import Callable, Mapping
"""
This module contains the classes that represent all the language
entities like S-Expr, Integer etc.
"""


Runtime = Mapping[str, "Entity"]


class Entity:
    def fmap(self, f: Callable[["Entity"], "Entity"]) -> "Entity":
        return self

    def compute(self, runtime: Runtime) -> "Entity":
        return self

    def evaluate(self, runtime: Runtime) -> "Entity":
        state = self
        while True:
            # compute until the entity is final
            next_state = state.compute(runtime)
            if next_state is state:
                return state
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
        return str(self.s)

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
