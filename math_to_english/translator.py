"""Translate a fragment of LaTeX math into spoken English.

The low-level entry point is :func:`translate_fragment` (and the
:class:`MathTranslator` class for callers that want to customise the
vocabulary); :func:`math_to_english.math2english` wraps it.  The translator is a
small tokenizer feeding a recursive-descent renderer, which keeps structural
constructs (fractions, roots, powers, sets, intervals) readable without a full
LaTeX parser.
"""

import re

from . import symbols as S
from . import chemistry as C

__all__ = ["MathTranslator", "translate_fragment", "MODES"]

MODES = ("math", "physics", "chemistry")

# One token is: a control word (\alpha), a control symbol (\,), a decimal or
# integer literal, a single letter, a run of whitespace, or any other single
# character (operators, braces, parentheses, ...).
_TOKEN_RE = re.compile(
    r"""
      \\[a-zA-Z]+      # control word, e.g. \le \mathbb \sqrt
    | \\.              # control symbol, e.g. \, \{ \%
    | \d+\.\d+         # decimal literal
    | \d+              # integer literal
    | [A-Za-z]         # single-letter identifier
    | \s+              # whitespace
    | .                # any single leftover char
    """,
    re.VERBOSE | re.DOTALL,
)

_OPENERS = "([{"
_CLOSERS = ")]}"


def _tokenize(latex):
    tokens = []
    for match in _TOKEN_RE.finditer(latex):
        tok = match.group(0)
        # Normalise escaped braces (\{ \}) to bare braces so set notation and
        # LaTeX's literal-brace form are handled the same way.
        if tok == r"\{":
            tok = "{"
        elif tok == r"\}":
            tok = "}"
        tokens.append(tok)
    return tokens


def _is_ws(tok):
    return tok.isspace()


class MathTranslator:
    """Render LaTeX math fragments as spoken English.

    Vocabulary tables are copied from :mod:`math_to_english.symbols` at
    construction time, so instances can be customised without affecting others::

        t = MathTranslator()
        t.relations[r"\\gg"] = "way bigger than"
    """

    def __init__(self, mode="math", function_application=True):
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}; choose from {MODES}")
        self.mode = mode
        self.words = S.combined_word_map()
        self.operators = dict(S.OPERATORS)
        self.big_operators = dict(S.BIG_OPERATORS)
        self.functions = dict(S.FUNCTIONS)
        self.char_operators = dict(S.CHAR_OPERATORS)
        self.symbols = dict(S.SYMBOLS)
        self.ignored = set(S.IGNORED)
        self.font_commands = set(S.FONT_COMMANDS)
        self.accents = dict(S.ACCENTS)
        self.unary_of = dict(S.UNARY_OF)
        self.binary_templates = dict(S.BINARY_TEMPLATES)
        # Names that trigger "f of x" reading when followed by "(...)".
        self.function_application = function_application
        self.function_names = set(self.functions.values())
        self._apply_mode(mode)

    def _apply_mode(self, mode):
        if mode == "physics":
            self.symbols.update(S.PHYSICS_SYMBOLS)
            self.unary_of.update(S.PHYSICS_UNARY_OF)
            self.binary_templates.update(S.PHYSICS_BINARY_TEMPLATES)
        elif mode == "chemistry":
            # Formulas such as O(g) are not function calls.
            self.function_application = False

    # -- public API -------------------------------------------------------
    def translate(self, latex):
        """Translate a LaTeX math string into an English phrase."""
        tokens = _tokenize(latex)
        return _cleanup(self._render(tokens))

    # -- rendering --------------------------------------------------------
    def _render(self, tokens):
        """Render a flat token list into a single English string."""
        parser = _Parser(self, tokens)
        return parser.run()


