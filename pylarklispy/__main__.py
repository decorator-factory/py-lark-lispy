from sys import argv, exit
from . import repl, compile_and_run

def ellipsify(s: str):
    parts = s.split("/")
    if len(parts) < 3:
        return s
    else:
        first, *body, last = parts
        body_s = "/".join(body)
        if len(body_s) < 16:
            return s
        return first + "/" + body_s[:6] + "..." + body_s[-6:] + "/" + last


EXECUTABLE = ellipsify(argv[0])
USAGE_STR = f"Usage: {EXECUTABLE} repl | run <filename> | runrepl <filename>"

if len(argv) not in (2, 3):
    print(USAGE_STR)
    exit(1)

if argv[1] == "repl":
    repl()
elif argv[1] == "run":
    with open(argv[2]) as file:
        program = file.read()
    compile_and_run(program)
elif argv[1] == "runrepl":
    with open(argv[2]) as file:
        program = file.read()
    _, runtime = compile_and_run(program)
    repl(runtime=runtime)
else:
    print(USAGE_STR)
    exit(1)