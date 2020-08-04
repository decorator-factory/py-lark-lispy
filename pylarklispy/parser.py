import json
from os.path import join, dirname, realpath

import lark

from . import entities

DIR = dirname(realpath(__file__))
GRAMMAR_FILENAME = join(DIR, "grammar.lark")

with open(GRAMMAR_FILENAME) as grammar_file:
    grammar = grammar_file.read()

parser = lark.Lark(grammar, parser="lalr")

@lark.v_args(inline=True)
class Transformer(lark.Transformer):
    @staticmethod
    def ESCAPED_STRING(token):
        return json.loads(str(token))

    @staticmethod
    def start(*e: entities.Entity):
        return e

    @staticmethod
    def integer(token):
        return entities.Integer(int(token))

    @staticmethod
    def string(s):
        return entities.String(s)

    @staticmethod
    def atom(token):
        return entities.Atom(str(token))

    @staticmethod
    def sigil_string(sigil_token, string):
        return entities.SigilString(str(sigil_token), string)

    @staticmethod
    def name(token):
        return entities.Name(str(token))

    @staticmethod
    def s_expr(*es: entities.Entity):
        return entities.SExpr(*es)

    @staticmethod
    def vector(*es: entities.Entity):
        return entities.Vector(*es)

    @staticmethod
    def quoted(subentity):
        return entities.Quoted(subentity)