class _Parser:
    """Cursor over a token list producing English word-groups."""

    def __init__(self, translator, tokens):
        self.t = translator
        self.tokens = tokens
        self.i = 0
        self.parts = []

    # -- helpers ----------------------------------------------------------
    def _skip_ws(self):
        while self.i < len(self.tokens) and _is_ws(self.tokens[self.i]):
            self.i += 1

    def _collect_group(self):
        """Consume a balanced (), [] or {} group starting at the cursor.

        Returns ``(opener, closer, inner_tokens)`` with the cursor left just
        past the closing delimiter.  Depth is counted across bracket kinds,
        which is sufficient for well-formed input.
        """
        opener = self.tokens[self.i]
        self.i += 1
        depth = 1
        inner = []
        while self.i < len(self.tokens):
            tok = self.tokens[self.i]
            if tok in _OPENERS:
                depth += 1
            elif tok in _CLOSERS:
                depth -= 1
                if depth == 0:
                    self.i += 1
                    return opener, tok, inner
            inner.append(tok)
            self.i += 1
        return opener, "", inner  # unbalanced: treat rest as the group

    def _read_arg(self):
        """Read one rendered argument: a brace group or a single unit."""
        self._skip_ws()
        if self.i >= len(self.tokens):
            return ""
        if self.tokens[self.i] == "{":
            _, _, inner = self._collect_group()
            return self.t._render(inner)
        return self._render_unit()

    def _read_raw_arg(self):
        """Read one argument as literal text (used for \\text, \\mathbb...)."""
        self._skip_ws()
        if self.i >= len(self.tokens):
            return ""
        if self.tokens[self.i] == "{":
            _, _, inner = self._collect_group()
            return "".join(inner).strip()
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def _render_unit(self):
        """Render exactly one token (number, letter, symbol or command)."""
        tok = self.tokens[self.i]
        self.i += 1
        return self._render_token(tok)

    def _next_is_brace(self):
        j = self.i
        while j < len(self.tokens) and _is_ws(self.tokens[j]):
            j += 1
        return j < len(self.tokens) and self.tokens[j] == "{"

    # -- environments (matrices, cases, aligned blocks) ------------------
    def _handle_environment(self):
        env = self._read_raw_arg()
        if env in ("array", "tabular"):  # skip the column-spec argument
            self._skip_ws()
            if self.i < len(self.tokens) and self.tokens[self.i] in "{[":
                self._collect_group()
        inner = self._collect_until_end()
        self._emit(self._render_environment(env, inner))

    def _collect_until_end(self):
        depth = 1
        inner = []
        while self.i < len(self.tokens):
            tok = self.tokens[self.i]
            if tok == r"\begin":
                depth += 1
            elif tok == r"\end":
                depth -= 1
                if depth == 0:
                    self.i += 1
                    self._skip_ws()
                    if self.i < len(self.tokens) and self.tokens[self.i] == "{":
                        self._collect_group()
                    return inner
            inner.append(tok)
            self.i += 1
        return inner

    def _render_environment(self, env, inner):
        rows = []
        for row_tokens in _split_top(inner, {"\\\\"}):
            cols = [self.t._render(c).strip() for c in _split_top(row_tokens, {"&"})]
            cols = [c for c in cols if c]
            if cols:
                rows.append(cols)
        if not rows:
            return ""
        base = env.rstrip("*")
        if base in _DET_ENVS:
            return "the determinant with " + _matrix_body(rows)
        if base in _MATRIX_ENVS:
            return "the matrix with " + _matrix_body(rows)
        if base == "cases":
            return "the following: " + "; ".join(" ".join(c) for c in rows)
        # align / aligned / gather / equation / split / eqnarray, etc.
        return ", ".join(" ".join(c) for c in rows)

    # -- main loop --------------------------------------------------------
    def run(self):
        while self.i < len(self.tokens):
            tok = self.tokens[self.i]

            if _is_ws(tok):
                self.i += 1
                continue

            if tok in _OPENERS:
                _, closer, inner = self._collect_group()
                if tok == "(" and self._is_function_call(inner):
                    name = self.parts.pop()
                    self.parts.append(f"{name} of {self.t._render(inner).strip()}")
                else:
                    self._emit(self._render_group(tok, closer, inner))
                continue

            if tok in ("^", "_"):
                self.i += 1
                self._apply_script(tok)
                continue

            if tok.startswith("\\"):
                self._handle_command(tok)
                continue

            self.i += 1
            self._emit(self._render_token(tok))

        return " ".join(p for p in self.parts if p)

    def _emit(self, text):
        if text:
            self.parts.append(text)

    def _is_function_call(self, inner):
        """True when the previous part names a function applied to ``inner``."""
        if not self.t.function_application or not self.parts or not inner:
            return False
        prev = self.parts[-1]
        return bool(re.fullmatch(r"[A-Za-z]", prev) or prev in self.t.function_names)

    # -- token / command handling ----------------------------------------
    def _render_token(self, tok):
        if _is_ws(tok):
            return ""
        if tok in self.t.char_operators:
            return self.t.char_operators[tok]
        if tok.startswith("\\"):
            return self._render_command_word(tok)
        return tok  # numbers and single letters read as themselves

    def _render_command_word(self, tok):
        if tok in self.t.ignored:
            return ""
        if tok in self.t.words:
            return self.t.words[tok]
        if tok in self.t.symbols:
            return self.t.symbols[tok]
        if tok in self.t.functions:
            return self.t.functions[tok]
        if tok in self.t.big_operators:
            return self.t.big_operators[tok]
        # Unknown command: read its name so nothing is silently dropped.
        return tok[1:]

    def _handle_command(self, tok):
        self.i += 1  # consume the command token

        if tok in self.t.ignored:
            return

        if tok == r"\begin":
            self._handle_environment()
            return

        if tok in (r"\ce", r"\pu"):
            content = self._read_raw_arg()
            self._emit(C.translate_ce(content) if tok == r"\ce"
                       else C.translate_pu(content))
            return

        if tok in (r"\SI", r"\qty"):
            number = self._read_raw_arg()
            unit = self._read_raw_arg()
            self._emit(C.translate_si(number, unit))
            return

        if tok in (r"\si", r"\unit"):
            self._emit(C.translate_si("", self._read_raw_arg()))
            return

        if tok in self.t.accents:
            arg = self._read_arg()
            self._emit(f"{arg} {self.t.accents[tok]}".strip())
            return

        if tok in self.t.binary_templates:
            a = self._read_arg()
            b = self._read_arg()
            self._emit(self.t.binary_templates[tok].format(a=a, b=b))
            return

        if tok in self.t.unary_of:
            # \div is a divergence operator only when it has a braced argument;
            # otherwise it is the ordinary division sign.
            if tok == r"\div" and not self._next_is_brace():
                self._emit("divided by")
                return
            self._emit(f"{self.t.unary_of[tok]} {self._read_arg()}".strip())
            return

        if tok == r"\frac" or tok == r"\dfrac" or tok == r"\tfrac":
            num = self._read_arg()
            den = self._read_arg()
            self._emit(f"{num} over {den}")
            return

        if tok == r"\sqrt":
            self._skip_ws()
            index = None
            if self.i < len(self.tokens) and self.tokens[self.i] == "[":
                _, _, inner = self._collect_group()
                index = self.t._render(inner)
            radicand = self._read_arg()
            self._emit(_root_phrase(index, radicand))
            return

        if tok == r"\mathbb":
            self._emit(self._read_raw_arg())
            return

        if tok in self.t.font_commands:
            # Styled text/operator names: read the argument plainly.
            raw = self._read_raw_arg()
            self._emit(raw)
            return

        if tok in self.t.big_operators:
            # e.g. \sup A -> "the supremum of A"; the operand follows naturally.
            # Limits/bounds in scripts are read in place: "the sum from i
            # equals 1 to n of", "the limit as n goes to infinity of".
            sub, sup = self._read_operator_scripts()
            self._emit(_operator_phrase(tok, self.t.big_operators[tok], sub, sup))
            return

        if tok in self.t.functions:
            self._emit(self.t.functions[tok])
            return

        # Plain word-mapped or unknown command.
        self._emit(self._render_command_word(tok))

    def _read_operator_scripts(self):
        """Consume ``_{..}`` / ``^{..}`` (in either order) after an operator."""
        scripts = {}
        while True:
            self._skip_ws()
            if self.i < len(self.tokens) and self.tokens[self.i] in self.t.ignored:
                self.i += 1  # e.g. \limits
                continue
            if self.i >= len(self.tokens) or self.tokens[self.i] not in ("_", "^"):
                break
            kind = self.tokens[self.i]
            if kind in scripts:
                break
            self.i += 1
            scripts[kind] = self._read_arg().strip()
        return scripts.get("_"), scripts.get("^")

    def _apply_script(self, kind):
        """Attach a superscript (^) or subscript (_) to the previous part."""
        arg = self._read_arg()
        base = self.parts.pop() if self.parts else ""
        if kind == "^":
            self.parts.append(_power_phrase(base, arg))
        else:
            self.parts.append(f"{base} sub {arg}".strip())

    # -- grouped constructs ----------------------------------------------
    def _render_group(self, opener, closer, inner):
        if opener == "{":
            return self._render_set(inner)
        return self._render_bracketed(opener, closer, inner)

    def _render_set(self, inner):
        # Set-builder notation:  { x : predicate }  or  { x \mid predicate }.
        cond = _split_top(inner, {":", "|", r"\mid", r"\colon"})
        if len(cond) == 2:
            left = self.t._render(cond[0]).strip()
            right = self.t._render(cond[1]).strip()
            return f"the set of {left} such that {right}"
        body = self.t._render(inner).strip()
        if not body:
            return "the empty set"
        return f"the set {body}"

    def _render_bracketed(self, opener, closer, inner):
        parts = _split_top(inner, {","})
        if len(parts) == 2 and _is_simple(parts[0]) and _is_simple(parts[1]):
            low = self.t._render(parts[0]).strip()
            high = self.t._render(parts[1]).strip()
            return _interval_phrase(opener, closer, low, high)
        # Otherwise the delimiters are plain grouping; read the contents.
        return self.t._render(inner).strip()


