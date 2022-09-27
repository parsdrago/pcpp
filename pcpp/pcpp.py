TEMPLATE = """int main(void) {
    {{STATEMENTS}}
}"""


class IntNode:
    def __init__(self, value):
        self.value = value
        self.type = "int"

    def evaluate(self):
        return str(self.value)


class FloatNode:
    def __init__(self, value):
        self.value = value
        self.type = "double"

    def evaluate(self):
        return str(self.value)


class StringNode:
    def __init__(self, value):
        self.value = value
        self.type = "std::string"

    def evaluate(self):
        return f"std::string({self.value})"


class ListNode:
    def __init__(self, elements):
        self.elements = elements
        self.type = f"std::vector<{elements[0].type}>"
        self.element_type = elements[0].type

    def evaluate(self):
        return f'{self.type} {{{",".join(elem.evaluate() for elem in self.elements)}}}'


class TrueNode:
    def __init__(self):
        self.type = "bool"

    def evaluate(self):
        return "true"


class FalseNode:
    def __init__(self):
        self.type = "bool"

    def evaluate(self):
        return "false"


class VariableNode:
    def __init__(self, name, variable_type=None):
        self.name = name
        self.type = self._parse_type(variable_type)

    def _parse_type(self, type_str):
        if type_str == "auto":
            return "auto"
        if type_str == "int":
            return "int"
        if type_str == "float":
            return "double"
        if type_str == "string":
            return "std::string"
        if type_str.startswith("list[") and type_str.endswith("]"):
            return f"std::vector<{self._parse_type(type_str[5:-1])}>"

        raise ValueError(f"Unknown type {type_str}")

    def evaluate(self):
        return self.name


class ListElementNode:
    def __init__(self, array, index, array_type):
        self.array = array
        self.index = index
        if array_type.startswith("std::vector"):
            self.is_list = True
            self.type = array_type.split("<")[1].split(">")[0]
        else:
            self.is_list = False
            self.type = array_type

    def evaluate(self):
        if not self.is_list and self.type == "std::string":
            return f"{self.array}.substr({self.index.evaluate()}, {self.index.evaluate()} + 1)"
        return f"{self.array}[{self.index.evaluate()}]"


class ParenthesisNode:
    def __init__(self, inner):
        self.inner = inner
        self.type = self.inner.type

    def evaluate(self):
        return f"({self.inner.evaluate()})"


class BinaryOperatorNode:
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

        if self.left.type == self.right.type:
            self.type = self.left.type

        elif self.left.type == "auto":
            self.type = self.right.type

        elif self.right.type == "auto":
            self.type = self.left.type

        elif self.left.type == "int" and self.right.type == "double":
            self.type = "double"

        elif self.left.type == "double" and self.right.type == "int":
            self.type = "double"

        else:
            raise Exception(
                f"Cannot perform {self.operator} on {self.left.type} and {self.right.type}"
            )

    def evaluate(self):
        return f"{self.left.evaluate()} {self.operator} {self.right.evaluate()}"


class AssignmentNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = self.value.type

    def evaluate(self):
        return f"{self.name.evaluate()} = {self.value.evaluate()}"


class DeclarationNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = self.value.type

        if self.name.type == "auto":
            self.name.type = self.value.type

        if self.name.type != self.value.type:
            raise Exception(
                f"Type mismatch for {self.name.evaluate()}: {self.name.type} != {self.value.type}"
            )

    def evaluate(self):
        return f"{self.name.type} {self.name.evaluate()} = {self.value.evaluate()}"


class IfExpressionNode:
    def __init__(self, condition, true_branch, false_branch):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

        if self.true_branch.type != self.false_branch.type:
            raise Exception(
                f"Type mismatch in if expression: {self.true_branch.type} != {self.false_branch.type}"
            )

        self.type = true_branch.type

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
        self.return_type = "int" if name == "main" else "auto"

    def evaluate(self):
        return f"{self.return_type} {self.name}({','.join('auto ' + arg.name  for arg in self.args)}) {{ {self.body.evaluate()} }}"


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


class ForNode:
    def __init__(self, item_type, item_name, iterable, body):
        self.item_type = item_type
        self.item_name = item_name
        self.iterable = iterable
        self.body = body

    def evaluate(self):
        return f"for ({self.item_type} {self.item_name} : {self.iterable.evaluate()}) {{ {self.body.evaluate()} }}"


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
        self.type = "auto"

    def evaluate(self):
        if self.name == "range":
            start = None
            end = None
            step = None
            if len(self.args) == 1:
                start = 0
                end = int(self.args[0].evaluate())
                step = 1
            elif len(self.args) == 2:
                start = int(self.args[0].evaluate())
                end = int(self.args[1].evaluate())
                step = 1
            elif len(self.args) == 3:
                start = int(self.args[0].evaluate())
                end = int(self.args[1].evaluate())
                step = int(self.args[2].evaluate())
            else:
                raise Exception(
                    f"Invalid number of arguments for range: {len(self.args)}"
                )
            return f"pcpp::Range({start}, {end}, {step})"
        return f"{self.name}({','.join(arg.evaluate() for arg in self.args)})"


