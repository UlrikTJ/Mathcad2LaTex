#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MathCad to LaTeX Translator
---------------------------
This script translates MathCad expressions into LaTeX format.
"""

import re
import sys


class MathcadToLatexTranslator:
    """
    A translator for converting MathCad expressions to LaTeX format.
    """

    def __init__(self):
        """Initialize the translator with transformation rules."""
        self.operations = {
            # Basic operations
            '+': '+',
            '-': '-',
            '*': '\\cdot ',
            '/': '\\frac{{{}}}{{{}}}'
        }
        
        # Special symbols
        self.special_symbols = {
            "†": "{\\dagger}",  # Dagger symbol
            "‡": "{\\ddagger}",  # Double dagger
            "∗": "^{*}",          # Asterisk superscript
            "°": "^{\\circ}",     # Degree symbol
            "′": "^{\\prime}",    # Prime
            "″": "^{\\prime\\prime}",  # Double prime
            "‴": "^{\\prime\\prime\\prime}"  # Triple prime
        }
        
        # Greek letter mappings
        self.greek_letters = {
            # Lowercase
            'α': '\\alpha',
            'β': '\\beta',
            'χ': '\\chi',
            'δ': '\\delta',
            'ε': '\\epsilon',
            'φ': '\\phi',
            'ϕ': '\\varphi',
            'γ': '\\gamma',
            'η': '\\eta',
            'ι': '\\iota',
            'κ': '\\kappa',
            'λ': '\\lambda',
            'μ': '\\mu',
            'ν': '\\nu',
            'ο': '\\omicron',
            'π': '\\pi',
            'θ': '\\theta',
            'ρ': '\\rho',
            'σ': '\\sigma',
            'τ': '\\tau',
            'υ': '\\upsilon',
            'ω': '\\omega',
            'ξ': '\\xi',
            'ψ': '\\psi',
            'ζ': '\\zeta',
            'ϑ': '\\vartheta',
            
            # Uppercase
            'Α': '\\Alpha',
            'Β': '\\Beta',
            'Χ': '\\Chi',
            'Δ': '\\Delta',
            'Ε': '\\Epsilon',
            'Φ': '\\Phi',
            'Γ': '\\Gamma',
            'Η': '\\Eta',
            'Ι': '\\Iota',
            'Κ': '\\Kappa',
            'Λ': '\\Lambda',
            'Μ': '\\Mu',
            'Ν': '\\Nu',
            'Ο': '\\Omicron',
            'Π': '\\Pi',
            'Θ': '\\Theta',
            'Ρ': '\\Rho',
            'Σ': '\\Sigma',
            'Τ': '\\Tau',
            'Υ': '\\Upsilon',
            'Ω': '\\Omega',
            'Ξ': '\\Xi',
            'Ψ': '\\Psi',
            'Ζ': '\\Zeta'
        }
        
        # Units dictionary
        self.units = {
            # Base SI units
            "m": "\\mathrm{m}",
            "kg": "\\mathrm{kg}",
            "s": "\\mathrm{s}",
            "A": "\\mathrm{A}",
            "K": "\\mathrm{K}",
            "mol": "\\mathrm{mol}",
            "cd": "\\mathrm{cd}",
            
            # Derived SI units with special handling for "N" (Newton)
            "N": "\\mathrm{N}",  # Explicitly define Newton
            "n": "\\mathrm{n}",  # Case-insensitive handling
            "newton": "\\mathrm{N}",  # Alternative spelling
            "Pa": "\\mathrm{Pa}",
            "J": "\\mathrm{J}",
            "W": "\\mathrm{W}",
            "C": "\\mathrm{C}",
            "V": "\\mathrm{V}",
            "F": "\\mathrm{F}",
            "Ω": "\\Omega",
            "S": "\\mathrm{S}",
            "T": "\\mathrm{T}",
            "H": "\\mathrm{H}",
            "Hz": "\\mathrm{Hz}",
            
            # Common non-SI units
            "min": "\\mathrm{min}",
            "h": "\\mathrm{h}",
            "day": "\\mathrm{day}",
            "deg": "^{\\circ}",
            "rad": "\\mathrm{rad}",
            "sr": "\\mathrm{sr}",
            "L": "\\mathrm{L}",
            "g": "\\mathrm{g}",
            "t": "\\mathrm{t}",
            "eV": "\\mathrm{eV}",
            "bar": "\\mathrm{bar}",
            "atm": "\\mathrm{atm}",
            "in": "\\mathrm{in}",
            "ft": "\\mathrm{ft}",
            "mi": "\\mathrm{mi}",
            "lb": "\\mathrm{lb}"
        }
        
        # Physical constants dictionary with proper LaTeX representations
        self.constants = {
            # Fundamental constants
            "c": "c",                # Speed of light
            "e_c": "e",              # Elementary charge
            "h": "h",                # Planck constant
            "ℏ": "\\hbar",           # Reduced Planck constant
            "k": "k_\\mathrm{B}",    # Boltzmann constant
            "m_u": "m_\\mathrm{u}",  # Atomic mass constant
            "N_A": "N_\\mathrm{A}",  # Avogadro constant
            "R": "R",                # Gas constant
            "R_∞": "R_{\\infty}",    # Rydberg constant
            "α": "\\alpha",          # Fine structure constant
            "γ": "\\gamma",          # Euler-Mascheroni constant
            "ε_0": "\\varepsilon_0", # Vacuum permittivity
            "μ_0": "\\mu_0",         # Vacuum permeability
            "σ": "\\sigma",          # Stefan-Boltzmann constant
            "Φ_0": "\\Phi_0",        # Magnetic flux quantum
            
            # Additional physical constants
            "G": "G",                # Gravitational constant
            "g": "g",                # Standard acceleration of gravity
            "M_e": "m_\\mathrm{e}",  # Electron mass
            "M_p": "m_\\mathrm{p}",  # Proton mass
            "M_n": "m_\\mathrm{n}",  # Neutron mass
            "q_e": "e",              # Elementary charge (alternative notation)
            "F": "F",                # Faraday constant
            "n_0": "n_0",            # Vacuum refractive index
            "K_J": "K_\\mathrm{J}",  # Josephson constant
            "R_K": "R_\\mathrm{K}",  # von Klitzing constant
            "μ_B": "\\mu_\\mathrm{B}", # Bohr magneton
            "μ_N": "\\mu_\\mathrm{N}", # Nuclear magneton
            "a_0": "a_0",            # Bohr radius
            "E_h": "E_\\mathrm{h}",  # Hartree energy
            "λ_C": "\\lambda_\\mathrm{C}", # Compton wavelength
        }

    def parse_expression(self, expression):
        """
        Parse a MathCad expression and convert it to LaTeX.
        
        Args:
            expression (str): The MathCad expression to convert
            
        Returns:
            str: The equivalent LaTeX expression
        """
        # Check if the expression is empty or None
        if not expression:
            return ""

        # Remove outer parentheses if they exist
        expression = expression.strip()
        
        # Check if we have a complex expression with symbolic evaluation
        if (expression.startswith("(/") or expression.startswith("(*") or 
            expression.startswith("(+") or expression.startswith("(-")) and (
            "(@LABEL" in expression or "(@APPLY" in expression):
            # This is likely a complex evaluation result - parse it as a whole
            return self._handle_complex_evaluation(expression)
        
        # Handle direct arithmetic operations in parentheses
        if expression.startswith("(+"):
            return self._handle_addition(expression)
        elif expression.startswith("(-"):
            return self._handle_subtraction(expression)
        elif expression.startswith("(*"):
            return self._handle_multiplication(expression)
        elif expression.startswith("(/"):
            return self._handle_division(expression)
        elif expression.startswith("(^"):
            return self._handle_power(expression)
        
        # Handle special constants
        if expression == "e":
            return "e"  # LaTeX will format 'e' as the natural logarithm base
        
        # Replace infinity symbol with LaTeX \infty
        if expression == "∞":
            return "\\infty"
            
        # Check for Greek letters (single character case)
        if len(expression) == 1 and expression in self.greek_letters:
            return self.greek_letters[expression]
            
        # Check for special symbols (like dagger)
        if len(expression) == 1 and expression in self.special_symbols:
            return self.special_symbols[expression]
        
        # Replace Greek letters in longer expressions
        for greek_char, latex_cmd in self.greek_letters.items():
            expression = expression.replace(greek_char, latex_cmd)
        
        # Replace special symbols in longer expressions
        for special_char, latex_cmd in self.special_symbols.items():
            expression = expression.replace(special_char, latex_cmd)
        
        # Replace infinity symbol in longer expressions
        expression = expression.replace("∞", "\\infty")
        
        # Handle special MathCad functions
        if expression.startswith("(@INTEGRAL"):
            return self._add_spaces_after_commands(self._handle_integral(expression))
        elif expression.startswith("(@PART_DERIV"):
            return self._add_spaces_after_commands(self._handle_partial_derivative(expression))
        elif expression.startswith("(@LIMIT"):
            return self._add_spaces_after_commands(self._handle_limit(expression))
        elif expression.startswith("(@DERIV"):
            return self._add_spaces_after_commands(self._handle_derivative(expression))
        elif expression.startswith("(@PRIME"):
            return self._add_spaces_after_commands(self._handle_prime(expression))
        elif expression.startswith("(@NTHROOT"):
            return self._add_spaces_after_commands(self._handle_nthroot(expression))
        elif expression.startswith("(@PRODUCT"):
            return self._add_spaces_after_commands(self._handle_product(expression))
        elif expression.startswith("(@SUM"):
            return self._add_spaces_after_commands(self._handle_sum(expression))
        elif expression.startswith("(@APPLY"):
            return self._add_spaces_after_commands(self._handle_apply(expression))
        elif expression.startswith("(@ARGS"):
            return self._add_spaces_after_commands(self._handle_args(expression))
        elif expression.startswith("(@ELEMENT_OF"):
            return self._add_spaces_after_commands(self._handle_element_of(expression))
        elif expression.startswith("(@XOR"):
            return self._add_spaces_after_commands(self._handle_xor(expression))
        elif expression.startswith("(@GEQ"):
            return self._add_spaces_after_commands(self._handle_geq(expression))
        elif expression.startswith("(@LEQ"):
            return self._add_spaces_after_commands(self._handle_leq(expression))
        elif expression.startswith("(@AND"):
            return self._add_spaces_after_commands(self._handle_and(expression))
        elif expression.startswith("(@OR"):
            return self._add_spaces_after_commands(self._handle_or(expression))
        elif expression.startswith("(@NOT"):
            return self._add_spaces_after_commands(self._handle_not(expression))
        elif expression.startswith("(@NEQ"):
            return self._add_spaces_after_commands(self._handle_neq(expression))
        elif expression.startswith("(@NEG"):
            return self._add_spaces_after_commands(self._handle_negation(expression))
        elif expression.startswith("(@SCALE"):
            return self._add_spaces_after_commands(self._handle_scale(expression))
        elif expression.startswith("(@RSCALE"):
            return self._add_spaces_after_commands(self._handle_rscale(expression))
        elif expression.startswith("(@PARENS"):
            return self._add_spaces_after_commands(self._handle_parentheses(expression))
        elif expression.startswith("(@LABEL"):
            return self._add_spaces_after_commands(self._handle_label(expression))
        elif expression.startswith("(@IS"):
            return self._add_spaces_after_commands(self._handle_is(expression))
        elif expression.startswith("(@MATRIX"):
            return self._add_spaces_after_commands(self._handle_matrix(expression))
        elif expression.startswith("(@CROSS"):
            return self._add_spaces_after_commands(self._handle_cross(expression))
        elif expression.startswith("(@DOT"):
            return self._add_spaces_after_commands(self._handle_dot(expression))
        elif expression.startswith("(@SYM_EVAL"):
            return self._add_spaces_after_commands(self._handle_sym_eval(expression))
        elif expression.startswith("(@SUB"):
            return self._add_spaces_after_commands(self._handle_subscript(expression))
        elif expression.startswith("(@ID") and "(@SUB" in expression:
            return self._add_spaces_after_commands(self._handle_identifier_with_subscript(expression))
        elif expression.startswith("(@EQ"):  # New handler for user-created equations
            return self._add_spaces_after_commands(self._handle_equation(expression))
        elif expression.startswith("(="):  # Handler for equals expressions
            return self._add_spaces_after_commands(self._handle_equals(expression))
        else:
            # If it's a simple expression (like a variable or number)
            return self._add_spaces_after_commands(expression)

    def _handle_complex_evaluation(self, expression):
        """
        Handle complex evaluation expressions from MathCad that contain nested labeled entities.
        
        Args:
            expression (str): The complex MathCad expression
            
        Returns:
            str: The equivalent LaTeX expression
        """
        # First, try to identify the root operation
        if expression.startswith("(/"):
            # This is a division operation
            # Find the arguments by carefully parsing
            content = expression[2:-1].strip()  # Remove "(/" and closing ")"
            
            # Split content at top level
            args = self._split_at_top_level(content)
            
            if len(args) >= 2:
                numerator = self.parse_expression(args[0])
                denominator = self.parse_expression(args[1])
                return f"\\frac{{{numerator}}}{{{denominator}}}"
            else:
                # Fallback to normal parsing if we can't identify the structure
                return self._handle_division(expression)
                
        elif expression.startswith("(*"):
            # This is a multiplication operation
            content = expression[2:-1].strip()  # Remove "(*" and closing ")"
            
            # Split content at top level
            args = self._split_at_top_level(content)
            
            if args:
                # Parse each argument and join with multiplication
                parsed_args = [self.parse_expression(arg) for arg in args]
                return " \\cdot ".join(parsed_args)
            else:
                # Fallback
                return self._handle_multiplication(expression)
                
        elif expression.startswith("(+"):
            # This is an addition operation
            content = expression[2:-1].strip()  # Remove "(+" and closing ")"
            
            # Split content at top level
            args = self._split_at_top_level(content)
            
            if args:
                # Parse each argument and join with addition
                parsed_args = [self.parse_expression(arg) for arg in args]
                return " + ".join(parsed_args)
            else:
                # Fallback
                return self._handle_addition(expression)
                
        elif expression.startswith("(-"):
            # This is a subtraction operation
            content = expression[2:-1].strip()  # Remove "(-" and closing ")"
            
            # Split content at top level
            args = self._split_at_top_level(content)
            
            if len(args) >= 2:
                minuend = self.parse_expression(args[0])
                subtrahend = self.parse_expression(args[1])
                return f"{minuend} - {subtrahend}"
            else:
                # Fallback
                return self._handle_subtraction(expression)
        
        # If we get here, we couldn't identify a specific structure
        # Let's try a more general approach by recursively parsing the expression
        
        # Replace labeled entities with their LaTeX representations
        pattern = r'\(@LABEL\s+([A-Z]+)\s+([^)]+)\)'
        
        def replace_labels(match):
            label_type = match.group(1)
            content = match.group(2)
            if label_type.upper() == "CONSTANT":
                if content in self.constants:
                    return self.constants[content]
                return content
            elif label_type.upper() == "VARIABLE":
                return content
            elif label_type.upper() == "UNIT":
                if content in self.units:
                    return self.units[content]
                return f"\\mathrm{{{content}}}"
            elif label_type.upper() == "FUNCTION":
                return f"\\operatorname{{{content}}}"
            return content
            
        # First pass: replace labels
        modified_expr = re.sub(pattern, replace_labels, expression)
        
        # Replace function applications
        func_pattern = r'\(@APPLY\s+([^)]+)\s+\(@ARGS\s+([^)]+)\)\)'
        
        def replace_functions(match):
            func_name = match.group(1)
            arg = match.group(2)
            
            # Handle labeled function
            if func_name.startswith('(@LABEL'):
                label_match = re.search(r'\(@LABEL\s+([A-Z]+)\s+([^)]+)\)', func_name)
                if label_match and label_match.group(1).upper() == "FUNCTION":
                    func_name = f"\\operatorname{{{label_match.group(2)}}}"
                else:
                    func_name = self.parse_expression(func_name)
            
            return f"{func_name}({arg})"
            
        # Second pass: replace function applications
        modified_expr = re.sub(func_pattern, replace_functions, modified_expr)
        
        # Replace operations
        op_patterns = [
            (r'\(/\s+([^)]+)\s+([^)]+)\)', r'\\frac{\1}{\2}'),  # Division
            (r'\(\*\s+([^)]+)\s+([^)]+)\)', r'\1 \\cdot \2'),   # Multiplication
            (r'\(\+\s+([^)]+)\s+([^)]+)\)', r'\1 + \2'),        # Addition
            (r'\(-\s+([^)]+)\s+([^)]+)\)', r'\1 - \2'),         # Subtraction
            (r'\(\^\s+([^)]+)\s+([^)]+)\)', r'{\1}^{\2}')       # Power
        ]
        
        # Apply operation replacements
        for pattern, replacement in op_patterns:
            modified_expr = re.sub(pattern, replacement, modified_expr)
            
        # Remove any remaining MathCad-specific syntax
        modified_expr = re.sub(r'\(@[A-Z_]+', '', modified_expr)
        modified_expr = re.sub(r'\)', '', modified_expr)
        
        # If all else fails, fall back to standard parsing
        if modified_expr == expression:
            if expression.startswith("(/"):
                return self._handle_division(expression)
            elif expression.startswith("(*"):
                return self._handle_multiplication(expression)
            elif expression.startswith("(+"):
                return self._handle_addition(expression)
            elif expression.startswith("(-"):
                return self._handle_subtraction(expression)
            else:
                # Just try standard parsing as a last resort
                pattern = r'\(@([A-Z_]+)([^)]*)\)'
                
                def parse_special(match):
                    cmd = match.group(1)
                    args = match.group(2)
                    method_name = f"_handle_{cmd.lower()}"
                    if hasattr(self, method_name):
                        handler = getattr(self, method_name)
                        return handler(f"(@{cmd}{args})")
                    return f"(@{cmd}{args})"
                    
                return re.sub(pattern, parse_special, expression)
                
        return modified_expr
        
    def _split_at_top_level(self, content):
        """
        Split content at top level spaces, correctly handling nested parentheses.
        
        Args:
            content (str): The content to split
            
        Returns:
            list: The split arguments
        """
        args = []
        current_arg = ""
        paren_level = 0
        
        for char in content:
            if char == "(":
                current_arg += char
                paren_level += 1
            elif char == ")":
                current_arg += char
                paren_level -= 1
            elif char == " " and paren_level == 0 and current_arg.strip():
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
                
        if current_arg.strip():
            args.append(current_arg.strip())
            
        return args

    def _add_spaces_after_commands(self, latex):
        """
        Add spaces after LaTeX commands to ensure proper separation.
        For example, turns \pib into \pi b and \alphax into \alpha x.
        
        Args:
            latex (str): The LaTeX expression
        
        Returns:
            str: LaTeX with spaces after commands
        """
        if not latex or '\\' not in latex:
            return latex

        # First, directly fix common issues with specific LaTeX commands
        # This handles cases like \pib -> \pi b, which can be difficult with recursive parsing
        common_patterns = [
            (r'\\pi([a-zA-Z0-9])', r'\\pi \1'),
            (r'\\alpha([a-zA-Z0-9])', r'\\alpha \1'),
            (r'\\beta([a-zA-Z0-9])', r'\\beta \1'),
            (r'\\gamma([a-zA-Z0-9])', r'\\gamma \1'),
            (r'\\delta([a-zA-Z0-9])', r'\\delta \1'),
            (r'\\epsilon([a-zA-Z0-9])', r'\\epsilon \1'),
            (r'\\zeta([a-zA-Z0-9])', r'\\zeta \1'),
            (r'\\eta([a-zA-Z0-9])', r'\\eta \1'),
            (r'\\theta([a-zA-Z0-9])', r'\\theta \1'),
            (r'\\iota([a-zA-Z0-9])', r'\\iota \1'),
            (r'\\kappa([a-zA-Z0-9])', r'\\kappa \1'),
            (r'\\lambda([a-zA-Z0-9])', r'\\lambda \1'),
            (r'\\mu([a-zA-Z0-9])', r'\\mu \1'),
            (r'\\nu([a-zA-Z0-9])', r'\\nu \1'),
            (r'\\xi([a-zA-Z0-9])', r'\\xi \1'),
            (r'\\omicron([a-zA-Z0-9])', r'\\omicron \1'),
            (r'\\rho([a-zA-Z0-9])', r'\\rho \1'),
            (r'\\sigma([a-zA-Z0-9])', r'\\sigma \1'),
            (r'\\tau([a-zA-Z0-9])', r'\\tau \1'),
            (r'\\upsilon([a-zA-Z0-9])', r'\\upsilon \1'),
            (r'\\phi([a-zA-Z0-9])', r'\\phi \1'),
            (r'\\chi([a-zA-Z0-9])', r'\\chi \1'),
            (r'\\psi([a-zA-Z0-9])', r'\\psi \1'),
            (r'\\omega([a-zA-Z0-9])', r'\\omega \1')
        ]
        
        result = latex
        for pattern, replacement in common_patterns:
            result = re.sub(pattern, replacement, result)
        
        # Process any remaining complex structures like \sqrt{}, \frac{}, etc.
        return self._process_nested_structures(result)
    
    def _process_nested_structures(self, latex):
        """
        Process LaTeX content with nested structures, ensuring correct spacing
        in constructs like \sqrt{}, \frac{}, etc.
        
        Args:
            latex (str): The LaTeX expression
            
        Returns:
            str: Properly formatted LaTeX with correct spacing
        """
        # Track positions where we are in special constructs
        i = 0
        result = ""
        brace_level = 0
        
        # Known complete commands that shouldn't be split
        complete_commands = ['int', 'sum', 'prod', 'lim', 'frac', 'sqrt', 'in']
        
        in_command = False
        current_command = ""
        
        while i < len(latex):
            # Handle backslash commands
            if latex[i] == '\\' and not in_command:
                in_command = True
                command_start = i
                i += 1
                current_command = ""
                while i < len(latex) and latex[i].isalpha():
                    current_command += latex[i]
                    i += 1
                
                # Add the command to the result
                result += latex[command_start:command_start+len(current_command)+1]
                
                # Skip anything that shouldn't have spaces added
                if current_command in complete_commands:
                    in_command = False
                continue
            
            # If we're inside a command but hit a non-alphabetic character, end the command
            if in_command and (i >= len(latex) or not latex[i].isalpha()):
                in_command = False
                
                # If the next character is alphanumeric, add a space
                if i < len(latex) and latex[i].isalnum() and latex[i] not in ['{', '}', '(', ')', '[', ']', ' ']:
                    result += " "
                
            # Handle braces
            if latex[i] == '{':
                brace_level += 1
            elif latex[i] == '}':
                brace_level -= 1
            
            # Add the current character
            result += latex[i]
            i += 1
            
        return result

    def _extract_arguments(self, expression):
        """
        Extract arguments from a MathCad function call.
        
        Args:
            expression (str): The MathCad function call
            
        Returns:
            list: The arguments of the function
        """
        # Remove the function name and outer parentheses
        function_end = expression.find(" ")
        if function_end == -1:
            return []
            
        content = expression[function_end + 1:-1].strip()
        
        args = []
        current_arg = ""
        paren_count = 0
        
        for char in content:
            if char == "(" and paren_count == 0 and current_arg.strip():
                args.append(current_arg.strip())
                current_arg = char
                paren_count += 1
            elif char == "(":
                current_arg += char
                paren_count += 1
            elif char == ")":
                current_arg += char
                paren_count -= 1
            elif char == " " and paren_count == 0 and current_arg.strip():
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
                
        if current_arg.strip():
            args.append(current_arg.strip())
            
        return args
    
    def _extract_arguments_from_op(self, expression):
        """
        Extract arguments from a MathCad operation expression like "+2 1".
        
        Args:
            expression (str): The MathCad operation expression (without the leading operator)
            
        Returns:
            list: The arguments of the operation
        """
        if not expression or len(expression) < 2:
            return []
            
        # Remove any outer parentheses and trim
        content = expression.strip()
        if content.startswith('(') and content.endswith(')'):
            content = content[1:-1].strip()
        
        args = []
        current_arg = ""
        paren_count = 0
        
        for char in content:
            if char == "(" and current_arg.strip() == "":
                paren_count += 1
                current_arg += char
            elif char == "(":
                current_arg += char
                paren_count += 1
            elif char == ")":
                current_arg += char
                paren_count -= 1
            elif char == " " and paren_count == 0 and current_arg.strip():
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
                
        if current_arg.strip():
            args.append(current_arg.strip())
            
        return args

    def _handle_integral(self, expression):
        """Convert a MathCad integral to LaTeX."""
        args = self._extract_arguments(expression)
        
        if len(args) < 4:
            return "\\int{}"  # Default simple integral if not enough arguments
        
        lower_limit = self.parse_expression(args[0])
        upper_limit = self.parse_expression(args[1])
        
        # Handle the integrand - could be complex
        integrand = self.parse_expression(args[2])
        
        # Get the integration variable
        var = self.parse_expression(args[3]) if len(args) > 3 else "x"
        
        return f"\\int_{{{lower_limit}}}^{{{upper_limit}}} {integrand} \\, d{var}"
    
    def _handle_scale(self, expression):
        """Convert a MathCad scale operation (for units) to LaTeX."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        # First argument is typically a numerical value
        value = self.parse_expression(args[0])
        
        # Second argument is the unit or another expression
        unit_expr = args[1]
        
        # Check if the unit is a simple unit or a compound expression
        if unit_expr in self.units:
            # For a simple unit, format as value with the unit
            unit = self.units[unit_expr]
            return f"{value}\\,{unit}"
        elif unit_expr.startswith("(/"):
            # Handle division in units (e.g., m/s)
            unit_args = self._extract_arguments(unit_expr)
            if len(unit_args) >= 2:
                num_unit = self.parse_expression(unit_args[0])
                denom_unit = self.parse_expression(unit_args[1])
                return f"{value}\\,\\frac{{{num_unit}}}{{{denom_unit}}}"
            else:
                return f"{value}"
        elif unit_expr.startswith("(^"):
            # Handle powers in units (e.g., m^2)
            unit_args = self._extract_arguments(unit_expr)
            if len(unit_args) >= 2:
                base_unit = unit_args[0]
                power = self.parse_expression(unit_args[1])
                
                if base_unit in self.units:
                    base_unit = self.units[base_unit]
                else:
                    base_unit = self.parse_expression(base_unit)
                
                return f"{value}\\,{base_unit}^{{{power}}}"
            else:
                return f"{value}"
        else:
            # For compound units or other expressions, parse and format appropriately
            unit = self.parse_expression(unit_expr)
            return f"{value}\\,{unit}"
    
    def _handle_rscale(self, expression):
        """Handle the RSCALE operation in MathCad (result with specific unit)."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        # First argument is the value, which may be in parentheses
        value_expr = args[0]
        if value_expr.startswith("(@PARENS"):
            value_args = self._extract_arguments(value_expr)
            if value_args:
                value = self.parse_expression(value_args[0])
            else:
                value = ""
        else:
            value = self.parse_expression(value_expr)
        
        # Second argument is the unit label
        unit_expr = args[1]
        unit = ""
        
        if unit_expr.startswith("(@LABEL"):
            label_args = self._extract_arguments(unit_expr)
            if len(label_args) >= 2:
                label_type = label_args[0]
                unit_name = label_args[1]
                
                # Check if it's a unit label (case-insensitive)
                if label_type.upper() == "UNIT":
                    # First try exact match
                    if unit_name in self.units:
                        unit = self.units[unit_name]
                    # Special case for Newton (N)
                    elif unit_name == "N":
                        unit = "\\mathrm{N}"
                    # Try case-insensitive match
                    else:
                        unit_key = next((k for k in self.units.keys() if k.upper() == unit_name.upper()), None)
                        if unit_key:
                            unit = self.units[unit_key]
                        else:
                            # Handle case where unit name is just a plain string
                            unit = f"\\mathrm{{{unit_name}}}"
                else:
                    unit = self.parse_expression(unit_expr)
            else:
                unit = self.parse_expression(unit_expr)
        else:
            unit = self.parse_expression(unit_expr)
            
        # Format with appropriate spacing
        return f"{value}\\,{unit}"
    
    def _handle_parentheses(self, expression):
        """Handle parenthesized expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return "()"
        
        inner_expr = self.parse_expression(args[0])
        return f"\\left({inner_expr}\\right)"
    
    def _handle_label(self, expression):
        """Handle labeled expressions like constants, units, variables and functions in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        label_type = args[0]
        
        # Handle different label types (case-insensitive comparison for label types)
        if label_type.upper() == "CONSTANT":
            if len(args) < 2:
                return ""
                
            value = args[1]
            
            # Check if this is a known physical constant
            if value in self.constants:
                return self.constants[value]
            elif value.startswith("(@ID"):
                # Handle constants with subscripts like e_c, m_u, etc.
                id_args = self._extract_arguments(value)
                if len(id_args) >= 2:
                    main_symbol = id_args[0]
                    sub_symbol = self.parse_expression(id_args[1])
                    
                    # Check if this ID with subscript matches a known constant pattern
                    sub_without_backslash = sub_symbol.replace('\\', '')
                    const_key = f"{main_symbol}_{sub_without_backslash}"
                    if const_key in self.constants:
                        return self.constants[const_key]
                    else:
                        return f"{main_symbol}_{{{sub_symbol}}}"
                else:
                    return value
            else:
                return value
        elif label_type.upper() == "UNIT":  # Case-insensitive comparison for "UNIT"
            if len(args) < 2:
                return ""
                
            unit_name = args[1]
            
            # First check for exact match
            if unit_name in self.units:
                return self.units[unit_name]
            
            # Special case for Newton unit
            if unit_name == "N":
                return "\\mathrm{N}"
            
            # Then check for case-insensitive match
            unit_key = next((k for k in self.units.keys() if k.upper() == unit_name.upper()), None)
            if unit_key:
                return self.units[unit_key]
                
            # Handle case where unit name is just a plain string
            return f"\\mathrm{{{unit_name}}}"
        elif label_type.upper() == "VARIABLE":  # Handle VARIABLE labels
            if len(args) < 2:
                return ""
                
            var_name = args[1]
            # Return the variable name as is, possibly in italic as per LaTeX math mode
            return f"{var_name}"
        elif label_type.upper() == "FUNCTION":  # Handle FUNCTION labels
            if len(args) < 2:
                return ""
                
            func_name = args[1]
            # Format function names with \operatorname for proper math formatting
            return f"\\operatorname{{{func_name}}}"
        
        # If we reach here, it's an unknown label type
        return self.parse_expression(args[1]) if len(args) > 1 else label_type
    
    def _handle_power(self, expression):
        """Handle power expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        base = self.parse_expression(args[0])
        exponent = self.parse_expression(args[1])
        
        # Special case for e (natural logarithm base)
        if base == "e":
            return f"e^{{{exponent}}}"
        
        return f"{{{base}}}^{{{exponent}}}"
    
    def _handle_multiplication(self, expression):
        """Handle multiplication expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        result = ""
        for i, arg in enumerate(args):
            parsed_arg = self.parse_expression(arg)
            if i > 0:
                result += " \\cdot " + parsed_arg
            else:
                result += parsed_arg
                
        return result
    
    def _handle_division(self, expression):
        """Handle division expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        numerator = self.parse_expression(args[0])
        denominator = self.parse_expression(args[1])
        
        return f"\\frac{{{numerator}}}{{{denominator}}}"
    
    def _handle_addition(self, expression):
        """Handle addition expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        result = ""
        for i, arg in enumerate(args):
            parsed_arg = self.parse_expression(arg)
            if i > 0:
                result += " + " + parsed_arg
            else:
                result += parsed_arg
                
        return result
    
    def _handle_subtraction(self, expression):
        """Handle subtraction expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        minuend = self.parse_expression(args[0])
        subtrahend = self.parse_expression(args[1])
        
        return f"{minuend} - {subtrahend}"
    
    def _handle_greater_than(self, expression):
        """Handle greater than expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} > {right}"
    
    def _handle_less_than(self, expression):
        """Handle less than expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} < {right}"
        
    def _handle_nthroot(self, expression):
        """Handle nth root expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        # First argument is the root order
        n = args[0]
        if n == "@PLACEHOLDER":
            n = ""  # Empty if placeholder
        else:
            n = self.parse_expression(n)
        
        # Second argument is the radicand
        radicand = self.parse_expression(args[1])
        
        # If n is 2 or empty, it's a square root
        if n == "2" or n == "":
            return f"\\sqrt{{{radicand}}}"
        else:
            return f"\\sqrt[{n}]{{{radicand}}}"
            
    def _handle_partial_derivative(self, expression):
        """Handle partial derivatives in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 3:
            return ""
        
        # Extract the variable of differentiation
        variable = self.parse_expression(args[0])
        
        # The second argument is either a placeholder or the order
        second_arg = args[1]
        order = ""
        
        # Check if the second argument is a numeric order
        if second_arg.isdigit():
            order = second_arg
        elif second_arg == "@PLACEHOLDER" and len(args) > 3:
            # If placeholder and there's another argument, it might be the order
            order = self.parse_expression(args[3])
        
        # The third argument is the function to differentiate
        third_arg = args[2]
        if third_arg.startswith("(@PARENS"):
            # Extract the content within the parentheses
            inner_args = self._extract_arguments(third_arg)
            if inner_args:
                function = self.parse_expression(inner_args[0])
                function = f"\\left({function}\\right)"
            else:
                function = ""
        else:
            function = self.parse_expression(third_arg)
        
        # Format the partial derivative with the order if specified
        if order:
            return f"\\frac{{\\partial^{{{order}}}}}{{\\partial {variable}^{{{order}}}}} {function}"
        else:
            # No order specified, assume first order
            return f"\\frac{{\\partial}}{{\\partial {variable}}} {function}"
    
    def _handle_limit(self, expression):
        """Handle limit expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 3:
            return ""
        
        # In MathCad format: (@LIMIT var approach direction func)
        variable = self.parse_expression(args[0])
        approach_value = self.parse_expression(args[1])
        
        # Handle direction (left/right hand) if present
        direction = ""
        func_index = 2
        if len(args) > 2 and (args[2] == "@LEFT_HAND" or args[2] == "@RIGHT_HAND"):
            if args[2] == "@LEFT_HAND":
                direction = "^{-}"
            elif args[2] == "@RIGHT_HAND":
                direction = "^{+}"
            func_index = 3
        
        # Get the function to find limit of
        if len(args) > func_index:
            # Handle the function part
            func_arg = args[func_index]
            
            if func_arg.startswith("(@PARENS"):
                # Extract the inner content of the parentheses
                inner_args = self._extract_arguments(func_arg)
                if inner_args:
                    # Parse the inner expression
                    function = self.parse_expression(inner_args[0])
                    function = f"\\left({function}\\right)"
                else:
                    function = ""
            else:
                function = self.parse_expression(func_arg)
        else:
            function = variable  # Default to the variable if no function is provided
        
        # Format with proper LaTeX
        return f"\\lim_{{{variable} \\to {approach_value}{direction}}} {function}"
            
    def _handle_derivative(self, expression):
        """Handle derivatives in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 3:
            return ""
        
        variable = self.parse_expression(args[0])
        
        # The second argument is the order of differentiation
        order = args[1]
        if order == "@PLACEHOLDER":
            order = "1"
        else:
            # Ensure order is treated as a number
            order = self.parse_expression(order)
        
        # The third argument is the function to differentiate
        function = args[2]
        if function.startswith("(@PARENS"):
            # Extract the content within the parentheses
            inner_args = self._extract_arguments(function)
            if inner_args:
                function = self.parse_expression(inner_args[0])
                # Wrap in parentheses for clarity
                function = f"\\left({function}\\right)"
            else:
                function = ""
        else:
            function = self.parse_expression(function)
        
        # Format the derivative based on the order
        if order == "1":
            return f"\\frac{{\\mathrm{{d}}}}{{\\mathrm{{d}}{variable}}} {function}"
        else:
            return f"\\frac{{\\mathrm{{d}}^{{{order}}}}}{{\\mathrm{{d}}{variable}^{{{order}}}}} {function}"
            
    def _handle_prime(self, expression):
        """Handle prime notation in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        function = self.parse_expression(args[0])
        count = int(args[1]) if len(args) > 1 else 1
        
        primes = "'" * count
        return f"{function}{primes}"
    
    def _handle_product(self, expression):
        """Handle product notation in MathCad."""
        args = self._extract_arguments(expression)
        
        # Check if we have enough arguments
        if len(args) < 3:
            return ""
        
        # The first arg might be an (@IS n 0) type expression
        if args[0].startswith("(@IS"):
            is_args = self._extract_arguments(args[0])
            if len(is_args) >= 2:
                var = self.parse_expression(is_args[0])
                start_val = self.parse_expression(is_args[1])
            else:
                var = "i"  # Default if no variable is specified
                start_val = "0"  # Default start value
        else:
            var = self.parse_expression(args[0])
            start_val = ""  # Will be filled in if available
            
        # Second argument is the upper limit
        upper = self.parse_expression(args[1])
        
        # If there's a third arg and no (@IS found, it could be the start value
        if len(args) > 2 and not args[0].startswith("(@IS"):
            start_val = self.parse_expression(args[1])
            upper = self.parse_expression(args[2])
            expr = self.parse_expression(args[3]) if len(args) > 3 else "1"
        else:
            # Otherwise, the expression is the next arg after the upper limit
            expr = self.parse_expression(args[2]) if len(args) > 2 else "1"
        
        # Format the product in LaTeX
        if start_val:
            return f"\\prod_{{{var}={start_val}}}^{{{upper}}} {expr}"
        else:
            return f"\\prod^{{{upper}}}_{{{var}}} {expr}"
    
    def _handle_sum(self, expression):
        """Handle summation notation in MathCad."""
        args = self._extract_arguments(expression)
        
        # Check if we have enough arguments
        if len(args) < 3:
            return "\\sum"  # Default empty sum
        
        # The first arg might be an (@IS n lower_limit) type expression
        if args[0].startswith("(@IS"):
            is_args = self._extract_arguments(args[0])
            if len(is_args) >= 2:
                var = self.parse_expression(is_args[0])
                start_val = self.parse_expression(is_args[1])
            else:
                var = "i"  # Default if no variable is specified
                start_val = "1"  # Default start value
        else:
            var = self.parse_expression(args[0])
            start_val = "1"  # Default start value
            
        # Second argument is the upper limit
        upper = self.parse_expression(args[1])
        
        # The expression to sum is the third argument
        # Important: Use parse_expression to handle nested special functions
        expr = self.parse_expression(args[2])
        
        # Format the sum in LaTeX
        return f"\\sum_{{{var}={start_val}}}^{{{upper}}} {expr}"
    
    def _handle_element_of(self, expression):
        """Handle element of notation in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        element = self.parse_expression(args[0])
        set_expr = self.parse_expression(args[1])
        
        return f"{element} \\in {set_expr}"
    
    def _handle_xor(self, expression):
        """Handle XOR operation in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} \\oplus {right}"
    
    def _handle_geq(self, expression):
        """Handle greater than or equal to in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} \\geq {right}"
    
    def _handle_leq(self, expression):
        """Handle less than or equal to in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} \\leq {right}"
    
    def _handle_and(self, expression):
        """Handle logical AND in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        result = ""
        for i, arg in enumerate(args):
            parsed_arg = self.parse_expression(arg)
            if i > 0:
                result += " \\land " + parsed_arg
            else:
                result += parsed_arg
                
        return result
    
    def _handle_or(self, expression):
        """Handle logical OR in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        result = ""
        for i, arg in enumerate(args):
            parsed_arg = self.parse_expression(arg)
            if i > 0:
                result += " \\lor " + parsed_arg
            else:
                result += parsed_arg
                
        return result
    
    def _handle_not(self, expression):
        """Handle logical NOT in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        operand = self.parse_expression(args[0])
        return f"\\neg {operand}"
    
    def _handle_neq(self, expression):
        """Handle not equal to in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} \\neq {right}"
    
    def _handle_negation(self, expression):
        """Handle negation expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        operand = self.parse_expression(args[0])
        
        # If operand is already complex, wrap in parentheses
        if " " in operand or "+" in operand or "-" in operand:
            return f"-\\left({operand}\\right)"
        else:
            return f"-{operand}"
    
    def _handle_is(self, expression):
        """Handle IS operator in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        return f"{left} = {right}"

    def _handle_apply(self, expression):
        """Handle function application in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        # The first argument is the function to apply (e.g., sin, cos, etc.)
        func_name = args[0].lower()
        
        # Map MathCad function names to LaTeX equivalents
        math_functions = {
            "sin": "\\sin",
            "cos": "\\cos",
            "tan": "\\tan",
            "cot": "\\cot",
            "sec": "\\sec",
            "csc": "\\csc",
            "arcsin": "\\arcsin",
            "arccos": "\\arccos",
            "arctan": "\\arctan",
            "sinh": "\\sinh",
            "cosh": "\\cosh",
            "tanh": "\\tanh",
            "ln": "\\ln",
            "log": "\\log",
            "log10": "\\log_{10}",
            "exp": "\\exp",
            "abs": "\\left|#\\right|",  # Placeholder for argument
            "max": "\\max",
            "min": "\\min"
        }
        
        # Get the LaTeX command for this function
        latex_func = math_functions.get(func_name, func_name)
        
        # Check if there's a second argument (the @ARGS expression)
        if len(args) > 1 and args[1].startswith("(@ARGS"):
            # Extract the arguments from the @ARGS expression
            args_expr = self._handle_args(args[1])
            
            # Special handling for abs function
            if func_name == "abs":
                return latex_func.replace("#", args_expr)
            
            # Return the function applied to its arguments
            return f"{latex_func}({args_expr})"
        
        return latex_func
    
    def _handle_args(self, expression):
        """Handle function arguments in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        # Parse each argument and join with commas
        parsed_args = [self.parse_expression(arg) for arg in args]
        return ", ".join(parsed_args)

    def _handle_matrix(self, expression):
        """Handle matrix expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 3:
            return "\\begin{pmatrix} \\end{pmatrix}"  # Empty matrix
        
        # First two arguments are rows and columns
        rows = int(args[0])
        cols = int(args[1])
        
        # Remaining arguments are the matrix elements
        elements = args[2:]
        
        if len(elements) != rows * cols:
            # If we don't have enough elements, pad with zeros
            elements.extend(["0"] * (rows * cols - len(elements)))
        
        # Create the LaTeX matrix
        latex_matrix = "\\begin{pmatrix}\n"
        for i in range(rows):
            row_elements = []
            for j in range(cols):
                idx = i * cols + j
                if idx < len(elements):
                    elem = self.parse_expression(elements[idx])
                    row_elements.append(elem)
                else:
                    row_elements.append("0")
            latex_matrix += " & ".join(row_elements)
            if i < rows - 1:
                latex_matrix += " \\\\\n"
        latex_matrix += "\n\\end{pmatrix}"
        
        return latex_matrix

    def _handle_cross(self, expression):
        """Handle cross product operations in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        # Parse both operands
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        # Return the formatted cross product
        return f"{left} \\times {right}"
        
    def _handle_dot(self, expression):
        """Handle dot product operations in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        # Parse both operands
        left = self.parse_expression(args[0])
        right = self.parse_expression(args[1])
        
        # Return the formatted dot product
        return f"{left} \\cdot {right}"

    def _handle_sym_eval(self, expression):
        """Handle symbolic evaluation expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        # Parse the expression to be evaluated
        left_expr = self.parse_expression(args[0])
        
        # Check if the next argument is @KW_STACK - if so, skip it
        right_index = 1
        if len(args) > 1 and args[1].startswith("(@KW_STACK"):
            right_index = 2
        
        # Parse the result (if available)
        right_expr = ""
        if len(args) > right_index:
            right_expr = self.parse_expression(args[right_index])
        
        # If there's a result, format with an rightarrow arrow, otherwise just return the expression
        if right_expr:
            return f"{left_expr} \\rightarrow {right_expr}"
        else:
            return left_expr

    def _handle_equals(self, expression):
        """Handle equals expressions in MathCad."""
        # Remove the '=' prefix from the expression, but keep the opening parenthesis
        content = expression[2:-1].strip()
        
        # Split content into left and right sides by finding the first space at top level
        split_position = -1
        paren_level = 0
        
        for i, char in enumerate(content):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            elif char == ' ' and paren_level == 0:
                split_position = i
                break
        
        if split_position != -1:
            left_expr = content[:split_position].strip()
            right_expr = content[split_position+1:].strip()
            
            # Parse each part
            left = self.parse_expression(left_expr)
            right = self.parse_expression(right_expr)
            
            return f"{left} = {right}"
        
        # If we can't find a good split point, try another approach
        args = content.split(None, 1)  # Split on first whitespace
        if len(args) >= 2:
            left = self.parse_expression(args[0])
            right = self.parse_expression(args[1])
            return f"{left} = {right}"
        
        # If all else fails, just return the original expression
        return expression

    def _handle_subscript(self, expression):
        """Handle subscript notation in MathCad."""
        args = self._extract_arguments(expression)
        
        if not args:
            return ""
        
        subscript = self.parse_expression(args[0])
        return f"{{{subscript}}}"

    def _handle_identifier_with_subscript(self, expression):
        """Handle identifier with subscript notation in MathCad."""
        # Extract the identifier name (normally comes after @ID)
        id_match = re.search(r'\(@ID\s+([^\s\)]+)', expression)
        if not id_match:
            return expression
            
        # Get the variable name
        identifier = id_match.group(1)
        
        # Find the subscript part
        sub_start = expression.find('(@SUB')
        if sub_start == -1:
            return identifier
            
        # Extract the subscript arguments
        sub_expr = expression[sub_start:]
        closing_paren_idx = self._find_matching_parenthesis(sub_expr, 0)
        
        if closing_paren_idx != -1:
            subscript_expr = sub_expr[:closing_paren_idx + 1]
            subscript_args = self._extract_arguments(subscript_expr)
            
            if subscript_args:
                subscript = self.parse_expression(subscript_args[0])
                return f"{identifier}_{{{subscript}}}"
        
        return identifier
        
    def _find_matching_parenthesis(self, text, start_idx):
        """Find the position of the matching closing parenthesis."""
        if start_idx >= len(text) or text[start_idx] != '(':
            return -1
            
        stack = 1
        for i in range(start_idx + 1, len(text)):
            if text[i] == '(':
                stack += 1
            elif text[i] == ')':
                stack -= 1
                if stack == 0:
                    return i
        return -1

    def _handle_equation(self, expression):
        """Handle user-created equation expressions in MathCad."""
        args = self._extract_arguments(expression)
        
        if len(args) < 2:
            return ""
        
        left = self.parse_expression(args[0])
        
        # Check if the right-hand side contains an arithmetic operation
        right_expr = args[1]
        if right_expr.startswith("(+"):
            # Handle addition - parse arguments more carefully
            # Remove the operator and outer parentheses
            content = right_expr[2:-1].strip()
            # Split by spaces at the top level
            addition_args = []
            current_arg = ""
            paren_count = 0
            
            for char in content:
                if char == "(":
                    current_arg += char
                    paren_count += 1
                elif char == ")":
                    current_arg += char
                    paren_count -= 1
                elif char == " " and paren_count == 0 and current_arg:
                    addition_args.append(current_arg.strip())
                    current_arg = ""
                else:
                    current_arg += char
                    
            if current_arg:
                addition_args.append(current_arg.strip())
                
            # Parse each argument and join with plus signs
            if addition_args:
                parsed_args = [self.parse_expression(arg) for arg in addition_args]
                right = " + ".join(parsed_args)
            else:
                right = self.parse_expression(right_expr)
        elif right_expr.startswith("(-"):
            # Handle subtraction
            subtraction_args = self._extract_arguments_from_op(right_expr[1:])
            if len(subtraction_args) == 2:
                right = f"{self.parse_expression(subtraction_args[0])} - {self.parse_expression(subtraction_args[1])}"
            else:
                right = self.parse_expression(right_expr)
        elif right_expr.startswith("(*"):
            # Handle multiplication
            multiplication_args = self._extract_arguments_from_op(right_expr[1:])
            parsed_args = [self.parse_expression(arg) for arg in multiplication_args]
            right = " \\cdot ".join(parsed_args)
        elif right_expr.startswith("(/"):
            # Handle division
            division_args = self._extract_arguments_from_op(right_expr[1:])
            if len(division_args) == 2:
                right = f"\\frac{{{self.parse_expression(division_args[0])}}}{{{self.parse_expression(division_args[1])}}}"
            else:
                right = self.parse_expression(right_expr)
        else:
            # If not an arithmetic operation, parse normally
            right = self.parse_expression(right_expr)
        
        return f"{left} = {right}"
        
    def _extract_arguments_from_op(self, expression):
        """
        Extract arguments from a MathCad operation expression like "+2 1".
        
        Args:
            expression (str): The MathCad operation expression (without the leading operator)
            
        Returns:
            list: The arguments of the operation
        """
        if not expression or len(expression) < 2:
            return []
            
        # Remove any outer parentheses and trim
        content = expression.strip()
        if content.startswith('(') and content.endswith(')'):
            content = content[1:-1].strip()
        
        args = []
        current_arg = ""
        paren_count = 0
        
        for char in content:
            if char == "(" and current_arg.strip() == "":
                paren_count += 1
                current_arg += char
            elif char == "(":
                current_arg += char
                paren_count += 1
            elif char == ")":
                current_arg += char
                paren_count -= 1
            elif char == " " and paren_count == 0 and current_arg.strip():
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
                
        if current_arg.strip():
            args.append(current_arg.strip())
            
        return args

    def translate(self, mathcad_expr):
        """
        Translate a MathCad expression to LaTeX.
        
        Args:
            mathcad_expr (str): The MathCad expression to translate
            
        Returns:
            str: The equivalent LaTeX expression
        """
        latex_expr = self.parse_expression(mathcad_expr)
        
        # For long expressions, we'll let the equation environment handle it
        # rather than trying to use a multline environment which causes issues
        return latex_expr


# Function to simplify conversion, used by the GUI
def convert_mathcad_to_latex(mathcad_expr):
    """
    Convert a MathCad expression to LaTeX format.
    
    Args:
        mathcad_expr (str): The MathCad expression to convert
        
    Returns:
        str: The equivalent LaTeX expression
    """
    translator = MathcadToLatexTranslator()
    latex_expr = translator.translate(mathcad_expr)
    return refine_latex(latex_expr)


def refine_latex(latex_expression):
    """
    Refine a LaTeX expression for better typesetting and readability.
    This function applies various improvements to already converted LaTeX expressions.
    
    Args:
        latex_expression (str): The LaTeX expression to refine
        
    Returns:
        str: The refined LaTeX expression
    """
    if not latex_expression or not isinstance(latex_expression, str):
        return latex_expression
    
    # Initialize refinement flag - will be set to True if any changes are made
    refinements_made = False
    refined_expression = latex_expression
    
    # 1. Improve fractions - convert simple divisions to proper \frac commands
    pattern = r'(\w+|\([^)]+\)) *\/ *(\w+|\([^)]+\))'
    if re.search(pattern, refined_expression):
        def replace_with_frac(match):
            nonlocal refinements_made
            refinements_made = True
            numerator = match.group(1)
            denominator = match.group(2)
            return f"\\frac{{{numerator}}}{{{denominator}}}"
        
        refined_expression = re.sub(pattern, replace_with_frac, refined_expression)
    
    # 2. Improve spacing around operators
    operators = ['+', '-', '=', r'\times', r'\cdot', '<', '>', r'\leq', r'\geq', r'\neq']
    for op in operators:
        # Escape any regex special characters in the operator
        escaped_op = op
        if op in ['+', '-', '*', '.', '(', ')', '[', ']', '{', '}', '\\']:
            escaped_op = '\\' + op
            
        # Add proper spacing around operators but not within commands
        pattern = f'([^\\\\]){escaped_op}([^\\s])'
        if re.search(pattern, refined_expression):
            refinements_made = True
            refined_expression = re.sub(pattern, f'\\1 {op} \\2', refined_expression)
    
    # 3. Improve superscripts and subscripts with proper command
    # Convert x^2 to x^{2} for better clarity when expression is complex
    superscript_pattern = r'(\w+)\^(\w)'
    if re.search(superscript_pattern, refined_expression):
        def replace_with_proper_superscript(match):
            nonlocal refinements_made
            refinements_made = True
            base = match.group(1)
            exponent = match.group(2)
            return f"{base}^{{{exponent}}}"
        
        refined_expression = re.sub(superscript_pattern, replace_with_proper_superscript, refined_expression)
    
    # 4. Add \left and \right to large parentheses containing fractions
    parentheses_pattern = r'\(([^()]*\\frac{[^{}]*}{[^{}]*}[^()]*)\)'
    if re.search(parentheses_pattern, refined_expression):
        def replace_with_left_right(match):
            nonlocal refinements_made
            refinements_made = True
            content = match.group(1)
            return f"\\left({content}\\right)"
        
        refined_expression = re.sub(parentheses_pattern, replace_with_left_right, refined_expression)
    
    # 5. Enhance mathematical functions with proper formatting
    math_funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'arcsin', 'arccos', 'arctan', 
                 'sinh', 'cosh', 'tanh', 'log', 'ln', 'exp', 'lim', 'max', 'min']
    
    for func in math_funcs:
        # Look for function names without \ prefix
        pattern = r'(?<![\\a-zA-Z])' + func + r'(?![a-zA-Z])'
        if re.search(pattern, refined_expression):
            refinements_made = True
            refined_expression = re.sub(pattern, f'\\\\{func}', refined_expression)
    
    # 6. Improve display of integrals, sums, and products
    # Add display style to make them larger in inline mode
    for cmd in [r'\int', r'\sum', r'\prod']:
        pattern = f'{cmd}((_{{[^}}]*}}\^{{[^}}]*}}))'
        if re.search(pattern, refined_expression):
            refinements_made = True
            refined_expression = re.sub(pattern, f'\\\\displaystyle{cmd}\\1', refined_expression)
    
    # 7. Add \mathrm to units
    units_pattern = r'([0-9]+) *([a-zA-Z]+)'
    if re.search(units_pattern, refined_expression):
        def process_units(match):
            nonlocal refinements_made
            number = match.group(1)
            unit = match.group(2)
            
            # Skip if unit is likely a variable name or already processed
            if unit in ['x', 'y', 'z', 'i', 'j', 'k', 't', 'n', 'a', 'b', 'c'] or '\\' in unit:
                return match.group(0)
            
            refinements_made = True
            return f"{number}\\,\\mathrm{{{unit}}}"
            
        refined_expression = re.sub(units_pattern, process_units, refined_expression)
    
    # 8. Add comment if no refinements were made
    if not refinements_made:
        refined_expression += "  % No further refinements available"
    
    return refined_expression

# Function to convert SVG for use in the GUI preview
def latex_to_svg(latex_content, output_file, scale=1.0):
    """
    Convert LaTeX content to SVG format.
    
    Args:
        latex_content (str): The LaTeX math expression
        output_file (str or file-like): The output file path or file-like object
        scale (float): Scale factor for the output
    
    Returns:
        None
    """
    # Check for matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_svg import FigureCanvasSVG
    
    # Create a figure with transparent background
    fig = plt.figure(figsize=(8, 4))
    fig.patch.set_alpha(0.0)
    
    # Add text with the LaTeX formula
    scaled_fontsize = 14 * scale
    plt.text(0.5, 0.5, f"${latex_content}$", 
             fontsize=scaled_fontsize, ha='center', va='center')
    
    # Remove axes
    plt.axis('off')
    
    # Save as SVG
    if hasattr(output_file, 'write'):
        # It's a file-like object
        plt.savefig(output_file, format='svg', bbox_inches='tight', transparent=True)
    else:
        # It's a file path
        plt.savefig(output_file, format='svg', bbox_inches='tight', transparent=True)
    
    plt.close(fig)

# If run directly
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use command line argument as input
        mathcad_expr = sys.argv[1]
        latex_result = convert_mathcad_to_latex(mathcad_expr)
        print(latex_result)
    else:
        # Test cases with actual MathCad expressions
        test_expressions = [
            "(@INTEGRAL 0 1 x^2 x)",
            "(@FRACTION α β)",
            "(@PARENS (*x y))",
            "(@DERIV x 2 (@PARENS (*x y)))",
            "(@SUM (@IS i 1) 10 i^2)"
        ]
        for expr in test_expressions:
            latex = convert_mathcad_to_latex(expr)
            print(f"MathCad: {expr}")
            print(f"LaTeX: {latex}")
            print("-" * 20)