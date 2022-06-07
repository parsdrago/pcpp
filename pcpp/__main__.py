import argparse
import pathlib
import shutil

import pcpp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="pcpp: python transpiler to C++")
    parser.add_argument("input_file", help="input file")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("--use_template", help="use template", action="store_true")

    args = parser.parse_args()
    if args.output is None:
        args.output = args.input_file.replace(".py", ".cpp")

    parent_directory = pathlib.Path(args.output).parent
    parent_directory.mkdir(parents=True, exist_ok=True)

    header_directory = pathlib.Path(__file__).parent

    shutil.copyfile(header_directory / "pcpp.h", parent_directory / "pcpp.h")

    with open(args.input_file, "r", encoding="utf-8") as f:
        code = f.read()
        pcpp.main(code, args.output, args.use_template)