_MATRIX_ENVS = {"matrix", "pmatrix", "bmatrix", "Bmatrix", "smallmatrix",
                "array", "tabular"}
_DET_ENVS = {"vmatrix", "Vmatrix"}


def _matrix_body(rows):
    return "; ".join(
        f"row {i + 1}: {', '.join(cols)}" for i, cols in enumerate(rows)
    )


# -- phrase builders ------------------------------------------------------
def _power_phrase(base, exponent):
    exp = exponent.strip()
    if exp == "2":
        return f"{base} squared"
    if exp == "3":
        return f"{base} cubed"
    if exp == "composed with":  # \circ, i.e. a degree sign: 90^\circ
        return f"{base} degrees"
    if exp in ("prime", "'"):
        return f"{base} prime"
    if exp in ("-1", "minus 1"):
        return f"{base} inverse"
    return f"{base} to the power of {exp}"


_LIMIT_OPS = {r"\lim", r"\limsup", r"\liminf"}
_RANGE_OPS = {r"\sum", r"\prod", r"\int", r"\oint"}


def _operator_phrase(tok, phrase, sub, sup):
    """Fold an operator's limits into its phrase, keeping the trailing "of"."""
    if not sub and not sup:
        return phrase
    head = phrase[:-len(" of")] if phrase.endswith(" of") else phrase
    if tok in _LIMIT_OPS and sub:
        return f"{head} as {sub} of"
    if tok in _RANGE_OPS and sub and sup:
        return f"{head} from {sub} to {sup} of"
    if tok in _RANGE_OPS and sup:
        return f"{head} up to {sup} of"
    return f"{head} over {sub} of"


