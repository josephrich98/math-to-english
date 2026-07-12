"""Read mhchem-style chemistry notation (``\\ce{...}``, ``\\pu{...}``) aloud.

Chemists dictate formulas element-by-element: ``H2O`` is spoken "H 2 O" and
``SO4^2-`` is "S O 4, 2 minus".  Single-letter element symbols are read as the
letter (a chemist says "C", "O", "H"); multi-letter symbols are read by name
(``Na`` -> "sodium", ``Cl`` -> "chlorine"), which is far clearer over audio.
"""

import re

__all__ = ["translate_ce", "translate_pu"]

# Element symbol -> spoken name (multi-letter symbols benefit most from this).
PERIODIC_TABLE = {
    "H": "hydrogen", "He": "helium", "Li": "lithium", "Be": "beryllium",
    "B": "boron", "C": "carbon", "N": "nitrogen", "O": "oxygen",
    "F": "fluorine", "Ne": "neon", "Na": "sodium", "Mg": "magnesium",
    "Al": "aluminium", "Si": "silicon", "P": "phosphorus", "S": "sulfur",
    "Cl": "chlorine", "Ar": "argon", "K": "potassium", "Ca": "calcium",
    "Sc": "scandium", "Ti": "titanium", "V": "vanadium", "Cr": "chromium",
    "Mn": "manganese", "Fe": "iron", "Co": "cobalt", "Ni": "nickel",
    "Cu": "copper", "Zn": "zinc", "Ga": "gallium", "Ge": "germanium",
    "As": "arsenic", "Se": "selenium", "Br": "bromine", "Kr": "krypton",
    "Rb": "rubidium", "Sr": "strontium", "Y": "yttrium", "Zr": "zirconium",
    "Nb": "niobium", "Mo": "molybdenum", "Tc": "technetium", "Ru": "ruthenium",
    "Rh": "rhodium", "Pd": "palladium", "Ag": "silver", "Cd": "cadmium",
    "In": "indium", "Sn": "tin", "Sb": "antimony", "Te": "tellurium",
    "I": "iodine", "Xe": "xenon", "Cs": "caesium", "Ba": "barium",
    "La": "lanthanum", "Ce": "cerium", "Pr": "praseodymium", "Nd": "neodymium",
    "Pm": "promethium", "Sm": "samarium", "Eu": "europium", "Gd": "gadolinium",
    "Tb": "terbium", "Dy": "dysprosium", "Ho": "holmium", "Er": "erbium",
    "Tm": "thulium", "Yb": "ytterbium", "Lu": "lutetium", "Hf": "hafnium",
    "Ta": "tantalum", "W": "tungsten", "Re": "rhenium", "Os": "osmium",
    "Ir": "iridium", "Pt": "platinum", "Au": "gold", "Hg": "mercury",
    "Tl": "thallium", "Pb": "lead", "Bi": "bismuth", "Po": "polonium",
    "At": "astatine", "Rn": "radon", "Fr": "francium", "Ra": "radium",
    "Ac": "actinium", "Th": "thorium", "Pa": "protactinium", "U": "uranium",
    "Np": "neptunium", "Pu": "plutonium", "Am": "americium", "Cm": "curium",
    "Bk": "berkelium", "Cf": "californium", "Es": "einsteinium",
    "Fm": "fermium", "Md": "mendelevium", "No": "nobelium", "Lr": "lawrencium",
}

# Reaction arrows.
ARROWS = {
    "->": "yields",
    "\\rightarrow": "yields",
    "<-": "is produced from",
    "<=>": "is in equilibrium with",
    "<=>>": "is in equilibrium with",
    "<<=>": "is in equilibrium with",
    "<->": "resonates with",
    "=>": "yields",
}

STATES = {
    "(aq)": "aqueous",
    "(s)": "solid",
    "(l)": "liquid",
    "(g)": "gas",
}

_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_to_int(text):
    total = 0
    prev = 0
    for ch in reversed(text):
        val = _ROMAN.get(ch, 0)
        if val < prev:
            total -= val
        else:
            total += val
            prev = val
    return total


