"""Command-line interface: ``math2english [FILE]``.

Reads a document from a file (or stdin) and writes the spoken-English version
to stdout.  With ``--math`` the input is treated as a single bare LaTeX
fragment instead of a full document.
"""

import argparse
import sys

from . import __version__
from .document import to_english
from .translator import translate_math


def build_parser():
    parser = argparse.ArgumentParser(
        prog="math2english",
        description="Convert text containing LaTeX math into plain English for "
        "text-to-speech.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Input file (default: read from stdin).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write result to this file (default: stdout).",
    )
    parser.add_argument(
        "--math",
        action="store_true",
        help="Treat the whole input as one LaTeX math fragment.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=("math", "physics", "chemistry"),
        default="math",
        help="Vocabulary mode (default: math). physics adds vectors, "
        "derivatives and bra-ket; chemistry reads \\ce{...} formulas.",
    )
    parser.add_argument(
        "--keep-markdown",
        action="store_true",
        help="Do not strip markdown formatting (**bold**, headings, bullets).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.file:
        with open(args.file, "r", encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = sys.stdin.read()

    if args.math:
        result = translate_math(text.strip(), mode=args.mode)
    else:
        result = to_english(
            text, strip_markdown=not args.keep_markdown, mode=args.mode
        )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(result + "\n")
    else:
        sys.stdout.write(result + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
