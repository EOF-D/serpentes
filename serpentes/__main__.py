import ast
import os
from argparse import ArgumentParser
from sysconfig import get_paths

import rich
from lark import Lark

from serpentes import SrpTransformer, __author__, __version__


def gen_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="Serpentes", description="Tools for Serpentes.")

    parser.add_argument("--author", action="store_true", help="The author of Serpentes.")
    parser.add_argument(
        "--hook", action="store_true", help="Hooks the Serpentes codec to Python."
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Shows the current version of Serpentes.",
    )

    parser.add_argument("--lark", help="Run a file with debug.")
    parser.add_argument("--run", help="Run a file without debug.")

    return parser


def main() -> None:
    parser = gen_parser()
    args = parser.parse_args()

    if args.version is True:
        print(f"Serpentes {__version__}")

    elif args.author is True:
        print(__author__)

    elif args.hook is True:
        path = get_paths()["purelib"]

        with open(path + "/serpentes_autoload.pth", "a") as fp:
            fp.write("import serpentes")

        print(f"Wrote `serpentes_autoload.pth` to {path}")

    elif args.lark or args.run:
        path = os.path.dirname(__file__)

        with open(f"{path}/parser/grammar.lark", "r") as fp:
            parser = Lark(
                fp.read(), start="module", parser="earley", propagate_positions=True
            )

        with open(args.lark or args.run, "r") as fp:
            tree = SrpTransformer().transform(parser.parse(fp.read()))

            if args.lark and not args.run:
                rich.inspect(tree, methods=True)

                module = tree.build()
                for index, children in enumerate(module.body):
                    rich.print(index, ast.dump(children, indent=2))

                code = compile(module, "<string>", "exec")
                exec(code)

            elif args.run:
                code = compile(tree.build(), "<string>", "exec")
                exec(code)


if __name__ == "__main__":
    main()
