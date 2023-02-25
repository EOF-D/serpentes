# TODO: Replace with compiled AST

from argparse import ArgumentParser


def compiler() -> None:
    parser = ArgumentParser(prog="Compiler")
    parser.add_argument("--file", help="File to compile.")

    args = parser.parse_args()
    if args.file:
        with open(args.file, "r") as fp:
            exec(fp.read())


if __name__ == "__main__":
    compiler()