def _root_phrase(index, radicand):
    if index is None:
        return f"the square root of {radicand}"
    index = index.strip()
    ordinals = {"2": "square", "3": "cube"}
    if index in ordinals:
        return f"the {ordinals[index]} root of {radicand}"
    return f"the {index}th root of {radicand}"


def _interval_phrase(opener, closer, low, high):
    left_closed = opener == "["
    right_closed = closer == "]"
    if left_closed and right_closed:
        kind = "closed interval"
    elif not left_closed and not right_closed:
        kind = "open interval"
    else:
        kind = "half-open interval"
    return f"the {kind} from {low} to {high}"


# -- token-list utilities -------------------------------------------------
def _split_top(tokens, separators):
    """Split a token list on top-level separator tokens (ignoring nesting)."""
    result = [[]]
    depth = 0
    for tok in tokens:
        if tok in _OPENERS:
            depth += 1
        elif tok in _CLOSERS:
            depth -= 1
        if depth == 0 and tok in separators:
            result.append([])
        else:
            result[-1].append(tok)
    return result


_SIMPLE_EXTRA = {r"\pi", r"\infty", "-", "+", ".", r"\sqrt"}


def _is_simple(tokens):
    """True if a token list is a single number/letter/constant (interval end)."""
    meaningful = [t for t in tokens if not _is_ws(t)]
    if not meaningful or len(meaningful) > 3:
        return False
    for tok in meaningful:
        if tok in _SIMPLE_EXTRA:
            continue
        if re.fullmatch(r"\d+(\.\d+)?", tok):
            continue
        if re.fullmatch(r"[A-Za-z]", tok):
            continue
        return False
    return True


# -- output cleanup -------------------------------------------------------
def _cleanup(text):
    text = re.sub(r"\s+", " ", text).strip()
    # No space before closing punctuation.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    # Collapse repeated / stray commas produced by trailing separators.
    text = re.sub(r"(,\s*)+", ", ", text)
    text = re.sub(r",\s*([.;:])", r"\1", text)
    text = re.sub(r"[\s,]+$", "", text)
    # Restore a trailing period if the source math ended a sentence.
    return text.strip()


_TRANSLATORS = {}


def _translator(mode):
    if mode not in _TRANSLATORS:
        _TRANSLATORS[mode] = MathTranslator(mode=mode)
    return _TRANSLATORS[mode]


def translate_fragment(latex, mode="math"):
    """Translate a bare LaTeX math fragment into spoken English.

    ``mode`` is one of ``"math"``, ``"physics"`` or ``"chemistry"``.  This is the
    low-level fragment engine; :func:`math_to_english.math2english` wraps it with
    document/prose handling and is the public entry point.
    """
    return _translator(mode).translate(latex)
