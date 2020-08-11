from tests.utils import result, run

def test_ref():
    expr, r = run("""
        (define ref (interop "pylarklispy.ref"))
        (define var ((ref :make) 0))
        ((ref :get!) var)
    """)
    assert expr == result("0")

    expr, r = run("""
        ((ref :set!) var 1)
        ((ref :get!) var)
    """, runtime=r)
    assert expr == result("1")
