"""math_to_english: read text containing LaTeX math aloud like a professor.

Convert documents (or bare LaTeX fragments) that mix prose and math notation
into plain English suitable for text-to-speech.

    >>> from math_to_english import math2english
    >>> math2english(r"a \\le b \\quad \\text{and} \\quad b \\le a")
    'a less than or equal to b and b less than or equal to a'

    >>> math2english("An element (u \\in S) is an upper bound.")
    'An element u in S is an upper bound.'
"""

from .translator import MathTranslator, translate_fragment, MODES
from .document import DocumentConverter, math2english, looks_like_math

__version__ = "0.2.0"

__all__ = [
    "math2english",
    "MathTranslator",
    "DocumentConverter",
    "looks_like_math",
    "translate_fragment",
    "MODES",
    "__version__",
]
