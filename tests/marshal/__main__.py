import marshal
import os
from argparse import ArgumentParser


def main() -> None:
    parser = ArgumentParser(prog="Marshal")
    parser.add_argument("--file", help="File to run.")
    parser.add_argument("--bootstrap", action="store_true")

    args = parser.parse_args()
    path = os.path.dirname(__file__) + "/"

    if args.file:
        with open(path + "bin/serpentes", "rb") as fp:
            exec(marshal.load(fp))

    elif args.bootstrap:
        with open(path + "bin/serpentes", "wb") as fp:
            with open(path + "compiler.py", "r") as fd:
                marshal.dump(compile(fd.read(), "<string>", "exec"), fp)


if __name__ == "__main__":
    main()
