import pytest
import pylarklispy.parser as parser
from pylarklispy.entities import *

FULL_EXAMPLE = \
"""
# This is a comment
(hello world)
(lorem :ipsum [dolor-sit amet])
(quoted &ex &[pression])
(turtles (all (the (way :down))))
(whitespace [:does not
             :mat  ter])
(commas,,,,, :are [white , , space])
(strings "work fine")
(sigils ~r"are cool")
((higher order) stuff)
"""


def test_smoke():
    # check that all the language constructs work
    lark_parser = parser.parser
    tree = lark_parser.parse(FULL_EXAMPLE)


def test_ast():
    # check that the generated AST is correct
    lark_parser = parser.parser
    lark_transformer = parser.Transformer()
    tree = lark_parser.parse(FULL_EXAMPLE)
    ast = lark_transformer.transform(tree)
    expected = (
        SExpr( Name("hello"), Name("world") ),
        SExpr( Name("lorem"), Atom("ipsum"), Vector(Name("dolor-sit"), Name("amet")) ),
        SExpr( Name("quoted"), Quoted(Name("ex")), Quoted(Vector(Name("pression"))) ),
        SExpr( Name("turtles"), SExpr( Name("all"), SExpr( Name("the"),  SExpr( Name("way"), Atom("down")  )) ) ),
        SExpr( Name("whitespace"), Vector(Atom("does"), Name("not"), Atom("mat"), Name("ter")) ),
        SExpr( Name("commas"), Atom("are"), Vector(Name("white"), Name("space")) ),
        SExpr( Name("strings"), String("work fine") ),
        SExpr( Name("sigils"), SigilString("r", "are cool") ),
        SExpr( SExpr(Name("higher"), Name("order")), Name("stuff") ),
    )
    assert len(ast) == len(expected)
    assert ast == expected