def _element_name(symbol):
    if len(symbol) == 1:
        # Single-letter symbols are dictated as the letter itself.
        return symbol
    return PERIODIC_TABLE.get(symbol, " ".join(symbol))


def _charge_phrase(number, sign):
    word = "plus" if sign == "+" else "minus"
    if number and number != "1":
        return f"{number} {word}"
    return word


def _parse_formula(token):
    """Render a single chemical species such as ``SO4^2-`` or ``Ca^2+``."""
    words = []

    # Trailing charge written plainly, e.g. H+, Ca2+, SO4^2-, Fe^{3+}.
    charge = None
    m = re.search(r"\^?\{?(\d*)([+-])\}?$", token)
    if m and (m.group(1) or token[m.start()] in "^{" or len(token) <= 3
              or token[m.start() - 1].isdigit() is False):
        # Only treat as a charge when it really terminates the species.
        core = token[: m.start()]
        if core and (core[-1].isalpha() or core[-1] in ")]}" or core[-1].isdigit()):
            charge = _charge_phrase(m.group(1), m.group(2))
            token = core

    i = 0
    while i < len(token):
        ch = token[i]
        # Oxidation state or superscript, e.g. ^{III} or ^{2-}.
        if ch == "^":
            j = i + 1
            if j < len(token) and token[j] == "{":
                end = token.find("}", j)
                content = token[j + 1:end] if end != -1 else token[j + 1:]
                i = end + 1 if end != -1 else len(token)
            else:
                content = ""
                while j < len(token) and (token[j].isalnum() or token[j] in "+-"):
                    content += token[j]
                    j += 1
                i = j
            words.append(_superscript_phrase(content))
            continue
        if ch.isupper():
            sym = ch
            if i + 1 < len(token) and token[i + 1].islower():
                sym += token[i + 1]
                i += 2
            else:
                i += 1
            words.append(_element_name(sym))
            continue
        if ch.isdigit():
            num = ""
            while i < len(token) and token[i].isdigit():
                num += token[i]
                i += 1
            words.append(num)
            continue
        if ch == "=":
            words.append("double bond")
            i += 1
            continue
        if ch == "#":
            words.append("triple bond")
            i += 1
            continue
        if ch in "().[]{}":
            i += 1
            continue
        if ch in "-·.":
            i += 1  # single bond / hydrate dot: read as a slight pause
            continue
        i += 1  # skip anything unrecognised

    if charge:
        words.append(charge)
    return " ".join(w for w in words if w)


def _superscript_phrase(content):
    content = content.strip("{}")
    if not content:
        return ""
    if re.fullmatch(r"[IVXLCDM]+", content):
        return str(_roman_to_int(content))
    m = re.fullmatch(r"(\d*)([+-])", content)
    if m:
        return _charge_phrase(m.group(1), m.group(2))
    return content


def translate_ce(content):
    """Translate the body of a ``\\ce{...}`` chemical expression."""
    content = content.strip()
    words = []
    for token in content.split():
        if token in ARROWS:
            words.append(ARROWS[token])
        elif token.startswith("->[") or token.startswith("<=>["):
            arrow, _, rest = token.partition("[")
            cond = rest.rstrip("]")
            words.append(ARROWS.get(arrow, "yields"))
            words.append(f"in the presence of {_parse_formula(cond)}")
        elif token == "+":
            words.append("plus")
        elif token in STATES:
            words.append(token[1:-1] if token in STATES else token)
            words[-1] = STATES[token]
        elif token == "v":
            words.append("precipitate")
        elif token == "^":
            words.append("gas")
        else:
            words.append(_parse_formula(token))
    return " ".join(w for w in words if w)


