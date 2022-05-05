import sys

TEMPLATE = """#include <stdio.h>

int main(void) {
    {{STATEMENTS}}
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


class IfNode:
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def evaluate(self):
        return f"{self.condition.evaluate()} ? {self.true_branch.evaluate()} : {self.false_branch.evaluate()}"


class ReturnNode:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return f"return {self.value.evaluate()}"


class StatementList:
    def __init__(self):
        self.expressions = []

    def add(self, expr):
        self.expressions.append(expr)

    def evaluate(self):
        return "; ".join(expr.evaluate() for expr in self.expressions) + ";"


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
        elif c == "i":
            i += 1
            if code[i] == "f":
                tokens.append("if")
            else:
                raise Exception("Expected if")
        elif c == "e":
            i += 1
            if code[i] == "l":
                i += 1
                if code[i] == "s":
                    i += 1
                    if code[i] == "e":
                        tokens.append("else")
                    else:
                        raise Exception("Expected else")
                else:
                    raise Exception("Expected else")
            else:
                raise Exception("Expected else")
        elif c == " ":
            pass
        elif c == ";":
            tokens.append(";")
        elif c == "r":
            i += 1
            if code[i] == "e":
                i += 1
                if code[i] == "t":
                    i += 1
                    if code[i] == "u":
                        i += 1
                        if code[i] == "r":
                            i += 1
                            if code[i] == "n":
                                tokens.append("return")
                            else:
                                raise Exception("Expected return")
                        else:
                            raise Exception("Expected return")
                    else:
                        raise Exception("Expected return")
                else:
                    raise Exception("Expected return")
            else:
                raise Exception("Expected return")
        else:
            raise Exception("Unknown token: " + c)
        i += 1

    return tokens


def parse(tokens):
    def atom(tokens):
        token = tokens.pop(0)
        if token == "(":
            result = expr(tokens)
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

    def comp(tokens):
        node = addi(tokens)
        while len(tokens) > 0 and (tokens[0] in ["==", "!=", ">", ">=", "<", "<="]):
            token = tokens.pop(0)
            node = Node(token, node, addi(tokens))
        return node

    def expr(tokens):
        node = comp(tokens)
        if len(tokens) > 0 and tokens[0] == "if":
            token = tokens.pop(0)
            condition = comp(tokens)
            if tokens.pop(0) != "else":
                raise Exception("Expected else")
            false_branch = comp(tokens)
            node = IfNode(condition, node, false_branch)
        return node

    def statement(tokens):
        if tokens[0] == "return":
            tokens.pop(0)
            return ReturnNode(expr(tokens))
        return expr(tokens)

    def statements(tokens):
        expr_list = StatementList()
        node = statement(tokens)
        expr_list.add(node)
        while len(tokens) > 0 and tokens[0] == ";":
            tokens.pop(0)
            node = statement(tokens)
            expr_list.add(node)
        return expr_list

    return statements(tokens)


def output_integer(i):
    tokens = tokenize(i)
    parsed = parse(tokens)
    value = parsed.evaluate()
    print(TEMPLATE.replace("{{STATEMENTS}}", value))


if __name__ == "__main__":
    output_integer(sys.argv[1])
