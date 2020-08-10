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

    @addf("map")
    def _(r: e.Runtime, f: e.Entity, v: e.Vector):
        return e.Vector(
            *(e.SExpr(f, x) for x in v.es)
        )

    ###################################
    return index