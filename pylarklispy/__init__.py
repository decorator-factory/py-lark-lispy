from typing import Iterable, List
from . import parser, entities, bif

def compile_code(code: str) -> List[entities.SExpr]:
    tree = parser.parser.parse(code)
    return parser.Transformer().transform(tree)

def run_ast(statements: Iterable[entities.SExpr]) -> entities.Runtime:
    runtime = entities.Runtime(bif.index)
    for statement in statements:
        statement.evaluate(runtime)
    return runtime
