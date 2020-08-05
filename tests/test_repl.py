from io import StringIO
import pytest
from pylarklispy import repl

def test_repl(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin",
        StringIO(
            "(+ 1 2 3)\n"
            "(print! :hello)\n"
            "(quit!)\n"
    ))
    with pytest.raises(SystemExit):
        repl()
    out, err = capsys.readouterr()
    lines = out.splitlines()
    assert "REPL" in lines[0]
    assert "6" in lines[1]
    assert ":hello" in lines[2]
    assert ":Nil" in lines[3]
    # it should look kind of like this:
    """
    [REPL]
    |> (+ 1 2 3)
    6
    |> (print! :hello)
    :hello
    :Nil
    |> (quit!)
    Bye for now!
    """