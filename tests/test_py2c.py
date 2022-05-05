from py2c import __version__
from py2c import py2c


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


def test_parse_integer():
    assert py2c.parse([1]) == "1"


def test_parse_addition():
    assert py2c.parse([1, "+", 2]) == "1 + 2"
