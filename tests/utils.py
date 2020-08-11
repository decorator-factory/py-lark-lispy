from pylarklispy import compile_and_run


def result(code: str):
    """Evaluate zero or more expressions from a stringly piece of code"""
    expr, _ = compile_and_run(code)
    return expr


run = compile_and_run