# ---- physical units (\pu and, loosely, siunitx) -------------------------
_UNIT_NAMES = {
    "m": "meter", "km": "kilometer", "cm": "centimeter", "mm": "millimeter",
    "nm": "nanometer", "s": "second", "ms": "millisecond", "min": "minute",
    "h": "hour", "hr": "hour", "g": "gram", "kg": "kilogram", "mg": "milligram",
    "mol": "mole", "L": "liter", "mL": "milliliter", "J": "joule",
    "kJ": "kilojoule", "cal": "calorie", "kcal": "kilocalorie", "N": "newton",
    "Pa": "pascal", "kPa": "kilopascal", "atm": "atmosphere", "bar": "bar",
    "K": "kelvin", "C": "coulomb", "V": "volt", "A": "ampere", "W": "watt",
    "Hz": "hertz", "eV": "electron volt", "T": "tesla", "F": "farad",
    "ohm": "ohm", "rad": "radian", "deg": "degree",
}

_SI_PREFIX = {
    "\\kilo": "kilo", "\\milli": "milli", "\\micro": "micro", "\\nano": "nano",
    "\\centi": "centi", "\\mega": "mega", "\\giga": "giga",
}
_SI_UNIT = {
    "\\metre": "meter", "\\meter": "meter", "\\second": "second",
    "\\gram": "gram", "\\mole": "mole", "\\kelvin": "kelvin",
    "\\ampere": "ampere", "\\newton": "newton", "\\joule": "joule",
    "\\watt": "watt", "\\pascal": "pascal", "\\volt": "volt",
    "\\hertz": "hertz", "\\ohm": "ohm", "\\litre": "liter", "\\liter": "liter",
    "\\per": "per", "\\squared": "squared", "\\cubed": "cubed",
}


def _unit_word(unit, plural):
    name = _UNIT_NAMES.get(unit, unit)
    if plural and name not in ("per",) and not name.endswith("s"):
        name += "s"
    return name


def _render_unit_expr(expr, plural):
    # mhchem uses // or / for "per"; a leading number scales pluralisation.
    expr = expr.replace("//", "/")
    words = []
    for idx, part in enumerate(expr.split("/")):
        if idx > 0:
            words.append("per")
        part = part.strip()
        m = re.fullmatch(r"([A-Za-z]+)\^?(\d+)?", part)
        if not m:
            words.append(part)
            continue
        base = _unit_word(m.group(1), plural and idx == 0)
        words.append(base)
        if m.group(2) == "2":
            words.append("squared")
        elif m.group(2) == "3":
            words.append("cubed")
        elif m.group(2):
            words.append(f"to the power of {m.group(2)}")
    return " ".join(words)


def translate_pu(content):
    """Translate ``\\pu{...}`` physical-unit notation, e.g. ``123 kJ//mol``."""
    content = content.strip()
    m = re.match(r"([\d.,]+(?:\s*[eE]?[-+]?\d+)?)\s*(.*)", content)
    if m and m.group(2):
        number = m.group(1).strip()
        plural = number not in ("1",)
        return f"{number} {_render_unit_expr(m.group(2), plural)}".strip()
    return _render_unit_expr(content, True)


def translate_si(number, unit):
    """Loosely translate siunitx ``\\SI{number}{unit}`` and ``\\si{unit}``."""
    tokens = re.findall(r"\\[a-zA-Z]+|[A-Za-z]+|\^?\d+|/|//", unit)
    plural = number not in ("", "1")  # only the leading (numerator) unit
    words = []
    pending_prefix = ""
    for tok in tokens:
        if tok in _SI_PREFIX:
            pending_prefix = _SI_PREFIX[tok]
        elif tok in _SI_UNIT:
            base = _SI_UNIT[tok]
            if base in ("per", "squared", "cubed"):
                words.append(base)
            else:
                words.append(pending_prefix + base + ("s" if plural else ""))
                pending_prefix = ""
                plural = False
        elif tok in ("/", "//"):
            words.append("per")
            plural = False
        elif re.fullmatch(r"\^?\d+", tok):
            n = tok.lstrip("^")
            words.append("squared" if n == "2" else "cubed" if n == "3" else f"to the power of {n}")
        else:
            words.append(_render_unit_expr(tok, plural))
            plural = False
    unit_words = " ".join(w for w in words if w)
    return f"{number} {unit_words}".strip() if number else unit_words
