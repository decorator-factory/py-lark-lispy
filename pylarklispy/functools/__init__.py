from typing import *
import pylarklispy.entities as e
from ..interop_utils import Index


class LinkedList(e.Entity):
    def __init__(self, value, rest):
        self.value = value
        self.rest = rest

    def __iter__(self):
        acc = self
        while acc is not EmptyList:
            yield acc.value
            acc = acc.rest

    def __str__(self):
        if self is EmptyList:
            return "emp"
        else:
            s = f"(+> {self.value} {{}})"
            for x in self.rest:
                s = s.format(f"(+> {x} {{}})")
            s = s.format("emp")
            return s

    def __repr__(self):
        return f"LinkedList({self.value!r}, {self.rest!r})"

EmptyList = LinkedList(None, None)


def interop(_runtime: e.Runtime):
    index = Index()
    ####################################

    @index.add_function("map")
    def _(r: e.Runtime, f: e.Entity, v: e.Vector):
        return e.Vector(
            *(e.SExpr(f, x) for x in v.es)
        )


    index.add_value("emp", EmptyList)

    @index.add_function("+>")
    def _cons(r: e.Runtime, element: e.Entity, llist: LinkedList):
        if not isinstance(llist, LinkedList):
            raise TypeError(f"Cannot (+> {element} {llist})")
        return LinkedList(element, llist)

    @index.add_function("emp?")
    def _(r: e.Runtime, llist: LinkedList):
        if llist is EmptyList:
            return e.Atom("True")
        else:
            return e.Atom("False")

    @index.add_function("lhead")
    def _(r: e.Runtime, llist: LinkedList):
        if llist is EmptyList:
            return e.Atom("Nil")
        else:
            return llist.value

    @index.add_function("lrest")
    def _(r: e.Runtime, llist: LinkedList):
        if llist is EmptyList:
            return e.Atom("Nil")
        else:
            return llist.rest

    @index.add_function("lmap")
    def _lmap(r: e.Runtime, fn: e.Entity, llist: LinkedList):
        if not isinstance(llist, LinkedList):
            raise TypeError(f"Cannot (lmap ... {llist})")
        if llist is EmptyList:
            return llist
        else:
            return e.SExpr(
                _cons,
                e.SExpr(fn, llist.value),
                e.SExpr(_lmap, fn, llist.rest)
            )

    @index.add_function("lforeach")
    def _lmap(r: e.Runtime, fn: e.Entity, llist: LinkedList):
        if not isinstance(llist, LinkedList):
            raise TypeError(f"Cannot (lmap ... {llist})")
        for x in llist:
            fn.call(x).evaluate(r)
        return e.Atom("Nil")


    ###################################
    return index