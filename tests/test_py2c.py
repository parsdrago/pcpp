import pytest

from py2c import __version__, py2c


def test_version():
    assert __version__ == "0.1.0"


def test_tokenize_1():
    assert py2c.tokenize("1") == [1]


def test_tokenize_42():
    assert py2c.tokenize("42") == [42]


def test_tokenize_two_digits():
    assert py2c.tokenize("42 12") == [42, 12]


def test_tokenize_addition():
    assert py2c.tokenize("1 + 2") == [1, "+", 2]


def test_tokenize_subtraction():
    assert py2c.tokenize("1 - 2") == [1, "-", 2]


def test_tokenize_multiplication():
    assert py2c.tokenize("1 * 2") == [1, "*", 2]


def test_tokenize_division():
    assert py2c.tokenize("1 // 2") == [1, "/", 2]


def test_tokenize_unknown_token():
    with pytest.raises(Exception):
        py2c.tokenize("1 ? 2")


def test_tokenize_parenthes():
    assert py2c.tokenize("(1 + 2)") == ["(", 1, "+", 2, ")"]


def test_parse_integer():
    assert py2c.parse([1]).evaluate() == "1"


def test_parse_addition():
    assert py2c.parse([1, "+", 2]).evaluate() == "1 + 2"


def test_parse_subtraction():
    assert py2c.parse([1, "-", 2]).evaluate() == "1 - 2"


def test_parse_multiplication():
    assert py2c.parse([1, "*", 2]).evaluate() == "1 * 2"


def test_parse_division():
    assert py2c.parse([1, "/", 2]).evaluate() == "1 / 2"


def test_parse_parenthes():
    assert py2c.parse(["(", 1, "+", 2, ")"]).evaluate() == "(1 + 2)"


def test_parse_parenthes_complicated():
    assert py2c.parse(["(", 1, "+", 2, ")", "*", 3]).evaluate() == "(1 + 2) * 3"

    
def test_parse_parenthes_complicated2():
    assert py2c.parse(["(", 1, "+", 2, ")", "*", "(", 2, "-", 1, ")"]).evaluate() == "(1 + 2) * (2 - 1)"
    