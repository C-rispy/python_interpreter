# Little German Language — Custom Interpreter in Python

A small interpreter for **LGL (Little German Language)**, built from scratch in Python.  
It supports arithmetic, control flow, data structures, and functional programming. Everything is evaluated from JSON-like lists rather than Python syntax.

> Developed as part of the Software Construction course at University of Zurich.  
> Original work completed together with **Bleron Neziri** and **Cynthia Ka Ong**.

---

## 🚀 Project Summary

This interpreter evaluates programs written in `.lgl` files using a simple execution model based on **operation lists** and **environment stacks**.  
Key supported features:

- Arithmetic + boolean expressions  
- Variables, environments, and sequential execution
- `do…until` loops for control flow
- Arrays and sets as mutable data structures
- Functional programming:
  - `map` — element-wise transformation
  - `reduce` — aggregation into a single value
  - `filter` — predicate-based selection
- Optional **visual call tracing** showing nested function structure and execution timing

The goal was to understand how interpreters process syntax trees and maintain execution state — without relying on Python’s native expression evaluation.

---

## 🧩 Language & Execution Overview

Programs are JSON-like structures:

```json
["addieren", 2, ["multiplizieren", 3, 4]]
```

Execution is driven by a dispatch table mapping operation names to Python functions.

### Construct Categories Supported

| Category      | Examples                                               | Notes                                                |
| ------------- | ------------------------------------------------------ | ---------------------------------------------------- |
| Arithmetic    | `addieren`, `multiplizieren`, `potenz`, `rest`         | Assertions ensure safety (e.g., no division by zero) |
| Comparison    | `kleiner`, `gleich`, `ungleich`, …                     | Booleans evaluated directly                          |
| Boolean Logic | `AND`, `OR`, `NOT`                                     | Operate on truth-values from comparisons             |
| Loops         | `loop_until`                                           | Condition checked **after** each iteration           |
| Arrays        | `create_array`, `set_array_value`, `concatenate_array` | True mutation through env lookup                     |
| Sets          | `create_set`, `set_insert`, `merge_set`                | Duplicate-safe behavior                              |
| Functions     | `func`, `call`                                         | Fresh lexical scope for each call                    |
| FP Tools      | `map`, `reduce`, `filter`                              | Only user-defined functions permitted                |

---

## 🔍 Visual Tracing Mode

Tracing reveals nested function execution and durations in milliseconds:

```bash
python interpreter.py --trace tracing.lgl
```

Example output style:

```bash
main
+-- add_three (0.032ms)
|  +-- add_two (0.004ms)
+-- print
```

This helped reason about recursion, environment depth, and performance.

---

## 📂 Repository Structure

```bash
interpreter.py       # Core interpreter implementation
extensions.lgl       # Numeric operations & loops showcase
data_structures.lgl  # Arrays and sets showcase
functional.lgl       # Map / reduce / filter showcase
tracing.lgl          # Tracing visualization demo
README.md            # This document
```

Run any program like:

```bash
python interpreter.py functional.lgl
```

---

## 🧠 Key Learnings

This project reinforced:
- Managing variable scope using stacked environments
- Implementing dynamic execution in a tree-based interpreter
- Defensive programming through assertions + type checks
- Designing APIs for functional + imperative constructs
- Adding debugging instrumentation (tracing) without breaking semantics
- Programming logic directly, made the relationship between language features and interpreter mechanics nicely explicit


## 📌 Attribution

This repository represents my personal portfolio version of the project.
Course collaboration credits:
- Thierry Mathys
- Bleron Neziri
- Cynthia Ka Ong
