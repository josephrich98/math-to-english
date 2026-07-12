"""Lookup tables mapping LaTeX symbols and commands to spoken English.

These are intentionally kept as plain dictionaries so they are easy to read,
extend, and override (see ``MathTranslator`` in :mod:`math_to_english.translator`).

The spoken forms follow the convention that a professor reads relations
*without* a linking verb, e.g. ``a \\le b`` -> "a less than or equal to b"
(not "a is less than or equal to b").  This matches the phrasing requested for
the project and keeps chained relations readable.
"""

# Binary relations and set relations.
RELATIONS = {
    r"\le": "less than or equal to",
    r"\leq": "less than or equal to",
    r"\ge": "greater than or equal to",
    r"\geq": "greater than or equal to",
    r"\ne": "is not equal to",
    r"\neq": "is not equal to",
    r"\ll": "much less than",
    r"\gg": "much greater than",
    r"\equiv": "is equivalent to",
    r"\approx": "is approximately equal to",
    r"\simeq": "is approximately equal to",
    r"\sim": "is similar to",
    r"\cong": "is congruent to",
    r"\propto": "is proportional to",
    r"\doteq": "equals",
    r"\in": "in",
    r"\notin": "is not in",
    r"\ni": "contains",
    r"\subset": "is a proper subset of",
    r"\subsetneq": "is a proper subset of",
    r"\subseteq": "is a subset of",
    r"\supset": "is a proper superset of",
    r"\supseteq": "is a superset of",
    r"\perp": "is perpendicular to",
    r"\parallel": "is parallel to",
    r"\mid": "such that",
    r"\to": "goes to",
    r"\rightarrow": "goes to",
    r"\longrightarrow": "goes to",
    r"\mapsto": "maps to",
    r"\Rightarrow": "implies",
    r"\implies": "implies",
    r"\Leftarrow": "is implied by",
    r"\Leftrightarrow": "if and only if",
    r"\iff": "if and only if",
    r"\uparrow": "increases",
    r"\downarrow": "decreases",
    r"\nearrow": "increases to",
    r"\searrow": "decreases to",
}

# Binary operators and connectives.
OPERATORS = {
    r"\times": "times",
    r"\cdot": "times",
    r"\div": "divided by",
    r"\pm": "plus or minus",
    r"\mp": "minus or plus",
    r"\ast": "star",
    r"\star": "star",
    r"\circ": "composed with",
    r"\cup": "union",
    r"\cap": "intersection",
    r"\setminus": "minus",
    r"\oplus": "direct sum",
    r"\otimes": "tensor product",
    r"\wedge": "and",
    r"\land": "and",
    r"\vee": "or",
    r"\lor": "or",
    r"\neg": "not",
    r"\lnot": "not",
}

# Standalone symbols / named constants.
SYMBOLS = {
    r"\infty": "infinity",
    r"\emptyset": "the empty set",
    r"\varnothing": "the empty set",
    r"\forall": "for all",
    r"\exists": "there exists",
    r"\nexists": "there does not exist",
    r"\partial": "partial",
    r"\nabla": "del",
    r"\angle": "angle",
    r"\dots": "and so on",
    r"\ldots": "and so on",
    r"\cdots": "and so on",
    r"\vdots": "and so on",
    r"\ddots": "and so on",
    r"\prime": "prime",
    r"\aleph": "aleph",
    r"\hbar": "h bar",
    r"\ell": "l",
    r"\Re": "the real part of",
    r"\Im": "the imaginary part of",
}

# Named operators that take an operand read as "the ... of".
BIG_OPERATORS = {
    r"\sup": "the supremum of",
    r"\inf": "the infimum of",
    r"\max": "the maximum of",
    r"\min": "the minimum of",
    r"\lim": "the limit of",
    r"\limsup": "the limit superior of",
    r"\liminf": "the limit inferior of",
    r"\sum": "the sum of",
    r"\prod": "the product of",
    r"\int": "the integral of",
    r"\oint": "the contour integral of",
    r"\gcd": "the greatest common divisor of",
    r"\det": "the determinant of",
    r"\dim": "the dimension of",
    r"\deg": "the degree of",
    r"\ker": "the kernel of",
}

# Named functions read as their own name.
FUNCTIONS = {
    r"\log": "log",
    r"\ln": "natural log",
    r"\lg": "log base 2",
    r"\exp": "exponential of",
    r"\sin": "sine",
    r"\cos": "cosine",
    r"\tan": "tangent",
    r"\cot": "cotangent",
    r"\sec": "secant",
    r"\csc": "cosecant",
    r"\arcsin": "arcsine",
    r"\arccos": "arccosine",
    r"\arctan": "arctangent",
    r"\sinh": "hyperbolic sine",
    r"\cosh": "hyperbolic cosine",
    r"\tanh": "hyperbolic tangent",
}

