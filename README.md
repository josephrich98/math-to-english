# math-to-english

Convert text that contains LaTeX math into **plain English**, so a
text-to-speech engine (like the ones in ChatGPT or Claude) can dictate the math
the way a professor would read it aloud.

```text
a \le b \quad \text{and} \quad b \le a
        ↓
a less than or equal to b and b less than or equal to a
```

## Install

```bash
pip install -e .
```

## Usage

### Library

```python
from math_to_english import translate_math, to_english

# Translate a bare LaTeX fragment:
translate_math(r"s = \sup A")           # -> "s equals the supremum of A"
translate_math(r"A = \{q \in \mathbb Q : q^2 < 2\}")
# -> "A equals the set of q in Q such that q squared less than 2"

# Convert a whole document (prose + math) for TTS:
to_english("An element (u \\in S) is an upper bound of (A).")
# -> "An element u in S is an upper bound of A."
```

### Command line

```bash
math2english testfile.md                 # convert a document
math2english --math -                     # translate one LaTeX fragment from stdin
echo 'a \le b' | math2english --math -
cat notes.md | math2english               # read from stdin
math2english reactions.md --mode chemistry
```

## Modes

Pass `mode=` (API) or `--mode` (CLI) to select the vocabulary:

| Mode | Adds | Example |
|------|------|---------|
| `math` *(default)* | core relations, structures, sets, intervals | `a \le b` → "a less than or equal to b" |
| `physics` | vectors, derivatives, grad/div/curl, bra-ket, units | `\dv{f}{x}` → "the derivative of f with respect to x" |
| `chemistry` | `\ce{...}` formulas, ions, reaction arrows, `\pu{...}` units | `\ce{2H2 + O2 -> 2H2O}` → "2 H 2 plus O 2 yields 2 H 2 O" |

```python
translate_math(r"\ce{SO4^2-}", mode="chemistry")   # "S O 4 2 minus"
translate_math(r"\ce{H+}",     mode="chemistry")   # "H plus"
translate_math(r"\grad{\phi}", mode="physics")     # "the gradient of phi"
```

`\ce{...}`, `\pu{...}` and `\SI{}{}` are recognised even outside math
delimiters, so ordinary chemistry prose works. Single-letter element symbols are
read as the letter (`H`, `O`, `C`); multi-letter symbols by name
(`Na` → "sodium", `Cl` → "chlorine").

## What it handles

- **Relations & operators:** `\le`, `\ge`, `\ne`, `\in`, `\notin`,
  `\subseteq`, `\subset`, `\cup`, `\cap`, `=`, `<`, `>`, `\pm`, `\times`, …
- **Structures:** fractions (`\frac{a}{b}` → "a over b"), roots
  (`\sqrt{2}` → "the square root of 2"), powers (`x^2` → "x squared",
  `x^{n+1}` → "x to the power of n plus 1"), subscripts (`x_i` → "x sub i"),
  binomials (`\binom{n}{k}` → "n choose k").
- **Function application:** `f(x)` → "f of x", `\sin(x)` → "sine of x".
- **Accents:** `\vec{v}` → "v vector", `\hat{x}` → "x hat", `\bar{y}` → "y bar",
  `\dot{x}` → "x dot", `\ddot{x}` → "x double dot", `f'` → "f prime".
- **Matrices & environments:** `\begin{pmatrix} a & b \\ c & d \end{pmatrix}`
  → "the matrix with row 1: a, b; row 2: c, d"; also `cases`, `align`, …
- **Sets & intervals:** `(0,1)` → "the open interval from 0 to 1",
  `[0,1]` → "the closed interval from 0 to 1",
  `{1,2,3}` → "the set 1, 2, 3", set-builder `{x : P}` → "the set of x such that P".
- **Greek letters, named functions** (`\sin`, `\log`, …) and **big operators**
  (`\sup`, `\lim`, `\sum`, …).
- **`\text{...}`** is read as literal words; spacing commands (`\quad`, `\,`,
  `\;`) are dropped.

## Math delimiters

Both standard LaTeX and the "backslash-stripped" form that chat assistants
often emit are recognised:

| Style | Inline | Display |
|-------|--------|---------|
| Standard LaTeX | `$...$`, `\(...\)` | `$$...$$`, `\[...\]` |
| Backslash-stripped markdown | `(...)` | a standalone `[` … `]` block |

Because bare parentheses are also ordinary punctuation, `(...)` is only
translated when its contents *look like math* — asides such as
`(or totally ordered set)` are left untouched.

Markdown emphasis (`**bold**`, headings, bullets) is stripped by default so it
is not spoken; pass `--keep-markdown` (CLI) or `strip_markdown=False` (API) to
keep it.

## Customising the vocabulary

Every mapping lives in `math_to_english/symbols.py`. To override a phrase for a
single job, copy the translator and edit its tables:

```python
from math_to_english import MathTranslator
t = MathTranslator()
t.words[r"\gg"] = "way bigger than"
t.translate(r"n \gg 1")   # -> "n way bigger than 1"
```

## Development

```bash
pip install pytest
pytest
```