class BraceNode:
    def __init__(self, statements):
        self.statements = statements

    def evaluate(self):
        return self.statements.evaluate()


class StatementNode:
    def __init__(self, statement):
        self.statement = statement
        self.type = self.statement.type

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

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.value})"


class Scope:
    """
    A scope is a collection of variables.
    It has a parent scope, which it inherits variables from.
    It has a child scope, which it can create new variables in.
    """

    def __init__(self, parent):
        self.parent = parent
        self.variables = {}

    def get(self, name: str):
        """
        Get the value of a variable in this scope.
        If the variable is not found, it will look in the parent scope.
        If the variable is not found in the parent scope, raise an exception.
        """
        if name in self.variables:
            return self.variables[name]

        if self.parent:
            return self.parent.get(name)

        raise Exception(f"Variable {name} not found")

    def add(self, name):
        """
        Add a variable to this scope.

        If the variable already exists in this scope, raise an exception.
        """

        if name in self.variables:
            raise Exception(f"Variable {name} already exists")

        self.variables[name.name] = name

    def __contains__(self, item):
        if "[" in item and "]" in item:
            variable_name = item.split("[")[0]
            return variable_name in self.variables
        return item in self.variables


class ScopeStack:
    """
    A stack of scopes.
    It has a current scope, which it can access.
    """

    def __init__(self):
        self.scopes = [Scope(None)]

    def get(self, name: str):
        """
        Get the value of a variable in the current scope.
        If the variable is not found, raise an exception.
        """
        return self.scopes[-1].get(name)

    def add(self, name):
        """
        Add a variable to the current scope.

        If the variable already exists in the current scope, raise an exception.
        """
        self.scopes[-1].add(name)

    def push(self):
        """
        Push a new scope onto the stack.
        """
        self.scopes.append(Scope(self.scopes[-1]))

    def pop(self):
        """
        Pop the current scope off the stack.
        """
        self.scopes.pop()

    def __contains__(self, item):
        """
        Check if the current scope contains the given variable.
        """
        return item in self.scopes[-1]


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
        ("+=", Token("+=", "+=")),
        ("-=", Token("-=", "-=")),
        ("*=", Token("*=", "*=")),
        ("/=", Token("/=", "/=")),
        ("%=", Token("%=", "%=")),
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
        ("for", Token("for", "for")),
        ("in", Token("in", "in")),
        ("break", Token("break", "break")),
        ("continue", Token("continue", "continue")),
        ("def", Token("def", "def")),
        ("int", Token("type", "int")),
        ("float", Token("type", "float")),
        ("bool", Token("type", "bool")),
        ("str", Token("type", "str")),
        ("list", Token("type", "list")),
        (":", Token(":", ":")),
        (",", Token(",", ",")),
        ("{", Token("{", "{")),
        ("}", Token("}", "}")),
        ("True", Token("True", "True")),
        ("False", Token("False", "False")),
        ("[", Token("[", "[")),
        ("]", Token("]", "]")),
    ]
    symbols.sort(key=lambda s: len(s[0]), reverse=True)
    tokens = []
    i = 0
    while i < len(code):
        for symbol, tokenized in symbols:
            if code[i : i + len(symbol)] == symbol:
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
                while i + 1 < len(code) and code[i + 1] in [" ", "\t"]:
                    i += 1
                    indent_level += 1
                tokens.append(Token("\n", indent_level))
                i += 1
            elif code[i] == '"':
                start = i
                i += 1
                while i < len(code) and code[i] != '"':
                    i += 1
                if code[i] != '"':
                    raise ValueError("invalid string")
                tokens.append(Token("str", code[start : i + 1]))
                i += 1
            elif code[i] == " ":
                i += 1
            else:
                raise Exception("Unknown Symbol: " + code[i])

    return tokens


