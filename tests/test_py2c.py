import pytest

from py2c import __version__, py2c

Token = py2c.Token

def test_version():
    assert __version__ == "0.1.0"


def test_tokenize_1():
    assert py2c.tokenize("1") == [Token("int", 1)]


def test_tokenize_42():
    assert py2c.tokenize("42") == [Token("int", 42)]


def test_tokenize_two_digits():
    assert py2c.tokenize("42 12") == [Token("int", 42), Token("int", 12)]


def test_tokenize_addition():
    assert py2c.tokenize("1 + 2") == [Token("int", 1), Token("+", "+"), Token("int", 2)]


def test_tokenize_subtraction():
    assert py2c.tokenize("1 - 2") == [Token("int", 1), Token("-", "-"), Token("int", 2)]


def test_tokenize_multiplication():
    assert py2c.tokenize("1 * 2") == [Token("int", 1), Token("*", "*"), Token("int", 2)]


def test_tokenize_division():
    assert py2c.tokenize("1 // 2") == [Token("int", 1), Token("/", "/"), Token("int", 2)]


def test_tokenize_unknown_token():
    with pytest.raises(Exception):
        py2c.tokenize("1 ? 2")


def test_tokenize_parenthes():
    assert py2c.tokenize("(1 + 2)") == [Token("(", "("), Token("int", 1), Token("+", "+"), Token("int", 2), Token(")", ")")]


def test_tokenize_equality():
    assert py2c.tokenize("1 == 2") == [Token("int", 1), Token("==", "=="), Token("int", 2)]


def test_tokenize_inequality():
    assert py2c.tokenize("1 != 2") == [Token("int", 1), Token("!=", "!="), Token("int", 2)]


def test_tokenize_greaterthan():
    assert py2c.tokenize("1 > 2") == [Token("int", 1), Token(">", ">"), Token("int", 2)]


def test_tokenize_lessthan():
    assert py2c.tokenize("1 < 2") == [Token("int", 1), Token("<", "<"), Token("int", 2)]


def test_tokenize_greaterthan_equal():
    assert py2c.tokenize("1 >= 2") == [Token("int", 1), Token(">=", ">="), Token("int", 2)]


def test_tokenize_lessthan_equal():
    assert py2c.tokenize("1 <= 2") == [Token("int", 1), Token("<=", "<="), Token("int", 2)]


def test_tokenize_if():
    assert py2c.tokenize("3 if 1 == 1 else 5") == [Token("int", 3), Token("if", "if"), Token("int", 1), Token("==", "=="), Token("int", 1), Token("else", "else"), Token("int", 5)]


def test_tokenize_multiple_expressions():
    assert py2c.tokenize("1 + 2 * 3; 1 + 3") == [Token("int", 1), Token("+", "+"), Token("int", 2), Token("*", "*"), Token("int", 3), Token(";", ";"), Token("int", 1), Token("+", "+"), Token("int", 3)]


def test_tokenize_return():
    assert py2c.tokenize("return 1") == [Token("return", "return"), Token("int", 1)]


def test_tokenize_assign():
    assert py2c.tokenize("a = 1") == [Token("name", "a"), Token("=", "="), Token("int", 1)]


def test_tokenize_variablename():
    assert py2c.tokenize("varname123 = 1") == [Token("name", "varname123"), Token("=", "="), Token("int", 1)]


def test_tokenize_variablename_with_no_succeeding_whitespace():
    assert py2c.tokenize("varname123=1") == [Token("name", "varname123"), Token("=", "="), Token("int", 1)]


def test_tokenize_variablename_startswith_underbar():
    assert py2c.tokenize("_varname123 = 1") == [Token("name", "_varname123"), Token("=", "="), Token("int", 1)]


def test_tokenize_newline():
    assert py2c.tokenize("1\n 2") == [Token("int", 1), Token("\n", 1), Token("int", 2)]


def test_parse_integer():
    assert py2c.parse([Token("int", 1)]).evaluate() == "1;"


def test_parse_addition():
    assert py2c.parse([Token("int", 1), Token("+", "+"), Token("int", 2)]).evaluate() == "1 + 2;"


def test_parse_subtraction():
    assert py2c.parse([Token("int", 1), Token("-", "-"), Token("int", 2)]).evaluate() == "1 - 2;"


def test_parse_multiplication():
    assert py2c.parse([Token("int", 1), Token("*", "*"), Token("int", 2)]).evaluate() == "1 * 2;"


def test_parse_division():
    assert py2c.parse([Token("int", 1), Token("/", "/"), Token("int", 2)]).evaluate() == "1 / 2;"


def test_parse_parenthes():
    assert py2c.parse([Token("(", "("), Token("int", 1), Token("+", "+"), Token("int", 2), Token(")", ")")]).evaluate() == "(1 + 2);"


def test_parse_equality():
    assert py2c.parse([Token("int", 1), Token("==", "=="), Token("int", 2)]).evaluate() == "1 == 2;"


def test_parse_inequality():
    assert py2c.parse([Token("int", 1), Token("!=", "!="), Token("int", 2)]).evaluate() == "1 != 2;"


def test_parse_greaterthan():
    assert py2c.parse([Token("int", 1), Token(">", ">"), Token("int", 2)]).evaluate() == "1 > 2;"


def test_parse_lessthan():
    assert py2c.parse([Token("int", 1), Token("<", "<"), Token("int", 2)]).evaluate() == "1 < 2;"


def test_parse_greaterthan_equal():
    assert py2c.parse([Token("int", 1), Token(">=", ">="), Token("int", 2)]).evaluate() == "1 >= 2;"


def test_parse_lessthan_equal():
    assert py2c.parse([Token("int", 1), Token("<=", "<="), Token("int", 2)]).evaluate() == "1 <= 2;"


def test_parse_if():
    assert py2c.parse([Token("int", 3), Token("if", "if"), Token("int", 1), Token("==", "=="), Token("int", 1), Token("else", "else"), Token("int", 5)]).evaluate() == "1 == 1 ? 3 : 5;"


def test_parse_multiple_expressions():
    assert py2c.parse([Token("int", 1), Token("+", "+"), Token("int", 2), Token("*", "*"), Token("int", 3), Token(";", ";"), Token("int", 1), Token("+", "+"), Token("int", 3)]).evaluate() == "1 + 2 * 3;\n1 + 3;"


def test_parse_return():
    assert py2c.parse([Token("return", "return"), Token("int", 1)]).evaluate() == "return 1;"


def test_parse_assign():
    assert py2c.parse([Token("name", "a"), Token("=", "="), Token("int", 1)]).evaluate() == "int a = 1;"


def test_parse_assign_and_return():
    assert py2c.parse([Token("name", "a"), Token("=", "="), Token("int", 1), Token(";", ";"), Token("return", "return"), Token("name", "a")]).evaluate() == "int a = 1;\nreturn a;"


def test_parse_declare_and_assing():
    assert py2c.parse([Token("name", "a"), Token("=", "="), Token("int", 1), Token(";",";"), Token("name", "a"), Token("=", "="), Token("int", 2)]).evaluate() == "int a = 1;\na = 2;"


def test_parse_define_function():
    assert py2c.parse([Token("def", "def"), Token("name", "f"), Token("(", "("), Token("name", "a"), Token(")", ")"),
    Token(":", ":"), Token("return", "return"), Token("name", "a")]).evaluate() == "int f(int a) { return a; };"
