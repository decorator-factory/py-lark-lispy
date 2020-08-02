from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Literal

from typing_extensions import runtime

"""
This module contains the classes that represent all the language
entities like S-Expr, Integer etc.

An entity is an internal representation of a value or a computation.
"""

EvaluationStatus = Tuple[Literal["full", "partial"], "Entity"]


class StackFrame:
    __slots__ = ("parent", "depth", "caller", "names")

    def __init__(self, parent: Optional["StackFrame"], depth: int, caller: str, names: Dict[str, "Entity"]):
        self.parent = parent
        self.depth = depth
        self.caller = caller
        self.names = names

    def lookup(self, name: str, *, trace: Tuple["StackFrame", ...] = ()):
        if name in self.names:
            return self.names[name]
        if self.parent is None:
            raise KeyError(name, trace)
        return self.parent.lookup(name, trace=trace + (self,))

    def insert(self, name: str, value: "Entity", *, depth: int = 0):
        if depth < 0:
            raise LookupError(f"depth ({depth}) cannot be negative")
        if depth == 0:
            self.names[name] = value
        if self.parent is None:
            raise LookupError("Cannot go further; already in global scope")
        self.parent.insert(name, value, depth=depth-1)


class Runtime:
    def __init__(self, built_ins: Mapping[str, "Entity"]):
        self.global_names = dict(built_ins)
        self.global_frame = StackFrame(
            parent=None,
            depth=0,
            caller="<global>",
            names=self.global_names
        )
        self.stack = [self.global_frame]

    @property
    def current_frame(self):
        return self.stack[-1]

    def __getitem__(self, name: str) -> "Entity":
        return self.stack[-1].lookup(name)

    def push(self, frame: StackFrame):
        self.stack.append(frame)

    def pop(self):
        if len(self.stack) == 1:
            raise LookupError("Popping the global stack frame")
        return self.stack.pop()


class Entity:
    @property
    def is_threadsafe(self):
        """An entity is threadsafe if its `compute` method does not
        depend on the runtime
        """
        return True

    def fmap(self, f: Callable[["Entity"], "Entity"]) -> "Entity":
        return f(self)

    def call(self, runtime: Runtime, *args: "Entity") -> "Entity":
        raise TypeError(f"Cannot call {self!r}")

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
    __slots__ = ("n",)

    def __init__(self, n: int):
        self.n = n

    def __eq__(self, other):
        if not isinstance(other, Integer):
            return False
        return self.n == other.n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"<Int {self.n}>"


class String(Entity):
    __slots__ = ("s",)

    def __init__(self, s: str):
        self.s = s

    def __eq__(self, other):
        if not isinstance(other, String):
            return False
        return self.s == other.s

    def __str__(self):
        return repr(self.s)

    def __repr__(self):
        return f"<String {self.s!r}>"


class Atom(Entity):
    __slots__ = ("s",)

    def __init__(self, s: str):
        self.s = s

    def __eq__(self, other):
        if not isinstance(other, Atom):
            return False
        return self.s == other.s

    def __str__(self):
        return f":{self.s}"

    def __repr__(self):
        return f"<Atom :{self.s}>"


class Quoted(Entity):
    __slots__ = ("e",)

    def __init__(self, e: Entity):
        self.e = e

    def fmap(self, f):
        return Quoted(self.e.fmap(f))

    def __eq__(self, other):
        if not isinstance(other, Quoted):
            return False
        return self.e == other.e

    def __str__(self):
        return f"&{self.e}"

    def __repr__(self):
        return f"<Quoted {self.e!r}>"


class SExpr(Entity):
    __slots__ = ("es",)

    is_threadsafe = False

    def __init__(self, *es: Entity):
        self.es = es

    def fmap(self, f):
        return SExpr(*(e.fmap(f) for e in self.es))

    def __eq__(self, other):
        if not isinstance(other, SExpr):
            return False
        return self.es == other.es

    def compute(self, runtime: Runtime) -> Entity:
        return self.es[0].evaluate(runtime).call(runtime, *self.es[1:])

    def __str__(self):
        return "(" + " ".join(map(str, self.es)) + ")"

    def __repr__(self):
        return f"<SExpr {self.es}>"


