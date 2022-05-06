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
        return f"{self.name.evaluate()} = {self.value.evaluate()}"


class DeclarationNode:
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


class FunctionNode:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def evaluate(self):
        return f"int {self.name}({','.join('int ' + arg  for arg in self.args)}) {{ {self.body.evaluate()} }}"


class StatementList:
    def __init__(self):
        self.expressions = []

    def add(self, expr):
        self.expressions.append(expr)

    def evaluate(self):
        return ";\n".join(expr.evaluate() for expr in self.expressions) + ";"


class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Token):
            return False
        return self.kind == __o.kind and self.value == __o.value


def tokenize(code):
    symbols = [
        ("+", Token("+", "+")),
        ("-", Token("-", "-")),
        ("*", Token("*", "*")),
        ("//", Token("/", "/")),
        ("%", Token("%", "%")),
        ("(", Token("(", "(")),
        (")", Token(")", ")")),
        ("=", Token("=", "=")),
        (";", Token(";", ";")),
        ("<", Token("<", "<")),
        (">", Token(">", ">")),
        ("<=", Token("<=", "<=")),
        (">=", Token(">=", ">=")),
        ("!=", Token("!=", "!=")),
        ("==", Token("==", "==")),
        ("if", Token("if", "if")),
        ("else", Token("else", "else")),
        ("return", Token("return", "return")),
        ("def", Token("def", "def")),
        (":", Token(":", ":")),
        (",", Token(",", ",")),
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
                tokens.append(Token("int", int(code[start:i])))
            elif code[i].isalpha() or code[i] == "_":
                start = i
                while i < len(code) and (code[i].isalnum() or code[i] == "_"):
                    i += 1
                tokens.append(Token("name", code[start:i]))
            elif code[i] == "\n":
                indent_level = 0
                while i+1 < len(code) and code[i+1] in [" ", "\t"]:
                    i += 1
                    indent_level += 1
                tokens.append(Token("\n",indent_level))
                i += 1
            elif code[i] == " ":
                i += 1
            else:
                raise Exception("Unexpected token: " + code[i])

    return tokens


def parse(tokens):
    def atom(tokens):
        token = tokens.pop(0)
        if token.kind == "(":
            result = expr(tokens)
            if tokens.pop(0).kind != ")":
                raise Exception("Missing )")
            return ParenthesisNode(result)
        if token.kind == "int":
            return AtomicNode(token.value)
        if token.kind == "name":
            return VariableNode(token.value)
        raise Exception("Unexpected token: " + token)

    def mul(tokens):
        node = atom(tokens)
        while len(tokens) > 0 and (tokens[0].kind in ["*", "/", "%"]):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token.value, node, atom(tokens))
        return node

    def addi(tokens):
        node = mul(tokens)
        while len(tokens) > 0 and (tokens[0].kind in ["+", "-"]):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token.value, node, mul(tokens))
        return node

    def comp(tokens):
        node = addi(tokens)
        while len(tokens) > 0 and (tokens[0].kind in ["==", "!=", ">", ">=", "<", "<="]):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token.value, node, addi(tokens))
        return node

    defined_variables = []

    def expr(tokens):
        node = comp(tokens)
        if len(tokens) > 0 and tokens[0].kind == "if":
            tokens.pop(0)
            condition = comp(tokens)
            if tokens.pop(0).kind != "else":
                raise Exception("Expected else")
            false_branch = comp(tokens)
            node = IfNode(condition, node, false_branch)
        elif len(tokens) > 0 and tokens[0].kind == "=":
            tokens.pop(0)
            value = comp(tokens)
            if not isinstance(node, VariableNode):
                raise Exception("Expected variable")
            if node.evaluate() in defined_variables:
                node = AssignmentNode(node, value)
            else:
                defined_variables.append(node.evaluate())
                node = DeclarationNode(node, value)
        return node

    def statement(tokens):
        if tokens[0].kind == "return":
            tokens.pop(0)
            return ReturnNode(expr(tokens))
        elif tokens[0].kind == "def":
            tokens.pop(0)
            name = tokens.pop(0).value
            if name in defined_variables:
                raise Exception("Variable already defined")
            if tokens.pop(0).kind != "(":
                raise Exception("Expected (")
            args = []
            while tokens[0].kind != ")":
                if tokens[0].kind != "name":
                    raise Exception("Expected variable name")
                if tokens[0].value in args:
                    raise Exception("Duplicate argument")
                args.append(tokens.pop(0).value)
            tokens.pop(0)
            if tokens.pop(0).kind != ":":
                raise Exception("Expected :")
            body = statements(tokens)
            defined_variables.append(name)
            return FunctionNode(name, args, body)
        return expr(tokens)

    def statements(tokens):
        expr_list = StatementList()
        node = statement(tokens)
        expr_list.add(node)
        while len(tokens) > 0 and tokens[0].kind in [";", "\n"]:
            tokens.pop(0)
            if len(tokens) == 0:
                break
            if tokens[0].kind in [";", "\n"]:
                continue
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
    with open(sys.argv[1], "r", encoding='utf-8') as f:
        code = f.read()
        output_integer(code)
