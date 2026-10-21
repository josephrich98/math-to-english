"""Command-line interface: ``math2english [INPUT]``.

``INPUT`` may be a file to convert, or literal text/LaTeX to convert directly::

    math2english math_doc.md            # convert a document file
    math2english "q \\in \\mathbb Q"      # translate a bare LaTeX fragment
    math2english                        # read a document from stdin
    math2english math_doc.md --annotate # keep the math, add "In words: ..."

Bare fragments and whole documents are told apart automatically; pass
``--math`` to force fragment interpretation.  Add ``--dictate`` to also speak
the result aloud with the system text-to-speech engine.
"""

import argparse
import os
import shutil
import subprocess
import sys

from . import __version__
from .document import as_sentence, math2english
from .translator import translate_fragment


def build_parser():
    parser = argparse.ArgumentParser(
        prog="math2english",
        description="Convert text containing LaTeX math into plain English for "
        "text-to-speech.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input file, or literal text/LaTeX to convert "
        "(default: read from stdin).",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Write result to this file (default: stdout).",
    )
    parser.add_argument(
        "--math",
        action="store_true",
        help="Force treating the input as one bare LaTeX math fragment.",
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
        "-a",
        "--annotate",
        action="store_true",
        help="Keep the math as written and follow each expression with its "
        "reading ('In words: ...'), so the output still displays correctly.",
    )
    parser.add_argument(
        "--keep-markdown",
        action="store_true",
        help="Do not strip markdown formatting (**bold**, headings, bullets).",
    )
    parser.add_argument(
        "--dictate",
        action="store_true",
        help="Speak the result aloud using the system text-to-speech engine "
        "(macOS 'say', Linux 'spd-say'/'espeak'). Still writes text output too.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _find_tts():
    """Return the argv prefix for an available TTS command, or None."""
    for cmd in ("say", "spd-say", "espeak-ng", "espeak"):
        path = shutil.which(cmd)
        if path:
            return [path]
    return None


def dictate(text):
    """Speak ``text`` aloud. Returns True on success, False otherwise."""
    tts = _find_tts()
    if tts is None:
        sys.stderr.write(
            "math2english: --dictate needs a text-to-speech command "
            "('say' on macOS, 'spd-say' or 'espeak' on Linux).\n"
        )
        return False
    try:
        subprocess.run(tts + [text], check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        sys.stderr.write(f"math2english: text-to-speech failed: {exc}\n")
        return False
    return True


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.input is None:
        text = sys.stdin.read()
    elif os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = args.input  # literal text / LaTeX

    if args.math:
        result = translate_fragment(text.strip(), mode=args.mode)
        if args.annotate:
            result = f"{text.strip()}\nIn words: {as_sentence(result)}"
    else:
        result = math2english(
            text,
            strip_markdown=not args.keep_markdown,
            mode=args.mode,
            annotate=args.annotate,
        )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(result + "\n")
    else:
        sys.stdout.write(result + "\n")

    if args.dictate and not dictate(result):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
