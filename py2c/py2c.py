import sys

TEMPLATE = """int main(void) {
    {{STATEMENTS}}
}"""


class AtomicNode:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return str(self.value)


class StringNode:
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return f"std::string({self.value})"


class TrueNode:
    def evaluate(self):
        return "true"


class FalseNode:
    def evaluate(self):
        return "false"


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
        return f"auto {self.name.evaluate()} = {self.value.evaluate()}"


class IfExpressionNode:
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
        return f"return {self.value.evaluate()};"


class FunctionNode:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def evaluate(self):
        if self.name == "main":
            return f"int {self.name}({','.join('auto ' + arg  for arg in self.args)}) {{ {self.body.evaluate()} }}"
        return f"auto {self.name}({','.join('auto ' + arg  for arg in self.args)}) {{ {self.body.evaluate()} }}"


class IfStatementsNode:
    def __init__(self, if_node, elif_nodes, else_node):
        self.if_node = if_node
        self.elif_nodes = elif_nodes
        self.else_node = else_node

    def evaluate(self):
        return f"{self.if_node.evaluate()}{''.join(elif_node.evaluate() for elif_node in self.elif_nodes)}{self.else_node.evaluate() if self.else_node else ''}"

class IfNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def evaluate(self):
        return f"if ({self.condition.evaluate()}) {{ {self.body.evaluate()} }}"


class ElifNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def evaluate(self):
        return f"else if ({self.condition.evaluate()}) {{ {self.body.evaluate()} }}"


class ElseNode:
    def __init__(self, body):
        self.body = body

    def evaluate(self):
        return f"else {{ {self.body.evaluate()} }}"


class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def evaluate(self):
        return f"while ({self.condition.evaluate()}) {{ {self.body.evaluate()} }}"


class BreakNode:
    def evaluate(self):
        return "break;"


class ContinueNode:
    def evaluate(self):
        return "continue;"


class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def evaluate(self):
        return f"{self.name}({','.join(arg.evaluate() for arg in self.args)})"


class BraceNode:
    def __init__(self, statements):
        self.statements = statements

    def evaluate(self):
        return self.statements.evaluate()


class StatementNode:
    def __init__(self, statement):
        self.statement = statement

    def evaluate(self):
        return self.statement.evaluate() + ";"

class StatementList:
    def __init__(self):
        self.expressions = []

    def add(self, expr):
        self.expressions.append(expr)

    def evaluate(self):
        return "\n".join(expr.evaluate() for expr in self.expressions)


class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Token):
            return False
        return self.kind == __o.kind and self.value == __o.value


def unoffside(code):
    """
    convert offside rule to {}-specified rule
    """
    lines = code.split("\n")
    new_lines = []
    indents = []
    for line in lines:
        i = 0
        if len(line) > 0:
            while line[i] == " ":
                i += 1
        indent = line[:i]
        if i == len(line):
            continue
        if len(indents) > 0 and indents[-1] != indent:
            if indent.startswith(indents[-1]):
                new_lines.append("{" + line[i:])
                indents.append(indent)
            else:
                count = 0
                while len(indents) > 0 and not indent.startswith(indents[-1]):
                    indents.pop()
                    count += 1
                new_lines.append("}\n" * count + line[i:])
        elif len(indents) == 0 and indent == "":
            new_lines.append(line)
        elif len(indents) == 0 and indent != "":
            new_lines.append("{" + line[i:])
            indents.append(indent)
        elif indents[-1] == indent:
            new_lines.append(line[i:])

    return "\n".join(new_lines) + "}" * len(indents)


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
        ("elif", Token("elif", "elif")),
        ("else", Token("else", "else")),
        ("return", Token("return", "return")),
        ("while", Token("while", "while")),
        ("break", Token("break", "break")),
        ("continue", Token("continue", "continue")),
        ("def", Token("def", "def")),
        (":", Token(":", ":")),
        (",", Token(",", ",")),
        ("{", Token("{", "{")),
        ("}", Token("}", "}")),
        ("True", Token("True", "True")),
        ("False", Token("False", "False")),
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
            if code[i].isdigit():
                dot_exist = False
                start = i
                while i < len(code):
                    if code[i] == ".":
                        if dot_exist:
                            raise ValueError("invalid number")
                        dot_exist = True
                    elif not code[i].isdigit():
                        break
                    i += 1
                if dot_exist:
                    tokens.append(Token("float", float(code[start:i])))
                else:
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
            elif code[i] == "\"":
                start = i
                i += 1
                while i < len(code) and code[i] != "\"":
                    i += 1
                if code[i] != "\"":
                    raise ValueError("invalid string")
                tokens.append(Token("str", code[start:i+1]))
                i += 1
            elif code[i] == " ":
                i += 1
            else:
                raise Exception("Unknown Symbol: " + code[i])

    return tokens


