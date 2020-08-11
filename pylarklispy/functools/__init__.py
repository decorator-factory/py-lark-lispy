from typing import *
import pylarklispy.entities as e
from ..interop_utils import Index

def interop(_runtime: e.Runtime):
    index = Index()
    ####################################

    @index.add_function("map")
    def _(r: e.Runtime, f: e.Entity, v: e.Vector):
        return e.Vector(
            *(e.SExpr(f, x) for x in v.es)
        )

    ###################################
    return index