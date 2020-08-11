from tests.utils import result


def test_sigil_percent():
    expr = result("""
        (import "$.sigils" :all)
        (~%"I am %, and I am % years old." "Alice" 42)
    """)
    assert expr == result('"I am Alice, and I am 42 years old."')


def test_sigil_f():
    expr = result("""
        (import "$.sigils" :all)
        (~f"I am %(name), and I am %(age) years old."
            [:name "Alice", :age 42])
    """)
    assert expr == result('"I am Alice, and I am 42 years old."')