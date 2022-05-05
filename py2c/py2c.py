import sys

TEMPLATE = """#include <stdio.h>

int main(void) {
    return {{return value}};
}"""


def output_integer(i):
    print(TEMPLATE.replace("{{return value}}", i))


if __name__ == "__main__":
    output_integer(sys.argv[1])
