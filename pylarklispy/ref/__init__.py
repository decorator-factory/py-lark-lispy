from typing import *
import pylarklispy.entities as e
from pylarklispy.entities import Entity
from ..interop_utils import Index


class Reference(Entity):
    def __init__(self, value: e.Entity):
        self.value: e.Entity = value

    def __repr__(self):
        return f"Reference({self.value!r})"

    def __str__(self):
        return f"(ref {self.value!s})"


def interop(_runtime: e.Runtime):
    index = Index()
    ####################################

    @index.add_function("make")
    def _(r: e.Runtime, value: e.Entity):
        return Reference(value)


    @index.add_function("set!")
    def _(r: e.Runtime, ref: Reference, value: e.Entity):
        ref.value = value
        return e.Atom("Nil")


    @index.add_function("get!")
    def _(r: e.Runtime, ref: Reference):
        return ref.value


    @index.add_function("change!")
    def _(r: e.Runtime, ref: Reference, callable_: e.Entity):
        new_value = callable_.call(r, ref.value).evaluate(r)
        ref.value = new_value
        return new_value

    ###################################
    return index
