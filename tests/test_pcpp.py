import glob
import shutil
import subprocess

import pytest

from pcpp import __version__, pcpp

Token = pcpp.Token


def test_version():
    assert __version__ == "0.1.0"


def test_unoffside_indent():
    assert pcpp.unoffside("a\n b") == "a\n{b}"


def test_unoffside_nested_indent():
    assert pcpp.unoffside("a\n b\n  c") == "a\n{b\n{c}}"


def test_tokenize_1():
    assert pcpp.tokenize("1") == [Token("int", 1)]


def test_tokenize_42():
    assert pcpp.tokenize("42") == [Token("int", 42)]


def test_tokenize_two_digits():
    assert pcpp.tokenize("42 12") == [Token("int", 42), Token("int", 12)]


def test_tokenize_addition():
    assert pcpp.tokenize("1 + 2") == [Token("int", 1), Token("+", "+"), Token("int", 2)]


def test_tokenize_subtraction():
    assert pcpp.tokenize("1 - 2") == [Token("int", 1), Token("-", "-"), Token("int", 2)]


def test_tokenize_multiplication():
    assert pcpp.tokenize("1 * 2") == [Token("int", 1), Token("*", "*"), Token("int", 2)]


def test_tokenize_division():
    assert pcpp.tokenize("1 // 2") == [
        Token("int", 1),
        Token("/", "/"),
        Token("int", 2),
    ]


def test_tokenize_unknown_token():
    with pytest.raises(Exception):
        pcpp.tokenize("1 ? 2")


def test_tokenize_parenthes():
    assert pcpp.tokenize("(1 + 2)") == [
        Token("(", "("),
        Token("int", 1),
        Token("+", "+"),
        Token("int", 2),
        Token(")", ")"),
    ]


def test_tokenize_equality():
    assert pcpp.tokenize("1 == 2") == [
        Token("int", 1),
        Token("==", "=="),
        Token("int", 2),
    ]


def test_tokenize_inequality():
    assert pcpp.tokenize("1 != 2") == [
        Token("int", 1),
        Token("!=", "!="),
        Token("int", 2),
    ]


def test_tokenize_greaterthan():
    assert pcpp.tokenize("1 > 2") == [Token("int", 1), Token(">", ">"), Token("int", 2)]


def test_tokenize_lessthan():
    assert pcpp.tokenize("1 < 2") == [Token("int", 1), Token("<", "<"), Token("int", 2)]


def test_tokenize_greaterthan_equal():
    assert pcpp.tokenize("1 >= 2") == [
        Token("int", 1),
        Token(">=", ">="),
        Token("int", 2),
    ]


def test_tokenize_lessthan_equal():
    assert pcpp.tokenize("1 <= 2") == [
        Token("int", 1),
        Token("<=", "<="),
        Token("int", 2),
    ]


def test_tokenize_if():
    assert pcpp.tokenize("3 if 1 == 1 else 5") == [
        Token("int", 3),
        Token("if", "if"),
        Token("int", 1),
        Token("==", "=="),
        Token("int", 1),
        Token("else", "else"),
        Token("int", 5),
    ]


def test_tokenize_multiple_expressions():
    assert pcpp.tokenize("1 + 2 * 3; 1 + 3") == [
        Token("int", 1),
        Token("+", "+"),
        Token("int", 2),
        Token("*", "*"),
        Token("int", 3),
        Token(";", ";"),
        Token("int", 1),
        Token("+", "+"),
        Token("int", 3),
    ]


def test_tokenize_return():
    assert pcpp.tokenize("return 1") == [Token("return", "return"), Token("int", 1)]


def test_tokenize_assign():
    assert pcpp.tokenize("a = 1") == [
        Token("name", "a"),
        Token("=", "="),
        Token("int", 1),
    ]


def test_tokenize_variablename():
    assert pcpp.tokenize("varname123 = 1") == [
        Token("name", "varname123"),
        Token("=", "="),
        Token("int", 1),
    ]


def test_tokenize_variablename_with_no_succeeding_whitespace():
    assert pcpp.tokenize("varname123=1") == [
        Token("name", "varname123"),
        Token("=", "="),
        Token("int", 1),
    ]


def test_tokenize_variablename_startswith_underbar():
    assert pcpp.tokenize("_varname123 = 1") == [
        Token("name", "_varname123"),
        Token("=", "="),
        Token("int", 1),
    ]


def test_tokenize_newline():
    assert pcpp.tokenize("1\n 2") == [Token("int", 1), Token("\n", 1), Token("int", 2)]


def test_evaluate_range_function():
    assert (
        pcpp.FunctionCallNode("range", [pcpp.IntNode("5")]).evaluate()
        == "pcpp::Range(0, 5, 1)"
    )


@pytest.mark.parametrize("file_name", glob.glob("./test_scripts/*.py"))
def test_script(file_name):
    with open(file_name) as f:
        with open("./.test/test.cpp", "w") as fw:
            fw.write(pcpp.transpile_code(f.read(), False))

        shutil.copyfile("./pcpp/pcpp.h", "./.test/pcpp.h")

        subprocess.run(
            "clang++ -std=c++20 -o ./.test/test.exe ./.test/test.cpp", check=True
        )
        return_value = subprocess.run("./.test/test.exe", check=False)

    assert return_value.returncode == 42
