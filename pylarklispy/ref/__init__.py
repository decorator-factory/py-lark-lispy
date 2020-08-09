from typing import *
import pylarklispy.entities as e
from pylarklispy.entities import Entity

def interop(_runtime: e.Runtime):
    from aiohttp import web
    import asyncio

    index = {}
    index: Dict[str, e.Function] = {}
    def _register(name):
        def _(f):
            index[name] = f
            return f
        return _

    def addf(name):
        def _(f):
            entity_function = e.Function.make(name)(f)
            _register(name)(entity_function)
            return entity_function
        return _

    ####################################


    class Reference(Entity):
        def __init__(self, value: e.Entity):
            self.value: e.Entity = value

        def __repr__(self):
            return f"Reference({self.value!r})"

        def __str__(self):
            return f"(ref {self.value!s})"


    @addf("make")
    def _(r: e.Runtime, value: e.Entity):
        return Reference(value)

    @addf("set!")
    def _(r: e.Runtime, ref: Reference, value: e.Entity):
        ref.value = value
        return e.Atom("Nil")

    @addf("get!")
    def _(r: e.Runtime, ref: Reference, value: e.Entity):
        return ref.value

    @addf("change!")
    def _(r: e.Runtime, ref: Reference, callable_: e.Entity):
        new_value = callable_.call(r, ref.value)
        ref.value = new_value
        return new_value

    ###################################
    return index