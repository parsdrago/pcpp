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


def test_tokenize_equality():
    assert py2c.tokenize("1 == 2") == [1, "==", 2]


def test_tokenize_inequality():
    assert py2c.tokenize("1 != 2") == [1, "!=", 2]


def test_tokenize_greaterthan():
    assert py2c.tokenize("1 > 2") == [1, ">", 2]


def test_tokenize_lessthan():
    assert py2c.tokenize("1 < 2") == [1, "<", 2]


def test_tokenize_greaterthan_equal():
    assert py2c.tokenize("1 >= 2") == [1, ">=", 2]


def test_tokenize_lessthan_equal():
    assert py2c.tokenize("1 <= 2") == [1, "<=", 2]


def test_tokenize_if():
    assert py2c.tokenize("3 if 1 == 1 else 5") == [3, "if", 1, "==", 1, "else", 5]


def test_tokenize_if_complicated():
    assert py2c.tokenize("4 if(1==2)else 1") == [4, "if", "(", 1, "==", 2, ")", "else", 1]


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
    

def test_parse_equality():
    assert py2c.parse([1, "==", 2]).evaluate() == "1 == 2"


def test_parse_equality_complicated():
    assert py2c.parse(["(", 1, "+", 2, ")", "==", 3]).evaluate() == "(1 + 2) == 3"


def test_parse_inequality():
    assert py2c.parse([1, "!=", 2]).evaluate() == "1 != 2"


def test_parse_greaterthan():
    assert py2c.parse([1, ">", 2]).evaluate() == "1 > 2"


def test_parse_lessthan():
    assert py2c.parse([1, "<", 2]).evaluate() == "1 < 2"


def test_parse_greaterthan_equal():
    assert py2c.parse([1, ">=", 2]).evaluate() == "1 >= 2"


def test_parse_lessthan_equal():
    assert py2c.parse([1, "<=", 2]).evaluate() == "1 <= 2"


def test_parse_if():
    assert py2c.parse([3, "if", 1, "==", 1, "else", 5]).evaluate() == "1 == 1 ? 3 : 5"


def test_parse_if_complicated():
    assert py2c.parse(["(", 1, "+", 2, ")", "if", "(", 1, "==", 2, ")", "else", 1]).evaluate() == "(1 == 2) ? (1 + 2) : 1"
