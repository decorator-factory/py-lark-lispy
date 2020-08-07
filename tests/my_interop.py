import pylarklispy as lisp
e = lisp.entities

def interop(runtime: e.Runtime):
    return {
        "ping": e.String("pong")
    }