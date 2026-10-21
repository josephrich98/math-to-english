---
name: math-in-words
description: Write math normally (LaTeX that renders correctly) and follow every non-trivial expression with how it is read aloud ("In words: ..."), so the answer both displays properly and can be listened to with text-to-speech. Use when the user asks for math "in words", for answers they can listen to or dictate, for TTS- or screen-reader-friendly math, or invokes /math-in-words. Also converts an existing Markdown/LaTeX document the same way with the math2english CLI.
---

# Math in words

Keep the math exactly as you would normally write it, then say it in English
right after, the way a professor reads a board aloud. The reader sees correct
notation; a text-to-speech engine (or a listener) gets plain English.

## Format

**Display math** — put an `In words:` line directly after the block:

```markdown
$$
s = \sup A
$$
In words: s equals the supremum of A.
```

**Inline math** — follow it with a parenthetical:

```markdown
Every $q \in \mathbb{Q}$ (in words: q in Q) with $q^2 < 2$ (in words: q squared less than 2) lies in $A$.
```

Rules:

- Never change, simplify or drop the math itself. The reading is an addition.
- Skip the reading for trivial inline math that reads the same as it is
  written: a single variable or number such as $x$, $A$, $3$, $\mathbb{R}$.
- One `In words:` line per display block, even for multi-line `align`
  environments; read the lines in order, joined with "and" or "so".
- Start the `In words:` sentence with a capital only when the first word is a
  real word ("The supremum of A ..."); keep a leading variable lowercase
  ("s equals ..."). End it with a full stop.
- Read structure, not glyphs: say "the set of q in Q such that ...", not
  "left brace q element of ...".

## Reading conventions

Relations are read **without** a linking verb, so chains stay readable:

| LaTeX | Read as |
|-------|---------|
| `a = b`, `a < b`, `a \le b` | a equals b · a less than b · a less than or equal to b |
| `a \ne b`, `a \approx b` | a is not equal to b · a is approximately equal to b |
| `x \in S`, `x \notin S` | x in S · x is not in S |
| `A \subseteq B`, `A \subset B` | A is a subset of B · A is a proper subset of B |
| `\Rightarrow`, `\iff`, `\to`, `\mapsto` | implies · if and only if · goes to · maps to |
| `\forall`, `\exists` | for all · there exists |
| `x^2`, `x^3`, `x^n`, `x^{-1}` | x squared · x cubed · x to the power of n · x inverse |
| `x_i`, `\frac{a}{b}`, `\sqrt{x}` | x sub i · a over b · the square root of x |
| `f(x)`, `\sin(x)` | f of x · sine of x |
| `(0,1)`, `[0,1]` | the open interval from 0 to 1 · the closed interval from 0 to 1 |
| `\{q \in \mathbb Q : q^2<2\}` | the set of q in Q such that q squared less than 2 |
| `\sup A`, `\lim_{n\to\infty} a_n` | the supremum of A · the limit as n goes to infinity of a sub n |
| `\sum_{i=1}^n a_i`, `\int_0^1 f(x)\,dx` | the sum from i equals 1 to n of a sub i · the integral from 0 to 1 of f of x d x |
| `\mathbb{R}`, `\alpha` | R · alpha |
| `\vec v`, `\hat x`, `\binom{n}{k}` | v vector · x hat · n choose k |
| `\dv{f}{x}`, `\pdv{f}{x}` | the derivative of f with respect to x · the partial derivative of ... |
| `\ce{2H2 + O2 -> 2H2O}` | 2 H 2 plus O 2 yields 2 H 2 O |

For long expressions, add spoken grouping so the reading is unambiguous:
`\frac{a+b}{c}` → "the quantity a plus b, over c" (the CLI reads this flatly
as "a plus b over c"; prefer the grouped wording when you write it yourself).

## Checking a reading or converting a document

If the `math2english` command is installed (`pip install` this repository),
it applies the same conventions mechanically:

```bash
math2english --math "s = \sup A"            # one expression -> "s equals the supremum of A"
math2english --annotate notes.md            # keep the math, add "In words:" after each expression
math2english --annotate -m physics notes.md # physics vocabulary (-m chemistry for \ce{...})
```

Use `--math` to check a reading you are unsure of. When the user hands you an
existing document to convert, run `--annotate` on it, then read the output and
fix any reading that sounds wrong before returning it. If the command is not
installed, write the readings yourself using the table above.
