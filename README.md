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
git clone git@github.com:josephrich98/math-to-english.git
cd math-to-english
pip install .
```

## Usage

### Library

```python
from math_to_english import math2english

# Translate a bare LaTeX fragment:
math2english(r"s = \sup A")  # -> "s equals the supremum of A"
math2english(r"A = \{q \in \mathbb Q : q^2 < 2\}")  # -> "A equals the set of q in Q such that q squared less than 2"

# Convert a whole document (prose + math) for TTS:
math2english("An element (u \\in S) is an upper bound of (A).")
# -> "An element u in S is an upper bound of A."
```

### Command line

```bash
math2english math_doc.md                 # convert a document file
math2english "q \in \mathbb Q"           # translate a bare LaTeX fragment
math2english math_doc.md --dictate       # also speak the result aloud
```

## Modes

Pass `mode=` (API) or `--mode` (CLI) to select the vocabulary:

| Mode | Adds | Example |
|------|------|---------|
| `math` *(default)* | core relations, structures, sets, intervals | `a \le b` → "a less than or equal to b" |
| `physics` | vectors, derivatives, grad/div/curl, bra-ket, units | `\dv{f}{x}` → "the derivative of f with respect to x" |
| `chemistry` | `\ce{...}` formulas, ions, reaction arrows, `\pu{...}` units | `\ce{2H2 + O2 -> 2H2O}` → "2 H 2 plus O 2 yields 2 H 2 O" |

```python
math2english(r"\ce{H+}",     mode="chemistry")   # "H plus"
math2english(r"\grad{\phi}", mode="physics")     # "the gradient of phi"
```

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
