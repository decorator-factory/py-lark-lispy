import lark
from typing import Iterable, List, Optional, Tuple
from . import parser, entities, bif

def compile_code(code: str) -> List[entities.SExpr]:
    tree = parser.parser.parse(code)
    return parser.Transformer().transform(tree)

def run_ast(
        statements: Iterable[entities.SExpr], *,
        runtime: Optional[entities.Runtime]=None
        ) -> Tuple[entities.Entity, entities.Runtime]:
    runtime = runtime or entities.Runtime(bif.index)
    result = entities.Atom("None")
    for statement in statements:
        result = statement.evaluate(runtime)
    return (result, runtime)

def repl():
    print("[REPL]")
    runtime = entities.Runtime(bif.index)
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
