"""Tests for math_to_english."""

import pytest

from math_to_english import translate_math, to_english, looks_like_math


# -- core fragment translation -------------------------------------------
@pytest.mark.parametrize(
    "latex, expected",
    [
        (r"a \le b \quad \text{and} \quad b \le a",
         "a less than or equal to b and b less than or equal to a"),
        (r"a \le b \quad \text{or} \quad b \le a",
         "a less than or equal to b or b less than or equal to a"),
        (r"a = b", "a equals b"),
        (r"a \in S", "a in S"),
        (r"1 \notin A", "1 is not in A"),
        (r"A \subseteq S", "A is a subset of S"),
        (r"s = \sup A", "s equals the supremum of A"),
        (r"\sqrt{2}", "the square root of 2"),
        (r"q^2 < 2", "q squared less than 2"),
        (r"x^3", "x cubed"),
        (r"x^{n+1}", "x to the power of n plus 1"),
        (r"\frac{a}{b}", "a over b"),
        (r"\mathbb{R}", "R"),
        (r"x_{i}", "x sub i"),
    ],
)
def test_translate_math(latex, expected):
    assert translate_math(latex) == expected


# -- intervals and sets ---------------------------------------------------
def test_open_interval():
    assert translate_math(r"A=(0,1)") == "A equals the open interval from 0 to 1"


def test_closed_interval():
    assert translate_math(r"A=[0,1]") == "A equals the closed interval from 0 to 1"


def test_set_roster():
    assert translate_math(r"A={1,2,3}") == "A equals the set 1, 2, 3"


def test_set_builder():
    assert (
        translate_math(r"{q \in \mathbb Q : q^2 < 2}")
        == "the set of q in Q such that q squared less than 2"
    )


def test_dots_in_list():
    assert translate_math(r"1,2,10,\dots") == "1, 2, 10, and so on"


# -- inline detection heuristic ------------------------------------------
@pytest.mark.parametrize(
    "inner, is_math",
    [
        (r"\le", True),
        ("S", True),
        ("1000", True),
        ("0,1", True),
        ("a \\in S", True),
        ("or totally ordered set", False),
        ("also called the supremum", False),
    ],
)
def test_looks_like_math(inner, is_math):
    assert looks_like_math(inner) is is_math


# -- document-level conversion -------------------------------------------
def test_inline_math_in_prose():
    text = "An element (u \\in S) is an **upper bound** of (A)."
    assert to_english(text) == "An element u in S is an upper bound of A."


def test_english_parenthetical_preserved():
    text = "An ordered set (or totally ordered set) is a set (S)."
    assert to_english(text) == "An ordered set (or totally ordered set) is a set S."


def test_display_block():
    text = "If\n[\na \\le b \\quad \\text{and} \\quad b \\le a,\n]\nthen"
    result = to_english(text)
    assert "a less than or equal to b and b less than or equal to a" in result


def test_standard_delimiters():
    assert to_english(r"We know $a \le b$ here.") == "We know a less than or equal to b here."
    assert to_english(r"Then \(x^2\) is positive.") == "Then x squared is positive."


# -- function application -------------------------------------------------
@pytest.mark.parametrize(
    "latex, expected",
    [
        (r"f(x)", "f of x"),
        (r"f(x) = x^2 + 1", "f of x equals x squared plus 1"),
        (r"f(x,y)", "f of x, y"),
        (r"\sin(x)", "sine of x"),
        (r"2(x+1)", "2 x plus 1"),  # coefficient, not a function
    ],
)
def test_function_application(latex, expected):
    assert translate_math(latex) == expected


# -- accents, binomials, primes ------------------------------------------
@pytest.mark.parametrize(
    "latex, expected",
    [
        (r"\vec{v}", "v vector"),
        (r"\hat{x}", "x hat"),
        (r"\bar{y}", "y bar"),
        (r"\ddot{x}", "x double dot"),
        (r"\binom{n}{k}", "n choose k"),
        (r"90^\circ", "90 degrees"),
        (r"x^{-1}", "x inverse"),
    ],
)
def test_accents_and_scripts(latex, expected):
    assert translate_math(latex) == expected


# -- matrices and environments -------------------------------------------
def test_matrix():
    latex = r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}"
    assert translate_math(latex) == "the matrix with row 1: a, b; row 2: c, d"


def test_cases():
    latex = r"\begin{cases} x & \text{if } x>0 \\ -x & \text{if } x<0 \end{cases}"
    result = translate_math(latex)
    assert "x if x greater than 0" in result
    assert "minus x if x less than 0" in result


# -- physics mode ---------------------------------------------------------
@pytest.mark.parametrize(
    "latex, expected",
    [
        (r"\dv{f}{x}", "the derivative of f with respect to x"),
        (r"\pdv{f}{x}", "the partial derivative of f with respect to x"),
        (r"\grad{\phi}", "the gradient of phi"),
        (r"\comm{A}{B}", "the commutator of A and B"),
        (r"\braket{\phi}{\psi}", "the inner product of phi and psi"),
        (r"\SI{9.8}{m/s^2}", "9.8 meters per second squared"),
    ],
)
def test_physics_mode(latex, expected):
    assert translate_math(latex, mode="physics") == expected


def test_div_is_operator_in_math_mode():
    assert translate_math(r"a \div b") == "a divided by b"


# -- chemistry mode -------------------------------------------------------
@pytest.mark.parametrize(
    "latex, expected",
    [
        (r"\ce{H+}", "H plus"),
        (r"\ce{H2O}", "H 2 O"),
        (r"\ce{2H2 + O2 -> 2H2O}", "2 H 2 plus O 2 yields 2 H 2 O"),
        (r"\ce{N2 + 3H2 <=> 2NH3}", "N 2 plus 3 H 2 is in equilibrium with 2 N H 3"),
        (r"\ce{SO4^2-}", "S O 4 2 minus"),
        (r"\ce{NaCl}", "sodium chlorine"),
        (r"\pu{123 kJ//mol}", "123 kilojoules per mole"),
    ],
)
def test_chemistry_mode(latex, expected):
    assert translate_math(latex, mode="chemistry") == expected


def test_embedded_ce_in_prose():
    doc = r"The reaction \ce{2H2 + O2 -> 2H2O} is exothermic."
    assert to_english(doc, mode="chemistry") == (
        "The reaction 2 H 2 plus O 2 yields 2 H 2 O is exothermic."
    )


def test_invalid_mode():
    with pytest.raises(ValueError):
        translate_math("x", mode="biology")
