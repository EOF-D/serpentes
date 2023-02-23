from argparse import ArgumentParser
from sysconfig import get_paths

from serpentes import __author__, __version__


def main() -> None:
    parser = ArgumentParser(prog="Serpentes", description="Tools for Serpentes.")

    parser.add_argument(
        "--hook", action="store_true", help="Hooks the Serpentes codec to Python."
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Shows the current version of Serpentes.",
    )

    parser.add_argument("--author", action="store_true", help="The author of Serpentes.")

    args = parser.parse_args()

    if args.version is True:
        print(f"Serpentes {__version__}")

    elif args.author is True:
        print(__author__)

    if args.hook is True:
        path = get_paths()["purelib"]

        with open(get_paths()["purelib"] + "/serpentes_autoload.pth", "a") as fp:
            fp.write("import serpentes")

        print(f"Wrote `serpentes_autoload.pth` to {path}")


if __name__ == "__main__":
    main()
