import lark
from typing import Iterable, List, Optional, Tuple
from . import parser, entities, bif

def compile_code(code: str) -> List[entities.Entity]:
    tree = parser.parser.parse(code)
    return parser.Transformer().transform(tree)

def run_ast(
        statements: Iterable[entities.Entity], *,
        runtime: Optional[entities.Runtime]=None
        ) -> Tuple[entities.Entity, entities.Runtime]:
    runtime = runtime or entities.Runtime(bif.index)
    result = entities.Atom("Nil")
    for statement in statements:
        result = statement.evaluate(runtime)
    return (result, runtime)

def compile_and_run(
            code: str,
            runtime: Optional[entities.Runtime]=None
    ) -> Tuple[entities.Entity, entities.Runtime]:
    return run_ast(compile_code(code), runtime=runtime)

def repl(runtime=None):
    print("[REPL]")
    runtime = runtime or entities.Runtime(bif.index)
    while True:
        command = input("|> ")
        try:
            ast = compile_code(command)
            result, _ = run_ast(ast, runtime=runtime)
            print(result)
        except lark.LarkError:
            print("Syntax error!")
        except Exception as e:
            print(e.__class__.__name__, e)
