These are two foundational concepts in real analysis.

### Ordered set

An **ordered set** (or **totally ordered set**) is a set (S) together with a relation (\le) satisfying four properties:

1. **Reflexive:** For every (a \in S),
   [
   a \le a.
   ]

2. **Antisymmetric:** If
   [
   a \le b \quad \text{and} \quad b \le a,
   ]
   then
   [
   a = b.
   ]

3. **Transitive:** If
   [
   a \le b \quad \text{and} \quad b \le c,
   ]
   then
   [
   a \le c.
   ]

4. **Total (comparability):** For any (a,b \in S), either
   [
   a \le b \quad \text{or} \quad b \le a.
   ]
   Every pair of elements can be compared.

**Examples**

* The integers (\mathbb{Z}) with the usual (\le).
* The rational numbers (\mathbb{Q}).
* The real numbers (\mathbb{R}).

---

### Upper bound

Suppose (A \subseteq S).

An element (u \in S) is an **upper bound** of (A) if

[
a \le u \quad \text{for every } a \in A.
]

There may be many upper bounds.

**Example**

For

[
A=(0,1)\subset\mathbb R,
]

the numbers (1,2,\pi,) and (1000) are all upper bounds.

---

### Least upper bound (supremum)

A **least upper bound** (also called the **supremum**) of (A) is an upper bound (s) satisfying:

1. (s) is an upper bound of (A), and
2. every other upper bound (u) satisfies
   [
   s \le u.
   ]

In other words, it is the **smallest** of all upper bounds.

We write

[
s=\sup A.
]

---

### Examples

1. **Open interval**
   [
   A=(0,1).
   ]

   * Upper bounds: (1,2,10,\dots)
   * Least upper bound:
     [
     \sup A = 1.
     ]

   Notice that (1\notin A).

2. **Closed interval**
   [
   A=[0,1].
   ]

   Here,

   [
   \sup A = 1,
   ]

   and (1) is actually an element of the set.

3. **Integers**
   [
   A={1,2,3}.
   ]

   The least upper bound is

   [
   \sup A=3.
   ]

---

### Why least upper bounds matter

The defining property of the real numbers is the **least upper bound property**:

> Every nonempty subset of (\mathbb{R}) that is bounded above has a least upper bound in (\mathbb{R}).

This is **not** true for the rational numbers. For example,

[
A={q\in\mathbb Q : q^2<2}
]

is bounded above in (\mathbb Q), but it has no least upper bound in (\mathbb Q), because the true supremum would be (\sqrt{2}), which is irrational. This completeness property is one of the key distinctions between (\mathbb{R}) and (\mathbb{Q}).
