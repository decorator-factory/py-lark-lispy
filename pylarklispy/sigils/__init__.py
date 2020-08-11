from typing import *
import pylarklispy.entities as e
from ..interop_utils import Index


def interop(_runtime: e.Runtime):
    import re
    index = Index()
    ####################################


    @index.add_function("sigil<%>")
    def _(r: e.Runtime, template: e.String):
        matches = list(re.finditer(r"(?<!%)%(?!%)", template.s))

        @e.Function.make("sigil<%>.substitute")
        def substitute(rr: e.Runtime, *args: e.Entity):
            if len(args) != len(matches):
                raise ValueError(f"Expected {len(matches)} args for "
                                 f"{template}, got: {e.Vector(*args)}")
            chars = list(template.s)
            for match, arg in [*zip(matches, args)][::-1]:
                index = match.start(0)
                chars[index:index+1] =\
                    e.SExpr(e.Name("format"), arg).evaluate(rr).s # type: ignore
            return e.String("".join(chars))

        return substitute


    @index.add_function("sigil<f>")
    def _(r: e.Runtime, template: e.String):
        matches = list(re.finditer(r"\%\(([^{}]+?)\)", template.s))

        @e.Function.make("sigil<f>.substitute")
        def substitute(rr: e.Runtime, lookup: e.Entity):
            chars = list(template.s)
            for match in matches[::-1]:
                name = match.group(1)
                slice_ = slice(match.start(0), match.end(1)+1)
                chars[slice_] = \
                    e.SExpr(e.Name("format"), e.SExpr(lookup, e.Atom(name))).evaluate(rr).s # type: ignore
            return e.String("".join(chars))

        return substitute



    ###################################
    return index