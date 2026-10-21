"""Turn a whole document (prose + math) into TTS-friendly English.

Supported math delimiters:

* Standard LaTeX:  ``$...$``, ``$$...$$``, ``\\(...\\)``, ``\\[...\\]``.
* Multi-line display blocks opened and closed by a line that is just ``$$``
  or ``\\[`` / ``\\]``.
* "Backslash-stripped" markdown (what ChatGPT/Claude output often becomes once
  rendered or copied): inline math in ``(...)`` and display math as a
  standalone ``[`` ... ``]`` block.  Because bare parentheses are also ordinary
  English punctuation, ``(...)`` is only translated when it *looks like* math
  (see :func:`looks_like_math`); genuine asides such as
  "(or totally ordered set)" are left untouched.

The public entry point is :func:`math2english`.  With ``annotate=True`` the
math is kept as written and each expression is followed by its reading
("In words: ..."), so the text still displays correctly but can be read aloud.
"""

import re

from .translator import MathTranslator, translate_fragment

__all__ = ["math2english", "looks_like_math", "DocumentConverter"]


def looks_like_math(inner):
    """Heuristic: does the content of a ``(...)`` group denote math?

    Conservative on purpose so ordinary English parentheticals are preserved.
    """
    text = inner.strip()
    if not text:
        return False
    # Any LaTeX control sequence is a strong signal.
    if "\\" in text:
        return True
    # A word of three or more letters means it is prose, not a math variable.
    if re.search(r"[A-Za-z]{3,}", text):
        return False
    # A single identifier, e.g. (S), (A), (u).
    if re.fullmatch(r"[A-Za-z]", text):
        return True
    # A bare number or numeric list / interval, e.g. (1000) or (0,1).
    if re.fullmatch(r"[\d\s,.\-+]+", text):
        return True
    # Short expressions containing a relation or operator, e.g. (a=b), (x<y).
    if re.search(r"[=<>^_]", text) and not re.search(r"[A-Za-z]{3,}", text):
        return True
    return False


# A standalone display-math block:  a line that is just "[", "\[" or "$$"
# (optionally indented) through the next line that is just the matching closer.
_DISPLAY_OPEN = re.compile(r"^(\s*)(\[|\\\[|\$\$)\s*$")
_DISPLAY_CLOSERS = {"[": "]", "\\[": "\\]", "$$": "$$"}

# Inline math with no nested parentheses.
_INLINE_PAREN = re.compile(r"\(([^()]*)\)")
_INLINE_BACKSLASH = re.compile(r"\\\((.+?)\\\)")
_INLINE_DISPLAY_BS = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
_INLINE_DOLLAR2 = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
_INLINE_DOLLAR1 = re.compile(r"\$([^$]+?)\$")

# Commands that carry their own braces and may appear outside math delimiters
# (common in chemistry/physics prose): \ce{...}, \pu{...}, \SI{..}{..}, ...
_EMBEDDED_CMD = re.compile(r"\\(ce|pu|SI|qty|si|unit)\b")

# Lightweight markdown that should not be spoken aloud.
_MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MD_ITALIC = re.compile(r"(?<![\w*])[*_](?!\s)(.+?)(?<!\s)[*_](?![\w*])")
_MD_CODE = re.compile(r"`([^`]+)`")
_MD_HEADING = re.compile(r"^\s*#{1,6}\s*")
_MD_BLOCKQUOTE = re.compile(r"^\s*>\s?")
_MD_BULLET = re.compile(r"^(\s*)[*+-]\s+")
_MD_HRULE = re.compile(r"^\s*([-*_])\1{2,}\s*$")

# Placeholder protecting already-handled math from later substitution passes.
_PLACEHOLDER = re.compile("\x00(\\d+)\x00")


