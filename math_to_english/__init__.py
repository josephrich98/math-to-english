"""math_to_english: read text containing LaTeX math aloud like a professor.

Convert documents (or bare LaTeX fragments) that mix prose and math notation
into plain English suitable for text-to-speech.

    >>> from math_to_english import translate_math
    >>> translate_math(r"a \\le b \\quad \\text{and} \\quad b \\le a")
    'a less than or equal to b and b less than or equal to a'

    >>> from math_to_english import to_english
    >>> to_english("An element (u \\in S) is an upper bound.")
    'An element u in S is an upper bound.'
"""

from .translator import MathTranslator, translate_math, MODES
from .document import DocumentConverter, to_english, looks_like_math

__version__ = "0.2.0"

__all__ = [
    "translate_math",
    "to_english",
    "MathTranslator",
    "DocumentConverter",
    "looks_like_math",
    "MODES",
    "__version__",
]