# Greek letters (lower and upper case).
GREEK = {
    r"\alpha": "alpha",
    r"\beta": "beta",
    r"\gamma": "gamma",
    r"\delta": "delta",
    r"\epsilon": "epsilon",
    r"\varepsilon": "epsilon",
    r"\zeta": "zeta",
    r"\eta": "eta",
    r"\theta": "theta",
    r"\vartheta": "theta",
    r"\iota": "iota",
    r"\kappa": "kappa",
    r"\lambda": "lambda",
    r"\mu": "mu",
    r"\nu": "nu",
    r"\xi": "xi",
    r"\pi": "pi",
    r"\varpi": "pi",
    r"\rho": "rho",
    r"\varrho": "rho",
    r"\sigma": "sigma",
    r"\varsigma": "sigma",
    r"\tau": "tau",
    r"\upsilon": "upsilon",
    r"\phi": "phi",
    r"\varphi": "phi",
    r"\chi": "chi",
    r"\psi": "psi",
    r"\omega": "omega",
    r"\Gamma": "capital gamma",
    r"\Delta": "capital delta",
    r"\Theta": "capital theta",
    r"\Lambda": "capital lambda",
    r"\Xi": "capital xi",
    r"\Pi": "capital pi",
    r"\Sigma": "capital sigma",
    r"\Upsilon": "capital upsilon",
    r"\Phi": "capital phi",
    r"\Psi": "capital psi",
    r"\Omega": "capital omega",
}

# Single-character operators / punctuation read literally.
CHAR_OPERATORS = {
    "=": "equals",
    "+": "plus",
    "-": "minus",
    "<": "less than",
    ">": "greater than",
    "*": "times",
    "/": "over",
    "!": "factorial",
    "'": "prime",
}

# Commands that are purely for spacing or layout and should be dropped.
IGNORED = {
    r"\quad",
    r"\qquad",
    r"\,",
    r"\;",
    r"\:",
    r"\!",
    r"\ ",
    r"\left",
    r"\right",
    r"\bigl",
    r"\bigr",
    r"\Bigl",
    r"\Bigr",
    r"\displaystyle",
    r"\textstyle",
    r"\limits",
    r"\nolimits",
}

# Commands whose single argument is styled text but read plainly.
FONT_COMMANDS = {
    r"\mathrm",
    r"\mathbf",
    r"\mathit",
    r"\mathsf",
    r"\mathtt",
    r"\mathcal",
    r"\mathscr",
    r"\mathfrak",
    r"\boldsymbol",
    r"\bm",
    r"\operatorname",
    r"\text",
    r"\textrm",
    r"\textbf",
    r"\textit",
}


# Accents: command -> spoken suffix appended to the argument.
# e.g. \hat{x} -> "x hat",  \vec{v} -> "v vector".
ACCENTS = {
    r"\vec": "vector",
    r"\overrightarrow": "vector",
    r"\overleftarrow": "vector",
    r"\hat": "hat",
    r"\widehat": "hat",
    r"\bar": "bar",
    r"\overline": "bar",
    r"\underline": "underline",
    r"\dot": "dot",
    r"\ddot": "double dot",
    r"\dddot": "triple dot",
    r"\tilde": "tilde",
    r"\widetilde": "tilde",
    r"\check": "check",
    r"\breve": "breve",
    r"\mathring": "ring",
}

# Commands taking one braced argument, read as "PHRASE of ARG".
UNARY_OF = {
    r"\abs": "the absolute value of",
    r"\norm": "the norm of",
    r"\floor": "the floor of",
    r"\ceil": "the ceiling of",
}

# Physics-package commands taking one argument, read as "PHRASE of ARG".
PHYSICS_UNARY_OF = {
    r"\grad": "the gradient of",
    r"\gradient": "the gradient of",
    r"\div": "the divergence of",
    r"\divergence": "the divergence of",
    r"\curl": "the curl of",
    r"\laplacian": "the Laplacian of",
    r"\bra": "the bra",
    r"\ket": "the ket",
    r"\Tr": "the trace of",
    r"\trace": "the trace of",
    r"\rank": "the rank of",
    r"\eval": "evaluated",
}

# Commands taking two braced arguments, read from a template.
BINARY_TEMPLATES = {
    r"\binom": "{a} choose {b}",
    r"\dbinom": "{a} choose {b}",
    r"\tbinom": "{a} choose {b}",
}

PHYSICS_BINARY_TEMPLATES = {
    r"\dv": "the derivative of {a} with respect to {b}",
    r"\pdv": "the partial derivative of {a} with respect to {b}",
    r"\comm": "the commutator of {a} and {b}",
    r"\acomm": "the anticommutator of {a} and {b}",
    r"\pb": "the Poisson bracket of {a} and {b}",
    r"\braket": "the inner product of {a} and {b}",
    r"\ip": "the inner product of {a} and {b}",
    r"\expval": "the expectation value of {a}",
    r"\ev": "the expectation value of {a}",
    r"\order": "order {a}",
}

# Extra constants/symbols enabled in physics mode.
PHYSICS_SYMBOLS = {
    r"\hbar": "h bar",
    r"\degree": "degrees",
    r"\ang": "degrees",
    r"\odot": "sun",
    r"\oplus": "earth",
}


def combined_word_map():
    """Return a single dict of every command that maps to a fixed phrase."""
    merged = {}
    for table in (RELATIONS, OPERATORS, SYMBOLS, GREEK):
        merged.update(table)
    return merged