def parse(tokens):
    include_flags = { "string": False }
    def atom(tokens):
        token = tokens.pop(0)
        if token.kind == "True":
            return TrueNode()
        if token.kind == "False":
            return FalseNode()
        if token.kind == "(":
            result = expr(tokens)
            if tokens.pop(0).kind != ")":
                raise Exception("Missing )")
            return ParenthesisNode(result)
        if token.kind == "int":
            return AtomicNode(token.value)
        if token.kind == "float":
            return AtomicNode(token.value)
        if token.kind == "str":
            include_flags["string"] = True
            return StringNode(token.value)
        if token.kind == "name":
            if len(tokens) > 0 and tokens[0].kind == "(":
                args = []
                tokens.pop(0)
                while len(tokens) > 0 and tokens[0].kind != ")":
                    args.append(expr(tokens))
                    if tokens[0].kind != ",":
                        break
                    tokens.pop(0)
                if tokens[0].kind != ")":
                    raise Exception("Missing )")
                tokens.pop(0)
                return FunctionCallNode(token.value, args)
            return VariableNode(token.value)
        raise Exception("Unexpected token: " + token.kind)

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
            node = IfExpressionNode(condition, node, false_branch)
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
            if tokens[0].kind == "\n":
                tokens.pop(0)
            body = brace(tokens)
            defined_variables.append(name)
            return FunctionNode(name, args, body)
        elif tokens[0].kind == "if":
            tokens.pop(0)
            if_condition = comp(tokens)
            if tokens.pop(0).kind != ":":
                raise Exception("Expected :")

            if tokens[0].kind == "\n":
                tokens.pop(0)
            if_body = brace(tokens)

            if_node = IfNode(if_condition, if_body)
            elif_nodes = []
            while len(tokens) > 0  and tokens[0].kind == "\n":
                tokens.pop(0)
            while len(tokens) > 0 and tokens[0].kind == "elif":
                tokens.pop(0)
                condition = comp(tokens)
                if tokens.pop(0).kind != ":":
                    raise Exception("Expected :")
                if tokens[0].kind == "\n":
                    tokens.pop(0)
                body = brace(tokens)
                elif_nodes.append(ElifNode(condition, body))
                while len(tokens) > 0  and tokens[0].kind == "\n":
                    tokens.pop(0)
            else_node = None
            while len(tokens) > 0  and tokens[0].kind == "\n":
                tokens.pop(0)
            if len(tokens) > 0 and tokens[0].kind == "else":
                tokens.pop(0)
                if tokens.pop(0).kind != ":":
                    raise Exception("Expected :")
                if tokens[0].kind == "\n":
                    tokens.pop(0)
                else_node = ElseNode(brace(tokens))

            return IfStatementsNode(if_node, elif_nodes, else_node)
        elif tokens[0].kind == "while":
            tokens.pop(0)
            condition = comp(tokens)
            if tokens.pop(0).kind != ":":
                raise Exception("Expected :")
            while tokens[0].kind == "\n":
                tokens.pop(0)

            body = brace(tokens)
            return WhileNode(condition, body)
        elif tokens[0].kind == "break":
            tokens.pop(0)
            return BreakNode()
        elif tokens[0].kind == "continue":
            tokens.pop(0)
            return ContinueNode()
        return StatementNode(expr(tokens))

    def brace(tokens):
        statements = StatementList()
        if tokens[0].kind != "{":
            statements.add(statement(tokens))
            return BraceNode(statements)
        tokens.pop(0)
        while True:
            statements.add(statement(tokens))
            if tokens[0].kind in [";", "\n"]:
                tokens.pop(0)
            if tokens[0].kind == "}":
                break
        tokens.pop(0)
        return BraceNode(statements)

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

    return include_flags, statements(tokens)


def evaluate_include_flags(include_flags):
    if include_flags["string"]:
        return "#include <string>\n"
    else:
        return ""


def main(code, use_template):
    unoffsided = unoffside(code)
    tokens = tokenize(unoffsided)
    include_flags, parsed = parse(tokens)
    inclusion_value = evaluate_include_flags(include_flags)
    value = parsed.evaluate()
    if use_template:
        print(inclusion_value + TEMPLATE.replace("{{STATEMENTS}}", value))
    else:
        print(inclusion_value + value)

if __name__ == "__main__":
    use_template = len(sys.argv) > 1 and "--template" in sys.argv
    with open(sys.argv[1], "r", encoding='utf-8') as f:
        code = f.read()
        main(code, use_template)
