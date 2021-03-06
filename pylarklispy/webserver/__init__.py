from typing import *
import pylarklispy.entities as e
from ..interop_utils import Index

def interop(_runtime: e.Runtime):
    from aiohttp import web
    index = Index()
    ####################################

    @index.add_function("render")
    def _render(r: e.Runtime, obj):
        if isinstance(obj, e.String):
            return obj
        elif isinstance(obj, e.Vector):
            key, elements = obj.es
            assert isinstance(elements, (e.Vector, e.String)), f"{elements=}"
            if isinstance(elements, e.String):
                elements = e.Vector(elements)
            if isinstance(key, (e.Atom, e.String)):
                tag_name = key.s
                param_string = ""
            elif isinstance(key, e.Vector):
                tag, attrs = key.es
                assert isinstance(tag, (e.Atom, e.String)), f"{tag=}"
                assert isinstance(attrs, e.Vector), f"{attrs=}"
                tag_name = tag.s
                param_string = " ".join(
                    f"{name.s}={value.s}" for (name, value) in attrs.pairs() # type: ignore
                )
            else:
                assert False, f"bad key: {obj}->{key}"
            return e.SExpr(
                e.Name("join"),
                e.String(f"<{tag_name} {param_string}>"),
                *(e.SExpr(_render, element) for element in elements.es), # type: ignore
                e.String(f"</{tag_name}>"),
            )
        else:
            assert False, f"bad obj: {obj}"


    @index.add_function("server")
    def _(
        r: e.Runtime,
        route_table: e.Vector,
        host: e.String = e.String("0.0.0.0"),
        port: e.Integer = e.Integer(8080)
    ):
        routes = web.RouteTableDef()

        def connect_route(route: e.Vector):
            method, name, fn = route.es
            if not isinstance(method, (e.String, e.Atom)):
                raise ValueError(f"{method} should be a string or an atom")
            if not isinstance(name, e.String):
                raise TypeError(f"Route name must be a string, not {name}.")
            # we hope that `fn` is callable :-)
            add_route = getattr(routes, method.s)(name.s)

            @add_route
            def a_route(request):
                @e.Function.make("<Request wrapper>")
                def request_wrapper(rr: e.Runtime, a: e.Atom):
                    return e.String(request.match_info[a.s])

                text = e.SExpr(_render, e.SExpr(fn, request_wrapper)).evaluate(r) # type: ignore
                assert isinstance(text, e.String)
                return web.Response(text=text.s, content_type="text/html")

        for row in route_table.es:
            if not isinstance(row, e.Vector):
                raise TypeError(f"Routing row must be a vector, got {row}")
            connect_route(row)

        app = web.Application()
        app.add_routes(routes)
        web.run_app(app, host=host.s, port=port.n)
        return e.Atom("Nil")




    ###################################
    return index