from typing import *
import pylarklispy.entities as e

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

    @addf("render")
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


    @addf("server")
    def _(
        r: e.Runtime,
        route_table: e.Vector,
        host: e.String = e.String("0.0.0.0"),
        port: e.Integer = e.Integer(8080)
    ):
        routes = web.RouteTableDef()

        @routes.get('/')
        async def hello(request):
            return web.Response(text="Hello, world")

        for route, fn in route_table.pairs():
            assert isinstance(route, e.String)
            assert isinstance(fn, e.Function)

            @routes.get(route.s)
            async def route_stuff(request, fn=fn): # closure crap!

                @e.Function.make("<Request wrapper>")
                def request_wrapper(rr: e.Runtime, a: e.Atom):
                    return e.String(request.match_info[a.s])

                text = e.SExpr(_render, e.SExpr(fn, request_wrapper)).evaluate(r) # type: ignore
                assert isinstance(text, e.String)
                return web.Response(text=text.s, content_type="text/html")

        app = web.Application()
        app.add_routes(routes)
        web.run_app(app, host=host.s, port=port.n)
        return e.Atom("Nil")


    ###################################
    return index