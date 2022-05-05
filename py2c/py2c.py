import sys

TEMPLATE = """#include <stdio.h>

int main(void) {
    return {{return value}};
}"""


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
        i += 1

    return tokens


def parse(tokens):
    parsed = ""
    for token in tokens:
        if isinstance(token, int):
            parsed += str(token)
        elif token == "+":
            parsed += " + "
        elif token == "-":
            parsed += " - "
    return parsed


def output_integer(i):
    tokens = tokenize(i)
    parsed = parse(tokens)
    print(TEMPLATE.replace("{{return value}}", parsed))


if __name__ == "__main__":
    output_integer(sys.argv[1])