def parse(tokens):
    include_flags = {
        "string": False,
        "vector": False,
        "initializer_list": False,
        "pcpp": False,
    }
    scopes = ScopeStack()

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
            return IntNode(token.value)
        if token.kind == "float":
            return FloatNode(token.value)
        if token.kind == "str":
            include_flags["string"] = True
            return StringNode(token.value)
        if token.kind == "[":
            include_flags["vector"] = True
            elements = []
            while len(tokens) > 0 and tokens[0].kind != "]":
                elements.append(expr(tokens))
                if tokens[0].kind != ",":
                    break
                tokens.pop(0)
            if len(tokens) == 0:
                raise Exception("Missing ]")
            tokens.pop(0)
            return ListNode(elements)
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
                if token.value == "range":
                    include_flags["pcpp"] = True
                return FunctionCallNode(token.value, args)
            if len(tokens) > 0 and tokens[0].kind == "[":
                args = []
                tokens.pop(0)
                index = expr(tokens)
                if tokens[0].kind != "]":
                    raise Exception("Missing ]")
                tokens.pop(0)
                if token.value not in scopes:
                    raise Exception("Undefined variable: " + token.value)
                return ListElementNode(token.value, index, scopes.get(token.value).type)
            if len(tokens) > 0 and tokens[0].kind == ":":
                tokens.pop(0)
                if len(tokens) > 0 and tokens[0].kind == "type":
                    type_token = tokens.pop(0)
                    if type_token.value == "list":
                        if len(tokens) > 0 and tokens[0].kind != "[":
                            raise Exception("Missing [")
                        tokens.pop(0)
                        item_type = tokens.pop(0)
                        if item_type.kind != "type":
                            raise Exception("Invalid type")
                        if tokens[0].kind != "]":
                            raise Exception("Missing ]")
                        tokens.pop(0)
                        type_token.value = "list[" + item_type.value + "]"
                    return VariableNode(token.value, type_token.value)
                tokens.insert(0, Token(":", ":"))
            return VariableNode(token.value, "auto")
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
        while len(tokens) > 0 and (
            tokens[0].kind in ["==", "!=", ">", ">=", "<", "<="]
        ):
            token = tokens.pop(0)
            node = BinaryOperatorNode(token.value, node, addi(tokens))
        return node

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
            if not isinstance(node, VariableNode) and not isinstance(
                node, ListElementNode
            ):
                raise Exception("Expected variable")
            if node.evaluate() in scopes:
                node = AssignmentNode(node, value)
            else:
                scopes.add(node)
                node = DeclarationNode(node, value)
        return node

    def statement(tokens):
        if tokens[0].kind == "return":
            tokens.pop(0)
            return ReturnNode(expr(tokens))
        elif tokens[0].kind == "def":
            tokens.pop(0)
            name = tokens.pop(0).value
            if name in scopes:
                raise Exception("Variable already defined")
            if tokens.pop(0).kind != "(":
                raise Exception("Expected (")
            args = []
            while tokens[0].kind != ")":
                if tokens[0].kind != "name":
                    raise Exception("Expected variable name")
                if tokens[0].value in args:
                    raise Exception("Duplicate argument")
                name_token = tokens.pop(0)
                type_token = None
                if len(tokens) > 0 and tokens[0].kind == ":":
                    tokens.pop(0)
                    if len(tokens) > 0 and tokens[0].kind == "type":
                        type_token = tokens.pop(0)
                    else:
                        raise Exception("Expected type")
                args.append(
                    VariableNode(
                        name_token.value, type_token.value if type_token else "auto"
                    )
                )
            tokens.pop(0)
            if tokens.pop(0).kind != ":":
                raise Exception("Expected :")
            if tokens[0].kind == "\n":
                tokens.pop(0)
            scopes.push()
            for arg in args:
                scopes.add(arg)
            body = brace(tokens)
            scopes.pop()
            node = FunctionNode(name, args, body)
            scopes.add(node)
            return node
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
            while len(tokens) > 0 and tokens[0].kind == "\n":
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
                while len(tokens) > 0 and tokens[0].kind == "\n":
                    tokens.pop(0)
            else_node = None
            while len(tokens) > 0 and tokens[0].kind == "\n":
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
        elif tokens[0].kind == "for":
            tokens.pop(0)
            name = tokens.pop(0)
            if name.kind != "name":
                raise Exception("Expected variable name")
            if tokens.pop(0).kind != "in":
                raise Exception("Expected in")
            iterable = atom(tokens)
            if tokens.pop(0).kind != ":":
                raise Exception("Expected :")
            while tokens[0].kind == "\n":
                tokens.pop(0)
            body = brace(tokens)
            return ForNode(iterable.type, name.value, iterable, body)
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
    includes = ""
    for flag in include_flags:
        if include_flags[flag]:
            if flag == "pcpp":
                includes += '#include "pcpp.h"\n'
            else:
                includes += f"#include <{flag}>\n"
    return includes


def transpile_code(code, use_template):
    unoffsided = unoffside(code)
    tokens = tokenize(unoffsided)
    include_flags, parsed = parse(tokens)
    inclusion_value = evaluate_include_flags(include_flags)
    value = parsed.evaluate()
    if use_template:
        return inclusion_value + TEMPLATE.replace("{{STATEMENTS}}", value)
    else:
        return inclusion_value + value


def main(code, output_file, use_template):
    with open(output_file, "w") as f:
        f.write(transpile_code(code, use_template))