class DocumentConverter:
    """Convert a mixed prose/math document into spoken English."""

    def __init__(self, translator=None, strip_markdown=True, mode="math",
                 annotate=False):
        self.translator = translator or MathTranslator(mode=mode)
        # Annotated output is meant to be displayed, so markdown stays intact.
        self.strip_markdown = strip_markdown and not annotate
        self.annotate = annotate

    def convert(self, text):
        lines = text.splitlines()
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            opener = _DISPLAY_OPEN.match(line)
            if opener:
                block, i = self._read_display_block(lines, i, opener)
                if block is not None:
                    out.append(block)
                    continue
            out.append(self._convert_prose_line(line))
            i += 1
        return "\n".join(out)

    # -- display math -----------------------------------------------------
    def _read_display_block(self, lines, start, opener):
        indent, delim = opener.groups()
        closer = _DISPLAY_CLOSERS[delim]
        j = start + 1
        body = []
        while j < len(lines) and lines[j].strip() != closer:
            body.append(lines[j])
            j += 1
        if j >= len(lines):
            return None, start  # no closer; treat the opener as ordinary text
        latex = " ".join(s.strip() for s in body).strip()
        spoken = self.translator.translate(latex)
        if self.annotate:
            original = "\n".join(lines[start:j + 1])
            return f"{original}\n{indent}In words: {as_sentence(spoken)}", j + 1
        spoken = _sentence_case(spoken)
        return spoken, j + 1

    # -- prose + inline math ---------------------------------------------
    def _convert_prose_line(self, line):
        if _MD_HRULE.match(line):
            return ""

        # Each handled span becomes a placeholder so later passes cannot
        # re-match the math (or its annotation); they are restored at the end.
        self._spans = []

        # Translate standard delimiters first so their contents are protected.
        line = _INLINE_DISPLAY_BS.sub(lambda m: self._inline(*m.group(0, 1), pad=True), line)
        line = _INLINE_DOLLAR2.sub(lambda m: self._inline(*m.group(0, 1)), line)
        line = _INLINE_BACKSLASH.sub(lambda m: self._inline(*m.group(0, 1)), line)
        line = _INLINE_DOLLAR1.sub(lambda m: self._inline(*m.group(0, 1)), line)

        # Chemistry/physics commands that appear without math delimiters.
        line = self._translate_embedded(line)

        # Backslash-stripped inline math in bare parentheses.
        line = _INLINE_PAREN.sub(self._maybe_inline_paren, line)

        if self.strip_markdown:
            line = self._strip_markdown(line)
            line = self._restore(line)
            # Markdown structure has been flattened; drop leftover indentation
            # so text-to-speech does not stumble over stray whitespace.
            return line.strip()
        return self._restore(line).rstrip()

    def _inline(self, original, latex, pad=False):
        """Placeholder for one inline math span: its reading, or (annotating)
        the original math followed by its reading."""
        spoken = self.translator.translate(latex)
        if self.annotate:
            text = original
            if " " in spoken:  # skip trivial readings such as (S) or $x$
                text += f" (in words: {spoken})"
        else:
            text = f" {spoken} " if pad else spoken
        self._spans.append(text)
        return f"\x00{len(self._spans) - 1}\x00"

    def _restore(self, line):
        return _PLACEHOLDER.sub(lambda m: self._spans[int(m.group(1))], line)

    def _translate_embedded(self, line):
        out = []
        pos = 0
        for m in _EMBEDDED_CMD.finditer(line):
            if m.start() < pos:
                continue
            cmd = m.group(1)
            nargs = 2 if cmd in ("SI", "qty") else 1
            args, end = _read_braced_args(line, m.end(), nargs)
            if args is None:
                continue  # malformed: leave as-is
            out.append(line[pos:m.start()])
            out.append(self._inline(line[m.start():end], "\\" + cmd + args))
            pos = end
        out.append(line[pos:])
        return "".join(out)

    def _maybe_inline_paren(self, match):
        if looks_like_math(match.group(1)):
            return self._inline(*match.group(0, 1))
        return match.group(0)  # keep genuine English parenthetical

    def _strip_markdown(self, line):
        line = _MD_HEADING.sub("", line)
        line = _MD_BLOCKQUOTE.sub("", line)
        line = _MD_BULLET.sub(r"\1", line)
        line = _MD_BOLD.sub(r"\1", line)
        line = _MD_CODE.sub(r"\1", line)
        line = _MD_ITALIC.sub(r"\1", line)
        return re.sub(r"[ \t]{2,}", " ", line)


def _read_braced_args(text, start, count):
    """Read ``count`` balanced ``{...}`` groups beginning at ``start``.

    Returns ``(raw_substring, end_index)`` including the braces, or
    ``(None, start)`` if the expected groups are not present.
    """
    i = start
    pieces = []
    for _ in range(count):
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text) or text[i] != "{":
            return None, start
        depth = 0
        j = i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        else:
            return None, start  # unbalanced
        pieces.append(text[i:j])
        i = j
    return "".join(pieces), i


def _sentence_case(text):
    if text and text[0].islower() and re.match(r"[a-z]", text):
        # Leave single-letter math variables (a, b, s) as-is; only uppercase
        # when the phrase begins with a real word.
        first = text.split(" ", 1)[0]
        if len(first) > 1:
            return text[0].upper() + text[1:]
    return text


def as_sentence(text):
    """Sentence-case *text* and end it with a full stop, for "In words: ..."."""
    return _sentence_case(text.strip().rstrip(".,;:")) + "."


# A whole document is signalled by explicit math delimiters ($...$, \(...\),
# \[...\]) which only make sense when math is embedded in surrounding prose.
_DOC_DELIMITER = re.compile(r"\$|\\\(|\\\[")


def _looks_like_document(text):
    """Heuristic: is *text* a whole document (prose + math) or a bare fragment?

    A document gets delimiter and markdown handling; a bare LaTeX fragment is
    translated directly.  Documents are recognised by explicit math delimiters,
    multiple lines, or ordinary English words -- anything else is treated as a
    single math fragment.
    """
    stripped = text.strip()
    if not stripped:
        return False
    if "\n" in stripped or _DOC_DELIMITER.search(stripped):
        return True
    # Count plain prose words (3+ letters) after removing LaTeX commands and
    # environment names, which also contain letters (e.g. \begin{pmatrix}).
    residue = re.sub(r"\\(?:begin|end)\s*\{[^}]*\}", " ", stripped)
    residue = re.sub(r"\\[A-Za-z]+", " ", residue)
    return len(re.findall(r"[A-Za-z]{3,}", residue)) >= 2


def math2english(text, strip_markdown=True, mode="math", annotate=False):
    """Convert LaTeX math into spoken English for text-to-speech.

    Accepts either a bare LaTeX fragment (e.g. ``r"s = \\sup A"``) or a whole
    document mixing prose and math (e.g. ``"An element (u \\in S) is ..."``);
    the two are told apart automatically.  ``mode`` selects the vocabulary:
    ``"math"`` (default), ``"physics"`` or ``"chemistry"``.  ``strip_markdown``
    applies to document input only.

    With ``annotate=True`` the math is kept as written and each expression is
    followed by its reading: display math gets an ``In words: ...`` line and
    inline math a ``(in words: ...)`` parenthetical.
    """
    if _looks_like_document(text):
        return DocumentConverter(
            strip_markdown=strip_markdown, mode=mode, annotate=annotate
        ).convert(text)
    spoken = translate_fragment(text, mode=mode)
    if annotate:
        return f"{text.strip()}\nIn words: {as_sentence(spoken)}"
    return spoken
