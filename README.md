# MathCad to LaTeX Translator

A Python application that converts MathCad expressions into LaTeX format. This tool helps you translate mathematical expressions from MathCad's syntax to LaTeX, which can be used in academic papers, reports, and other documents.

## Features

- Convert MathCad expressions to LaTeX format
- Command-line interface for quick translations
- GUI interface for interactive use
- Support for common mathematical operations:
  - Basic arithmetic (addition, subtraction, multiplication, division)
  - Powers and exponents
  - Integrals
  - Parentheses and grouping
  - Constants

## Usage

### Command Line Interface

Run the translator from the command line:

```
python mathcad_to_latex.py "(@INTEGRAL 0 (@LABEL CONSTANT ∞) (@PARENS (+ (@SCALE 3 x) (@SCALE (@PARENS (* (* (* (* 1 2) 3) 4) 5)) (^ x 2)))) x)"
```

Or run it in interactive mode:

```
python mathcad_to_latex.py
```

### GUI Interface

For a more user-friendly experience, use the GUI interface:

```
python gui.py
```

## MathCad Syntax Examples

Here are some examples of MathCad syntax and their LaTeX equivalents:

### Basic Examples

1. **Simple Expressions**:
   - Mathcad: `x + y`
   - LaTeX output: `x + y`

2. **Greek Letters**:
   - Mathcad: `α + β`
   - LaTeX output: `\alpha + \beta`

3. **Fractions**:
   - Mathcad: `(/ x y)`
   - LaTeX output: `\frac{x}{y}`

4. **Powers**:
   - Mathcad: `(^ x 2)`
   - LaTeX output: `{x}^{2}`

### Advanced Examples

5. **Integrals**:
   - Mathcad: `(@INTEGRAL 0 1 x^2 x)`
   - LaTeX output: `\int_{0}^{1} x^{2} \, dx`

6. **Derivatives**:
   - Mathcad: `(@DERIV x 1 (^ x 2))`
   - LaTeX output: `\frac{\mathrm{d}}{\mathrm{d} x} {x}^{2}`

7. **Partial Derivatives**:
   - Mathcad: `(@PART_DERIV x 1 (@PARENS (+ x y)))`
   - LaTeX output: `\frac{\partial}{\partial x} \left(x + y\right)`

8. **Limits**:
   - Mathcad: `(@LIMIT x 0 (@PARENS (/ (^ x 2) x)))`
   - LaTeX output: `\lim_{x \to 0} \left(\frac{x^{2}}{x}\right)`

9. **Products**:
   - Mathcad: `(@PRODUCT (@IS i 1) n i)`
   - LaTeX output: `\prod_{i=1}^{n} i`

10. **Square Roots**:
    - Mathcad: `(@NTHROOT 2 x)`
    - LaTeX output: `\sqrt{x}`

11. **Nth Roots**:
    - Mathcad: `(@NTHROOT 3 x)`
    - LaTeX output: `\sqrt[3]{x}`

12. **Trigonometric Functions**:
    - Mathcad: `(@APPLY sin (@ARGS x))`
    - LaTeX output: `\sin(x)`

13. **Logarithms**:
    - Mathcad: `(@APPLY ln (@ARGS x))`
    - LaTeX output: `\ln(x)`

14. **Absolute Value**:
    - Mathcad: `(@APPLY abs (@ARGS x))`
    - LaTeX output: `\left|x\right|`

15. **Complex Expression**:
    - Mathcad: `(+ (* 2 x) (/ y z))`
    - LaTeX output: `2 \cdot x + \frac{y}{z}`

16. **Equations**:
    - Mathcad: `(@IS (^ x 2) (+ y z))`
    - LaTeX output: `x^{2} = y + z`

17. **Inequalities**:
    - Mathcad: `(@LEQ x y)`
    - LaTeX output: `x \leq y`
    - Mathcad: `(@GEQ x y)`
    - LaTeX output: `x \geq y`

18. **Multiple Integration**:
    - Mathcad: `(@INTEGRAL 0 1 (@INTEGRAL 0 y x^2 x) y)`
    - LaTeX output: `\int_{0}^{1} \int_{0}^{y} x^{2} \, dx \, dy`

## Supported MathCad Syntax

- `(+ a b c)`: Addition (a + b + c)
- `(- a b)`: Subtraction (a - b)
- `(* a b c)`: Multiplication (a · b · c)
- `(/ a b)`: Division (a / b)
- `(^ a b)`: Power (a^b)
- `(@SCALE a b)`: Scaling (ab, where a is coefficient)
- `(@PARENS expr)`: Parentheses (expr)
- `(@INTEGRAL a b expr var)`: Integral from a to b of expr with respect to var
- `(@LABEL CONSTANT value)`: Constant value

## Requirements

- Python 3.6 or higher
- Tkinter (included with most Python installations)

## License

This project is open source and available under the MIT License.