class Vector(Entity):
    __slots__ = ("es", "_computed")

    def __init__(self, *es: Entity, _computed: int = 0):
        self.es = es
        self._computed = _computed

    def fmap(self, f):
        return Vector(*(e.fmap(f) for e in self.es), _computed=0)

    @property
    def is_threadsafe(self):
        return all(e.is_threadsafe for e in self.es)

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.es == other.es

    def compute(self, runtime: Runtime) -> "Vector":
        if self._computed == len(self.es):
            return self
        # compute a new iteration
        new_es = []
        computed = 0
        for e in self.es:
            next_e = e.compute(runtime)
            if next_e is e:
                computed += 1
            new_es.append(next_e)
        return Vector(*new_es, _computed=computed)

    def evaluate(self, runtime: Runtime) -> "Vector":
        # if we just want the result, there's no need
        # to do a billion `compute`s
        return Vector(
            *(e.compute(runtime) for e in self.es),
            _computed=len(self.es)
        )

    def __str__(self):
        return "[" + " ".join(map(str, self.es)) + "]"

    def __repr__(self):
        return f"<Vector {self.es}>"


class Name(Entity):
    __slots__ = ("identifier",)

    is_threadsafe = False

    def __init__(self, identifier: str):
        self.identifier = identifier

    def __eq__(self, other):
        if not isinstance(other, Name):
            return False
        return self.identifier == other.identifier

    def compute(self, runtime: Runtime) -> Entity:
        return runtime[self.identifier]

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return "<Name {self.identifier}>"


class SigilString(Entity):
    __slots__ = ("sigil", "string")

    is_threadsafe = False

    def __init__(self, sigil: str, string: str):
        self.sigil = sigil
        self.string = string

    def __eq__(self, other):
        if not isinstance(other, SigilString):
            return False
        return (self.sigil, self.string) == (other.sigil, other.string)

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


class Function(Entity):
    __slots__ = ("name", "fn", "closure", "lazy")

    def __init__(
        self,
        name: str,
        fn: Callable[..., Entity], # Runtime, *Entity -> Entity
        closure: Optional[StackFrame] = None,
        lazy: bool = False
    ):
        self.name = name
        self.fn = fn
        self.closure = closure
        self.lazy = lazy

    def with_name(self, name):
        return Function(name, self.fn, self.closure)

    def call(self, runtime: Runtime, *args: Entity) -> Entity:
        if self.lazy:
            computed_args = [Quoted(arg) for arg in args]
        else:
            computed_args = [arg.compute(runtime) for arg in args]

        if self.closure is not None:
            runtime.push(self.closure)
        try:
            return self.fn(runtime, *computed_args).evaluate(runtime)
        finally:
            if self.closure is not None:
                runtime.pop()

    def __str__(self):
        return f"<fun({self.name})[{self.fn}]>"

    def __repr__(self):
        return f"<Function {self.name} {self.fn} {self.closure}>"


def create_function(outer_runtime: Runtime, name: str, arg_names: Sequence[str], body: Entity, lazy: bool = False):
    """Create a new user-defined function and attaches
    a proper closure to it
    """
    def fun(runtime: Runtime, *args: Entity) -> Entity:
        nonlocal caller
        if len(args) != len(arg_names):
            raise ValueError(f"Got {len(args)} args, exprected {len(arg_names)}")
        local_frame = StackFrame(
            parent=runtime.current_frame,
            depth=runtime.current_frame.depth + 1,
            caller=repr(caller),
            names=dict(zip(arg_names, args))
        )
        runtime.push(local_frame)
        try:
            return body.evaluate(runtime)
        finally:
            runtime.pop()
    caller = Function(name, fun, closure=outer_runtime.current_frame, lazy=lazy)
    return caller
