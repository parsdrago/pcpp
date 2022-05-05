import sys

TEMPLATE = """#include <stdio.h>

int main(void) {
    return {{return value}};
}"""


class Leaf:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return str(self.value)


class Parenthesis:
    def __init__(self, inner):
        self.inner = inner

    def evaluate(self):
        return f"({self.inner.evaluate()})"


class Node:
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self):
        return f"{self.left.evaluate()} {self.operator} {self.right.evaluate()}"


def tokenize(code):
    tokens = []
    i = 0
    while i < len(code):
        c = code[i]
        if c.isdigit():
            current = int(c)
            i += 1
            while i < len(code) and code[i].isdigit():
                c = code[i]
                if c.isdigit():
                    current = current * 10 + int(c)
                else:
                    break
                i += 1
            i -= 1
            tokens.append(current)
        elif c == "+":
            tokens.append("+")
        elif c == "-":
            tokens.append("-")
        elif c == "*":
            tokens.append("*")
        elif c == "/":
            i += 1
            if code[i] == "/":
                tokens.append("/")
            else:
                raise Exception("Expected /")
        elif c == "(":
            tokens.append("(")
        elif c == ")":
            tokens.append(")")
        elif c == "=":
            i += 1
            if code[i] == "=":
                tokens.append("==")
            else:
                raise Exception("Expected ==")
        elif c == "!":
            i += 1
            if code[i] == "=":
                tokens.append("!=")
            else:
                raise Exception("Expected !=")
        elif c == ">":
            i += 1
            if code[i] == "=":
                tokens.append(">=")
            else:
                tokens.append(">")
                i -= 1
        elif c == "<":
            i += 1
            if code[i] == "=":
                tokens.append("<=")
            else:
                tokens.append("<")
                i -= 1
        elif c == " ":
            pass
        else:
            raise Exception("Unknown token: " + c)
        i += 1

    return tokens


def parse(tokens):
    def atom(tokens):
        token = tokens.pop(0)
        if token == "(":
            result = addi(tokens)
            if tokens.pop(0) != ")":
                raise Exception("Missing )")
            return Parenthesis(result)
        if not isinstance(token, int):
            raise Exception("Expected integer, got: " + str(token))
        return Leaf(token)

    def mul(tokens):
        node = atom(tokens)
        while len(tokens) > 0 and (tokens[0] == "*" or tokens[0] == "/"):
            token = tokens.pop(0)
            node = Node(token, node, atom(tokens))
        return node

    def addi(tokens):
        node = mul(tokens)
        while len(tokens) > 0 and (tokens[0] == "+" or tokens[0] == "-"):
            token = tokens.pop(0)
            node = Node(token, node, mul(tokens))
        return node

    def expr(tokens):
        node = addi(tokens)
        while len(tokens) > 0 and (tokens[0] in ["==", "!=", ">", ">=", "<", "<="]):
            token = tokens.pop(0)
            node = Node(token, node, addi(tokens))
        return node

    return expr(tokens)


def output_integer(i):
    tokens = tokenize(i)
    parsed = parse(tokens)
    value = parsed.evaluate()
    print(TEMPLATE.replace("{{return value}}", value))


if __name__ == "__main__":
    output_integer(sys.argv[1])
