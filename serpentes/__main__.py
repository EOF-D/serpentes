from argparse import ArgumentParser

from serpentes import __author__, __version__


def main() -> None:
    parser = ArgumentParser(prog="Serpentes", description="Tools for Serpentes.")
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Shows the current version of Serpentes.",
    )

    parser.add_argument(
        "-a", "--author", action="store_true", help="The author of Serpentes."
    )

    args = parser.parse_args()

    if args.version is True:
        print(f"Serpentes {__version__}")

    elif args.author is True:
        print(__author__)


if __name__ == "__main__":
    main()
