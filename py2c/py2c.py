import sys

TEMPLATE = """#include <stdio.h>

int main(void) {
    {{STATEMENTS}}
}"""


class AtomicNode:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return str(self.value)


class VariableNode:
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        return self.name


class ParenthesisNode:
    def __init__(self, inner):
        self.inner = inner

    def evaluate(self):
        return f"({self.inner.evaluate()})"


class BinaryOperatorNode:
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self):
        return f"{self.left.evaluate()} {self.operator} {self.right.evaluate()}"


class AssignmentNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def evaluate(self):
        return f"int {self.name.evaluate()} = {self.value.evaluate()}"


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
    symbols = [
        ("+", "+"),
        ("-", "-"),
        ("*", "*"),
        ("//", "/"),
        ("==", "=="),
        ("!=", "!="),
        (">", ">"),
        (">=", ">="),
        ("<", "<"),
        ("<=", "<="),
        ("=", "="),
        ("if", "if"),
        ("else", "else"),
        ("return", "return"),
        (";", ";"),
        ("(", "("),
        (")", ")"),
    ]
    symbols.sort(key=lambda s: len(s[0]), reverse=True)
    tokens = []
    i = 0
    while i < len(code):
        for symbol, tokenized in symbols:
            if code[i:i+len(symbol)] == symbol:
                tokens.append(tokenized)
                i += len(symbol)
                break
        else:
            if code[i] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                start = i
                while i < len(code) and code[i] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    i += 1
                tokens.append(int(code[start:i]))
            elif code[i].isalpha() or code[i] == "_":
                start = i
                while i < len(code) and (code[i].isalnum() or code[i] == "_"):
                    i += 1
                tokens.append(code[start:i])
            elif code[i] == " ":
                i += 1
            else:
                raise Exception("Unexpected token: " + code[i])

    return tokens


def parse(tokens):
    def atom(tokens):
        token = tokens.pop(0)
        if token == "(":
            result = expr(tokens)
            if tokens.pop(0) != ")":
                raise Exception("Missing )")
            return ParenthesisNode(result)
        if isinstance(token, int):
            return AtomicNode(token)
        if isinstance(token, str):
            return VariableNode(token)
        raise Exception("Unexpected token: " + token)

    def mul(tokens):
        node = atom(tokens)
        while len(tokens) > 0 and (tokens[0] == "*" or tokens[0] == "/"):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token, node, atom(tokens))
        return node

    def addi(tokens):
        node = mul(tokens)
        while len(tokens) > 0 and (tokens[0] == "+" or tokens[0] == "-"):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token, node, mul(tokens))
        return node

    def comp(tokens):
        node = addi(tokens)
        while len(tokens) > 0 and (tokens[0] in ["==", "!=", ">", ">=", "<", "<="]):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token, node, addi(tokens))
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
        elif len(tokens) > 0 and tokens[0] == "=":
            _ = tokens.pop(0)
            value = comp(tokens)
            node = AssignmentNode(node, value)
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
