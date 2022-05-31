import argparse

import pcpp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pcpp: python transpiler to C++")
    parser.add_argument("input_file", help="input file")
    parser.add_argument("--use_template", help="use template", action="store_true")

    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        code = f.read()
        pcpp.main(code, args.use_template)
