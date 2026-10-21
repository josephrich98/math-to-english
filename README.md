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
math2english math_doc.md --annotate      # keep the math, add "In words: ..."
```

### Annotate: keep the math, add the words

`--annotate` (or `annotate=True`) leaves every expression exactly as written and
follows it with its reading, so the document still renders correctly but can
also be read aloud. Display math gets an `In words:` line; non-trivial inline
math gets a parenthetical (single symbols like `$x$` are left alone):

```text
For every $q \in \mathbb Q$ we have
$$
s = \sup A
$$
        ↓
For every $q \in \mathbb Q$ (in words: q in Q) we have
$$
s = \sup A
$$
In words: s equals the supremum of A.
```

## Agent skill (Claude Code, Codex, ...)

[`skills/math-in-words/SKILL.md`](skills/math-in-words/SKILL.md) is an
[Agent Skill](https://agentskills.io) that makes a coding agent answer in the
annotated style above: correct math, followed by "In words: ...". It uses the
`math2english` CLI to check readings and to convert existing documents when it
is installed, and falls back to its own reading table when it is not.

```bash
# Claude Code (all projects)
mkdir -p ~/.claude/skills && ln -s "$PWD/skills/math-in-words" ~/.claude/skills/math-in-words

# Codex
mkdir -p ~/.codex/skills && ln -s "$PWD/skills/math-in-words" ~/.codex/skills/math-in-words
```

The agent picks the skill up when you ask for math "in words" or for answers
you can listen to, or you can call it directly with `/math-in-words`. To get
this style in every answer, add a line such as "Follow the math-in-words skill
whenever you write math" to your `CLAUDE.md` / `AGENTS.md`.

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
